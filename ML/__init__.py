from .magics import CodeAssistMagics
from .providers import config, LLMProvider

def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(CodeAssistMagics)