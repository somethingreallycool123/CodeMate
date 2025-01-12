from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.display import display, Code
from . import providers
from . import core
import sys
from io import StringIO
import traceback
from .providers import config, LLMProvider,call_openai,call_gemini,call_anthropic,call_local_transformers,call_huggingface_hub
from .core import clean_code_output

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

        model_path = None
        if len(args) > 1:
            model_path = args[1]
            providers.config.api_keys[provider_name]["model"] = model_path
        if provider_name == "transformers_local":
            if model_path:
                if providers.load_model(model_path):
                    return f"Local model '{model_path}' loaded successfully"
                return f"Failed to load model '{model_path}'"
        elif provider_name == "transformers_download":
            if model_path:
                try:
                    load_8bit = "--8bit" in args
                    device = next((arg.split("=")[1] for arg in args if arg.startswith("--device=")), "auto")

                    model_path = providers.download_model(model_path)
                    if providers.load_model(model_path, device=device, load_in_8bit=load_8bit):
                        return f"Model '{model_path}' downloaded and loaded successfully"
                    return f"Failed to load model '{model_path}'"
                except Exception as e:
                    return f"Error: {e}"
            else:
                return "Model path is required for transformers_download provider."
        else:
            if model_path:
                providers.config.model_name = model_path
            else:
                return "No model path provided."

        if model_path is not None:
            return f"Provider set to {provider_name}. Model set to {model_path}"
        else:
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
            context_summary = "\n".join([
                f"Function: {func}\nVariables: {', '.join(details['variables'])}\nBody:\n{details['body']}"
                for func, details in context_tree.items()
            ])
            
            return "Code analysis complete"
        except Exception as e:
            return f"Error analyzing code: {e}"


    @line_magic
    def generate_code(self, line):
        """Magic command to generate code."""
        if not config.provider:
            return "Please set up a provider first using %set_llm_provider"

        function_name = line.strip()
        if not context_tree:
            return "Context tree not built. Use %analyze_code '<notebook_path>' to build it."

        prompt = f"Generate Python code for a function named '{function_name}' considering the context provided."

        if config.provider == LLMProvider.TRANSFORMERS_LOCAL:
            return call_local_transformers(prompt)
        elif config.provider == LLMProvider.TRANSFORMERS_HUB:
            return call_huggingface_hub(prompt)
        elif config.provider == LLMProvider.OPENAI:
            return call_openai(prompt)
        elif config.provider == LLMProvider.ANTHROPIC:
            return call_anthropic(prompt)
        elif config.provider == LLMProvider.GEMINI:
            return call_gemini(prompt)
        elif config.provider == LLMProvider.TRANSFORMERS_DOWNLOAD:
            return call_local_transformers(prompt)  
        else:
            return "Provider not implemented" 


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
