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


