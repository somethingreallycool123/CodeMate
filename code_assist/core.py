import ast
import os
import json
import requests  # Import the missing library
from typing import Dict, Any
from IPython import get_ipython
import nbformat
from nbformat import NotebookNode
from jupyter_server.serverapp import list_running_servers
import astor
from IPython.display import HTML, display

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter



current_style = 'rrt'
current_persona = "normal"

def set_style(style):
    """
    Sets the global Pygments style.

    Parameters:
    - style (str): The Pygments style to use.
    """
    global current_style
    try:
        # Test if the style is valid by creating a formatter
        HtmlFormatter(style=style)
        current_style = style
        print(f"Pygments style set to: {style}")
    except Exception:
        raise ValueError(f"Style '{style}' is not valid. Check available styles at https://pygments.org/styles/")

def display_highlighted_code(code, language='python', style='rrt'):
    """
    Displays syntax-highlighted code in a Jupyter Notebook using Pygments.

    Parameters:
    - code (str): The code to display.
    - language (str): The programming language for syntax highlighting. Default is 'python'.
    - style (str): The Pygments style for highlighting. Default is 'rrt'.

    Supported styles: https://pygments.org/styles/
    """
    # Remove triple backticks and language specification from the code
    lines = code.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]  # Remove the first line if it's ```
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]  # Remove the last line if it's ```
    clean_code = "\n".join(lines)

    # Select the appropriate lexer based on the language
    if language.lower() == 'python':
        lexer = PythonLexer()
    else:
        raise ValueError(f"Language '{language}' is not supported yet.")
    
    # Format the code with the chosen style
    formatter = HtmlFormatter(style=current_style, noclasses=True)
    highlighted_code = highlight(clean_code, lexer, formatter)
    
    # Display the highlighted code
    display(HTML(highlighted_code))


def set_persona(mode):
    """
    Sets the global mode for LLM requests.

    Parameters:
    - mode (str): The mode to set (e.g., 'friendly', 'detailed', 'concise', 'normal').
    """
    global current_persona
    valid_modes = ['beginnerfriendly', 'detailed', 'concise', 'normal','technical', 'expert', 'creative']
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode: '{mode}'. Valid modes are: {', '.join(valid_modes)}")
    mode_def ={
    "beginnerfriendly": (
        "Explain the concept in the simplest terms possible  "
        "Use relatable analogies, step-by-step explanations, and avoid technical jargon. you may Include examples to help clarify. All explaination must be wrapped in code only using ''' "
    ),
    "detailed": (
        "Provide an in-depth explanation of the concept, including all relevant details, context, and examples. "
        "Cover edge cases, best practices, and common pitfalls. Assume the reader wants a thorough understanding of the topic. All of this should ideally be wrapped in the code onyl and use the ''' to elaborate on topics inside the code only"
    ),
    "concise": (
        "Focus only on the code and if very necessary Explain the concept in as few words as possible while still being clear and accurate. "
        "Focus only on the key points and avoid unnecessary details."
    ),
    "normal": ("give only code and any minimal stuff put in code comments"
        
    ),
    "technical": (
        "Explain the concept with a focus on the technical aspects. Use precise terminology and assume the reader "
        "has an intermediate to advanced understanding of coding and related technologies. Include code snippets and formal definitions where applicable.All of this should ideally be wrapped in the code onyl and using  the ''' "
    ),
    "expert": (
        "Deliver an advanced explanation of the concept with references to cutting-edge techniques, research, or standards. "
        "Assume the reader is highly experienced in coding and wants a deep dive into the nuances, optimizations, and trade-offs. All of this should ideally be wrapped in the code onyl and using  the ''' "
    ),
    "creative": (
        "Explain the concept in an engaging, imaginative way. Use  metaphors, or analogies to make the explanation memorable and fun. "
        "Include examples that showcase creativity and out-of-the-box thinking. any explainations shoudl be through code comments or in rare cases through ''' "
    )
}
    current_persona = mode_def[mode]
    print(f"Persona set to: {mode}")

def get_persona():
    """
    Gets the current mode.

    Returns:
    - str: The current mode.
    """
    return current_persona






def styled_code(code, language='python'):
    style = """
    <style>
        .custom-code {
            font-family: Consolas, "Courier New", monospace;
            font-size: 14px;
            background-color: #f5f5f5;
            color: #333;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
    """
    html = f"""
    {style}
    <div class="custom-code">
    <pre><code class="{language}">{code}</code></pre>
    </div>
    """
    
    display(HTML(html))

def clean_code_output(text: str) -> str:
    """Clean and format code output."""
    from IPython.display import display, Code
    
    # Remove markdown and quotes
    text = text.replace('```python\n', '').replace('\n```', '').strip("'").strip('"')
    
    # Display formatted code
    display(Code(text, language='python'))

def print_context_summary():
    """Display the current context tree in formatted form."""
    from IPython.display import display, Code
    
    if not context_tree:
        print("No context available. Use %analyze_code first.")
        return
        
    context_summary = "\n".join([
        f"Function: {func}\nVariables: {', '.join(details['variables'])}\nBody:\n{details['body']}"
        for func, details in context_tree.items()
    ])
    
    print("Context Summary:")
    display(Code(context_summary, language='python'))

def analyze_code(code: str) -> Dict[str, Any]:
    """Parse code and extract a context tree."""
    
    context_tree = {}
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                variables = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        variables.add(child.id)
                context_tree[func_name] = {
                    "variables": list(variables),
                    "body": astor.to_source(node)
                }
    except Exception as e:
        print(f"Error parsing code: {e}")
    return context_tree


def get_notebook_path() -> str:
    """Get the path of the current Jupyter notebook."""
    try:
        connection_file = os.path.basename(get_ipython().config['IPKernelApp']['connection_file'])
        kernel_id = connection_file.split('-', 1)[1].split('.')[0]

        for server in list_running_servers():
            try:
                response = requests.get(
                    f"{server['url']}api/sessions",
                    params={"token": server.get("token", "")},
                    verify=False,
                )
                response.raise_for_status()
                sessions = response.json()

                for session in sessions:
                    if session["kernel"]["id"] == kernel_id:
                        return os.path.join(server["root_dir"], session["notebook"]["path"])
            except Exception as e:
                print(f"Error fetching sessions from server: {e}")
                continue

        raise RuntimeError("Could not find the notebook path.")
    except Exception as e:
        print(f"Error getting notebook path: {e}")
        return None


def extract_code_from_notebook(notebook_path: str) -> str:
    """Extract code cells from a Jupyter notebook."""
    try:
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        code_cells = []
        for cell in nb.cells:
            if cell.cell_type == 'code':
                # Skip magic commands and shell commands
                code = '\n'.join(line for line in cell.source.split('\n')
                                 if not line.strip().startswith(('!', '%', 'pip')))
                if code.strip():
                    code_cells.append(code)

        return '\n\n'.join(code_cells)
    except Exception as e:
        print(f"Error extracting code: {e}")
        return ""


