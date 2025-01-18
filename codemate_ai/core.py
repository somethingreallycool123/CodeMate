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
import ast


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
    """Display the current context tree in a formatted form."""
    from IPython.display import display, Code
    
    # Ensure we have a context_tree in scope
    global context_tree
    
    if not context_tree:
        print("No context available. Use %analyze_code first.")
        return
    
    summary_lines = []
    
    # 1) Summarize functions
    functions_dict = context_tree.get("functions", {})
    if functions_dict:
        summary_lines.append("=== Functions ===")
        for func_name, func_info in functions_dict.items():
            summary_lines.append(f"Function: {func_name}")
            
            # Parameters
            params = func_info.get("params", [])
            if params:
                summary_lines.append(f"  Params: {', '.join(params)}")
            
            # Docstring
            docstring = func_info.get("docstring", "")
            if docstring:
                summary_lines.append(f"  Docstring: {docstring}")
            
            # Variables
            var_info = func_info.get("variables", {})
            if var_info:
                summary_lines.append("  Variables:")
                for var_name, usage_list in var_info.items():
                    usage_str = ", ".join(usage_list)
                    summary_lines.append(f"    {var_name} -> {usage_str}")
            
            summary_lines.append("")  # Blank line
    
    # 2) Summarize classes
    classes_dict = context_tree.get("classes", {})
    if classes_dict:
        summary_lines.append("=== Classes ===")
        for class_name, class_info in classes_dict.items():
            summary_lines.append(f"Class: {class_name}")
            
            # Class docstring
            class_doc = class_info.get("docstring", "")
            if class_doc:
                summary_lines.append(f"  Docstring: {class_doc}")
            
            # Methods
            methods_dict = class_info.get("methods", {})
            for method_name, method_info in methods_dict.items():
                summary_lines.append(f"  Method: {method_name}")
                
                # Method params
                method_params = method_info.get("params", [])
                if method_params:
                    summary_lines.append(f"    Params: {', '.join(method_params)}")
                
                # Method docstring
                method_doc = method_info.get("docstring", "")
                if method_doc:
                    summary_lines.append(f"    Docstring: {method_doc}")
                
                # Variables in the method
                method_vars = method_info.get("variables", {})
                if method_vars:
                    summary_lines.append("    Variables:")
                    for var_name, usage_list in method_vars.items():
                        usage_str = ", ".join(usage_list)
                        summary_lines.append(f"      {var_name} -> {usage_str}")
                
                summary_lines.append("")  # Blank line
    
    # 3) If no functions/classes found, look for a 'no_definitions' entry
    if "no_definitions" in context_tree:
        no_def_message = context_tree["no_definitions"].get("message", "")
        summary_lines.append("=== No Definitions ===")
        summary_lines.append(no_def_message)
    
    # Join everything
    context_summary = "\n".join(summary_lines).strip()
    
    if not context_summary:
        context_summary = "No content to display."
    
    print("Context Summary:")
    display(Code(context_summary, language='python'))








def create_parent_map(node: ast.AST) -> Dict[ast.AST, ast.AST]:
    """
    Recursively build a dictionary mapping each node to its direct parent node.
    """
    parent_map = {}
    for child in ast.iter_child_nodes(node):
        parent_map[child] = node
        parent_map.update(create_parent_map(child))
    return parent_map

