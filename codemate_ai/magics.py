from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.display import display, Code, Markdown,HTML,clear_output
import time
from codemate_ai import providers
from codemate_ai import core
import sys
import itertools
from io import StringIO
import traceback
from codemate_ai.providers import config, LLMProvider,call_openai,call_gemini,call_anthropic,call_local_transformers,call_huggingface_hub
from codemate_ai.core import clean_code_output,set_style,set_persona,get_persona,print_context_summary,display_highlighted_code
import inspect
import traceback
import cProfile
import pstats
from io import StringIO


@magics_class
class CodeAssistMagics(Magics):
    
    """Magic commands for CodeAssist."""

    @line_magic
    def set_code_theme(self,style):
        """
        Magic function to set the Pygments style dynamically.

        Usage:
        %set_code_theme <style_name>
        """
        try:
            if len(style) == 0:
                print("Check available styles at https://pygments.org/styles/")

            else:
                set_style(style)

            
        except ValueError as e:
            print(e)

    @line_magic
    def set_persona(self,persona):
        """
        Magic function to set the LLM persona dynamically.

        Usage:
        %set_persona <persona>
        
        Example:
        %set_persona friendly
        """
        try:
            set_persona(persona)
        except ValueError as e:
            print(e)        
    
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
            return f"Provider set to {provider_name}. Model set to {model_path} "
        else:
            return f"Provider set to {provider_name}"



    @line_magic
    def analyze_code(self,line):
        """
        Analyze code in the current notebook using core.analyze_code
        and store a global `context_tree`. 
        Returns a short textual summary.
        """
        notebook_path = line.strip() if line else core.get_notebook_path()
        if not notebook_path:
            return "Could not determine notebook path"

        try:
            code = core.extract_code_from_notebook(notebook_path)

            global context_tree
            context_tree = core.analyze_code(code)

            # Build a textual summary from the new structure
            summary_lines = []

            # 1) Check if we have "functions"
            functions_dict = context_tree.get("functions", {})
            for func_name, func_info in functions_dict.items():
                summary_lines.append(f"Function: {func_name}")
                if func_info.get("params"):
                    summary_lines.append(f"  Params: {', '.join(func_info['params'])}")
                if func_info.get("docstring"):
                    summary_lines.append(f"  Docstring: {func_info['docstring']}")
                
                # Variables are typically a dict { var_name: [usage_labels] }
                if "variables" in func_info:
                    summary_lines.append("  Variables:")
                    for var_name, usage_list in func_info["variables"].items():
                        usage_str = ", ".join(usage_list)
                        summary_lines.append(f"    {var_name} -> {usage_str}")

                summary_lines.append("")  # blank line for spacing

            # 2) Check if we have "classes"
            classes_dict = context_tree.get("classes", {})
            for class_name, class_info in classes_dict.items():
                summary_lines.append(f"Class: {class_name}")
                if class_info.get("docstring"):
                    summary_lines.append(f"  Docstring: {class_info['docstring']}")

                # Each class might have multiple methods
                methods_dict = class_info.get("methods", {})
                for method_name, method_info in methods_dict.items():
                    summary_lines.append(f"  Method: {method_name}")
                    if method_info.get("params"):
                        summary_lines.append(f"    Params: {', '.join(method_info['params'])}")
                    if method_info.get("docstring"):
                        summary_lines.append(f"    Docstring: {method_info['docstring']}")

                    # Variables for each method
                    if "variables" in method_info:
                        summary_lines.append("    Variables:")
                        for var_name, usage_list in method_info["variables"].items():
                            usage_str = ", ".join(usage_list)
                            summary_lines.append(f"      {var_name} -> {usage_str}")

                summary_lines.append("")  # blank line for spacing

            # 3) If we have no definitions at all
            if "no_definitions" in context_tree:
                message = context_tree["no_definitions"].get("message", "")
                summary_lines.append(message)

            # Create the final summary text
            context_summary = "\n".join(summary_lines).strip()
            return "Code analysis complete.\n"

        except Exception as e:
            return f"Error analyzing code: {e}"

    @line_magic
    def show_context_summary(self, line):
        """
        Magic line command to display the current context tree in a formatted form.
        """
        # Assuming print_context_summary() and context_tree are in scope
        # or imported from your 'core' module
        if 'print_context_summary' in globals():
            print_context_summary()
        else:
            print("print_context_summary() is not defined in the current scope.")
       


    @staticmethod
    def _split_code_and_explanation(response):
        """
        Split the LLM response into code and explanation text.

        Parameters:
        - response (str): The response from the LLM.

        Returns:
        - tuple: (code, explanation)
        """
        lines = response.splitlines()
        code_lines = []
        explanation_lines = []
        is_code_block = False

        for line in lines:
            # Detect code blocks (enclosed in triple backticks)
            if line.strip().startswith("```"):
                is_code_block = not is_code_block
                continue

            # Append to code or explanation based on current block
            if is_code_block:
                code_lines.append(line)
            else:
                explanation_lines.append(line)

        code = "\n".join(code_lines).strip()
        explanation = "\n".join(explanation_lines).strip()
        return code, explanation
    
    @staticmethod
    def analyze_codebase_fancy():
        """
        Displays a fancy message while analyzing the codebase.
        """
        message = [
            "🔍 Scanning your project...",
            "🛠️  Parsing functions, classes, and modules...",
            "⚙️  Building context tree...",
            "📊  Generating brilliance! "
        ]
        
        for line in message:
            display(line)
            time.sleep(1.5)
            clear_output(wait=True)


    @line_magic
    def generate_code(self, line):
        """Magic command to generate code and display it properly with explanations."""
        if not config.provider:
            return "Please set up a provider first using %set_llm_provider"

        function_name = line.strip()
        
        
                
        self.analyze_codebase_fancy()
        self.shell.run_line_magic('analyze_code', None)    
        # Get the current persona (mode)
        current_persona = get_persona()

        # Construct the prompt
        prompt = (
            f"Generate Python code for a function named '{function_name}' considering the context of the codebase provided: {context_tree}. {current_persona}"
        )

        # Call the appropriate LLM provider
        if config.provider == LLMProvider.TRANSFORMERS_LOCAL:
            response = call_local_transformers(prompt)
        elif config.provider == LLMProvider.TRANSFORMERS_HUB:
            response = call_huggingface_hub(prompt)
        elif config.provider == LLMProvider.OPENAI:
            response = call_openai(prompt)
        elif config.provider == LLMProvider.ANTHROPIC:
            response = call_anthropic(prompt)
        elif config.provider == LLMProvider.GEMINI:
            response = call_gemini(prompt)
        elif config.provider == LLMProvider.TRANSFORMERS_DOWNLOAD:
            response = call_local_transformers(prompt)
        else:
            return "Provider not implemented"

        # Split response into code and text explanation
        code, explanation = self._split_code_and_explanation(response)

        # Display the code with syntax highlighting
        if code:
            display_highlighted_code(code)

        # Display the explanation as Markdown
        if explanation:
            display(Markdown(explanation))

 


    
    @cell_magic
    def debug_cell(self, line, cell):
        """Debug a cell with AI assistance and display results with proper formatting."""
        if not config.provider:
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
            
            # Analyze codebase for context, similar to generate_code
            self.analyze_codebase_fancy()
            self.shell.run_line_magic('analyze_code', None)
            
            # Get current persona
            current_persona = get_persona()
            
            prompt = f"""Given this Python code:
    {cell}
    The code produced this error:
    {error_msg}
    Consider the context of the codebase if relevant:
    {context_tree}
    {current_persona}
    Please provide:
    1. A clear explanation of the error
    2. The corrected code
    3. Additional debugging tips if relevant"""
            
            # Call the appropriate LLM provider
            if config.provider == LLMProvider.TRANSFORMERS_LOCAL:
                response = call_local_transformers(prompt)
            elif config.provider == LLMProvider.TRANSFORMERS_HUB:
                response = call_huggingface_hub(prompt)
            elif config.provider == LLMProvider.OPENAI:
                response = call_openai(prompt)
            elif config.provider == LLMProvider.ANTHROPIC:
                response = call_anthropic(prompt)
            elif config.provider == LLMProvider.GEMINI:
                response = call_gemini(prompt)
            elif config.provider == LLMProvider.TRANSFORMERS_DOWNLOAD:
                response = call_local_transformers(prompt)
            else:
                return "Provider not implemented"
            
            # Split response into code and explanation
            code, explanation = self._split_code_and_explanation(response)
            
            # Display the explanation as Markdown first
            if explanation:
                display(Markdown(explanation))
            
            # Display the corrected code with syntax highlighting
            if code:
                print("\nCorrected code:")
                display_highlighted_code(code)
        else:
            output = stdout_capture.getvalue()
            if output:
                print("Code executed successfully. Output:", output)
            else:
                print("Code executed successfully with no output.")


    @cell_magic
    def refactor_code(self, line, cell):
        """Cell magic to suggest code refactoring improvements."""
        if not config.provider:
            return "Please set up a provider first using %set_llm_provider"
        
        # Analyze current codebase
        self.analyze_codebase_fancy()
        self.shell.run_line_magic('analyze_code', None)
        current_persona = get_persona()
        
        prompt = f"""Analyze this Python code and suggest refactoring improvements:
    {cell}

    Consider the broader codebase context:
    {context_tree}

    {current_persona}

    Please suggest:
    1. Code quality improvements
    2. Performance optimizations
    3. Better design patterns
    4. Refactored code implementation"""

        # Call appropriate provider and display results
        response = self._call_provider(prompt)
        code, explanation = self._split_code_and_explanation(response)
        
        if explanation:
            display(Markdown(explanation))
        if code:
            print("\nRefactored code suggestion:")
            display_highlighted_code(code)

    @cell_magic
    def explain_code(self, line, cell):
        """Cell magic to generate detailed explanation of code."""
        if not config.provider:
            return "Please set up a provider first using %set_llm_provider"
        
        current_persona = get_persona()
        prompt = f"""Explain this Python code in detail:
    {cell}

    {current_persona}

    Please provide:
    1. High-level overview
    2. Line-by-line explanation
    3. Key design decisions
    4. Usage examples"""
        
        response = self._call_provider(prompt)
        display(Markdown(response))

        

    @cell_magic
    def optimize_code(self, line, cell):
            """Magic command to suggest performance optimizations for code."""
            if not config.provider:
                return "Please set up a provider first using %set_llm_provider"
            
            # Run the code and profile it
            profiler = cProfile.Profile()
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            try:
                profiler.runctx(cell, self.shell.user_ns, {})
                stats = pstats.Stats(profiler)
                profile_output = StringIO()
                stats.sort_stats('cumulative').print_stats(20)
                profile_data = profile_output.getvalue()
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            
            current_persona = get_persona()
            prompt = f"""Analyze this Python code and its performance profile:

        Code:
        {cell}

        Profile results:
        {profile_data}

        {current_persona}

        Please suggest:
        1. Performance bottlenecks
        2. Optimization strategies
        3. Optimized implementation
        4. Benchmarking comparisons"""
            
            response = self._call_provider(prompt)
            code, explanation = self._split_code_and_explanation(response)
            
            if explanation:
                display(Markdown(explanation))
            if code:
                print("\nOptimized code suggestion:")
                display_highlighted_code(code)

    @cell_magic
    def generate_test(self, line, cell):
        """Cell magic to generate unit tests for code."""
        if not config.provider:
            return "Please set up a provider first using %set_llm_provider"
        
        self.analyze_codebase_fancy()
        current_persona = get_persona()
        
        prompt = f"""Generate comprehensive unit tests for this Python code:
    {cell}

    Consider the codebase context:
    {context_tree}

    {current_persona}

    Please provide:
    1. Test cases covering main functionality
    2. Edge cases
    3. Error cases
    4. Mocking examples if needed
    5. Complete test implementation"""
        
        response = self._call_provider(prompt)
        code, explanation = self._split_code_and_explanation(response)
        
        if explanation:
            display(Markdown(explanation))
        if code:
            print("\nGenerated test code:")
            display_highlighted_code(code)

    
    def _call_provider(self, prompt):
        """Helper method to call the configured LLM provider."""
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
