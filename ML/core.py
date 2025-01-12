import ast
import os
import json
from typing import Dict, Any
from IPython import get_ipython
import nbformat
from nbformat import NotebookNode

def analyze_code(code: str) -> Dict[str, Any]:
    """Analyze code to build context tree."""
    context = {}
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                context[node.name] = {
                    'variables': [arg.arg for arg in node.args.args],
                    'body': ast.unparse(node)
                }
    except Exception as e:
        print(f"Error analyzing code: {e}")
    return context

def get_notebook_path():
    """Get the path of the current Jupyter notebook."""
    try:
        connection_file = os.path.basename(get_ipython().config['IPKernelApp']['connection_file'])
        kernel_id = connection_file.split('-', 1)[1].split('.')[0]

        for server in list(list_running_servers()):
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
            except Exception:
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