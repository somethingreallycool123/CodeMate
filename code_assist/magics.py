from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.display import display, Code
from . import providers
from . import core
import sys
from io import StringIO
import traceback

@magics_class
class CodeAssistMagics(Magics):
    """Magic commands for CodeAssist."""
    
    @line_magic
    def set_api_key(self, line):
        """Set API key for a provider."""
        args = line.split()
        if len(args) < 2:
            return "Usage: %set_api_key <provider> <key> [model]"
        
        provider, key = args[0], args[1]
        model = args[2] if len(args) > 2 else None
        
        if provider not in providers.config.api_keys:
            return f"Invalid provider. Available: {', '.join(providers.config.api_keys.keys())}"
        
        providers.config.api_keys[provider]["api_key"] = key
        if model:
            providers.config.api_keys[provider]["model"] = model
            
        return f"API key for {provider} set successfully"

    @line_magic
    def set_llm_provider(self, line):
        """Set the LLM provider and optionally load a model."""
        args = line.split()
        if not args:
            return "Usage: %set_llm_provider <provider> [model_path] [options]"
            
        provider_name = args[0].lower()
        if provider_name not in [p.value for p in providers.LLMProvider]:
            return f"Invalid provider. Choose from: {', '.join(p.value for p in providers.LLMProvider)}"

        providers.config.provider = providers.LLMProvider(provider_name)
        
        if len(args) > 1:
            model_path = args[1]
            if provider_name == "transformers_local":
                if providers.load_model(model_path):
                    return f"Local model loaded successfully"
                return "Failed to load model"
            elif provider_name == "transformers_download":
                try:
                    load_8bit = "--8bit" in args
                    device = next((arg.split("=")[1] for arg in args if arg.startswith("--device=")), "auto")
                    
                    model_path = providers.download_model(model_path)
                    if providers.load_model(model_path, device=device, load_in_8bit=load_8bit):
                        return f"Model downloaded and loaded successfully"
                    return "Failed to load model"
                except Exception as e:
                    return f"Error: {e}"
            else:
                providers.config.model_name = model_path

        return f"Provider set to {provider_name}"

    @line_magic
    def analyze_code(self, line):
        """Analyze code in the current notebook."""
        notebook_path = line.strip() if line else core.get_notebook_path()
        if not notebook_path:
            return "Could not determine notebook path"
            
        try:
            code = core.extract_code_from_notebook(notebook_path)
            global context_tree
            context_tree = core.analyze_code(code)
            return "Code analysis complete"
        except Exception as e:
            return f"Error analyzing code: {e}"

    @cell_magic
    def debug_cell(self, line, cell):
        """Debug a cell with AI assistance."""
        if not providers.config.provider:
            return "Please set up a provider first using %set_llm_provider"
        
        # Capture output and errors
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        try:
            exec(cell, self.shell.user_ns)
            error_msg = None
        except Exception:
            error_msg = traceback.format_exc()
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        
        if error_msg:
            print("\nAnalyzing error and suggesting solutions...")
            prompt = f"""Given this Python code:

{cell}

The code produced this error:
{error_msg}

Please analyze the error and suggest a solution. Focus on:
1. What specifically caused the error
2. How to fix it
3. Any best practices or alternative approaches
"""
            
            provider = providers.config.provider
            if provider == providers.LLMProvider.OPENAI:
                suggestion = providers.call_openai(prompt)
            elif provider == providers.LLMProvider.ANTHROPIC:
                suggestion = providers.call_anthropic(prompt)
            elif provider == providers.LLMProvider.GEMINI:
                suggestion = providers.call_gemini(prompt)
            elif provider in (providers.LLMProvider.TRANSFORMERS_LOCAL, providers.LLMProvider.TRANSFORMERS_DOWNLOAD):
                suggestion = providers.generate_with_model(prompt)
            else:
                suggestion = "Provider not implemented"
            
            print("\nAI Suggestion:")
            print(suggestion)
        else:
            output = stdout_capture.getvalue()
            if output:
                print("Output:", output)