def analyze_code(code: str) -> Dict[str, Any]:
    """
    Parse code to extract:
      - Top-level functions: name, params, docstring, variables + usage context
      - Top-level classes: docstring, methods (same details)
      - If no functions or classes, store 'no_definitions' placeholder.

    For each variable, we gather:
      - "read" / "write" / "delete" from child.ctx (Load, Store, Del)
      - All relevant usage labels from ANY parent node in the chain,
        e.g. "loop_usage", "conditional_usage", "arithmetic", "function_call", etc.
    """
    global context
    context_tree = {
        "functions": {},
        "classes": {}
    }
    found_any_definitions = False

    # Extend usage_map to include loops and conditionals (plus existing ops).
    usage_map = {
        ast.BinOp: "arithmetic",
        ast.Call: "function_call",
        ast.Compare: "comparison",
        ast.Subscript: "index",
        ast.Return: "return_value",
        ast.For: "loop_usage",
        ast.While: "loop_usage",
        ast.If: "conditional_usage",
        ast.IfExp: "conditional_usage",
    }

    try:
        tree = ast.parse(code)

        # Helper function to gather usage labels from all parents
        def gather_parent_usage_labels(node_name: ast.Name, parent_dict: Dict[ast.AST, ast.AST]) -> set:
            """
            Given an ast.Name node and a parent map, climb up the chain
            and collect all relevant usage labels (loop_usage, conditional_usage, etc.).
            """
            labels = set()
            current = node_name

            # Walk up until we have no parent or we've hit the root
            while current in parent_dict:
                current = parent_dict[current]
                label = usage_map.get(type(current), None)
                if label:
                    labels.add(label)

            return labels

        # Iterate over top-level nodes (functions, classes, etc.)
        for node in ast.iter_child_nodes(tree):
            # 1) Top-level Functions
            if isinstance(node, ast.FunctionDef):
                found_any_definitions = True

                func_name = node.name
                params = [arg.arg for arg in node.args.args]
                docstring = ast.get_docstring(node)

                # Create a parent map inside this function
                func_parents = create_parent_map(node)
                var_usage = {}

                # Walk the function AST
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        var_name = child.id
                        if var_name not in var_usage:
                            var_usage[var_name] = set()

                        # (1) Read/Write/Delete
                        usage_type = type(child.ctx).__name__  # "Load", "Store", or "Del"
                        if usage_type == "Store":
                            var_usage[var_name].add("write")
                        elif usage_type == "Load":
                            var_usage[var_name].add("read")
                        elif usage_type == "Del":
                            var_usage[var_name].add("delete")

                        # (2) Gather *all* parent usage labels
                        parent_labels = gather_parent_usage_labels(child, func_parents)
                        var_usage[var_name].update(parent_labels)

                # Convert sets to lists for JSON-friendly structure
                var_usage = {k: list(v) for k, v in var_usage.items()}

                context_tree["functions"][func_name] = {
                    "params": params,
                    "docstring": docstring,
                    "variables": var_usage
                }

            # 2) Top-level Classes
            elif isinstance(node, ast.ClassDef):
                found_any_definitions = True

                class_name = node.name
                class_docstring = ast.get_docstring(node)
                methods = {}

                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef):
                        method_name = subnode.name
                        method_params = [arg.arg for arg in subnode.args.args]
                        method_doc = ast.get_docstring(subnode)

                        # Create a parent map for this method
                        method_parents = create_parent_map(subnode)
                        method_vars = {}

                        # Walk the method AST
                        for grandchild in ast.walk(subnode):
                            if isinstance(grandchild, ast.Name):
                                var_name = grandchild.id
                                if var_name not in method_vars:
                                    method_vars[var_name] = set()

                                # (1) Read/Write/Delete
                                usage_type = type(grandchild.ctx).__name__
                                if usage_type == "Store":
                                    method_vars[var_name].add("write")
                                elif usage_type == "Load":
                                    method_vars[var_name].add("read")
                                elif usage_type == "Del":
                                    method_vars[var_name].add("delete")

                                # (2) Gather *all* parent usage labels
                                parent_labels = gather_parent_usage_labels(grandchild, method_parents)
                                method_vars[var_name].update(parent_labels)

                        method_vars = {k: list(v) for k, v in method_vars.items()}
                        methods[method_name] = {
                            "params": method_params,
                            "docstring": method_doc,
                            "variables": method_vars
                        }

                context_tree["classes"][class_name] = {
                    "docstring": class_docstring,
                    "methods": methods
                }

        # 3) If code has no functions/classes, store a placeholder
        if not found_any_definitions:
            context_tree["no_definitions"] = {
                "message": "No functions or classes found in the code."
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


