# CodeAssist: AI-Powered Jupyter Notebook Assistant

**CodeAssist** is a Jupyter notebook extension that leverages powerful AI models for code assistance, debugging, and generation. It supports multiple Large Language Model (LLM) providers, including OpenAI, Anthropic, Google Gemini, and local models via Hugging Face, bringing a versatile range of tools right to your coding environment.

## Features

- 🤖 **Multiple LLM Provider Support**: Seamlessly integrate with OpenAI, Anthropic Claude, Google Gemini, and Hugging Face.
- 🔍 **Contextual Code Analysis**: Analyze your code's context and structure for better understanding.
- 🐛 **AI-Powered Debugging**: Get suggestions to fix errors directly within the notebook.
- ✨ **Code Generation**: Generate new code based on your current project context.
- 📱 **Local Model Support**: Run models locally using Hugging Face’s Transformers library.
- 📱 **Customization**: Customize the look and feel of the interface and the LLM interacting with.
- 🚀 **Easy Integration**: Effortlessly integrate with your Jupyter notebooks for enhanced productivity.

## Installation

Install CodeAssist via `pip`:

```bash
pip install code_assist
```
Install CodeAssist via git clone:
```bash
git clone https://github.com/somethingreallycool123/CodeAssist.git
pip install -e .
```

## Quick Start
### Import the extension in your Jupyter notebook:
```python


%load_ext code_assist
```
### Set up your preferred LLM provider:

#### For API-based LLMs (OpenAI, Anthropic, Google Gemini, etc): 

```python
%set_llm_provider <provider_name>
%set_api_key <provider_name> <YOUR_API_KEY>

```


#### Local Model Support
CodeAssist also supports running models locally using Hugging Face’s Transformers library:

Download and run a model locally:

```python

%set_llm_provider transformers_download <model_name> --8bit  # The --8bit option is optional for reduced memory usage
```
Use an already downloaded model:
```python

%set_llm_provider transformers_local ./models/my_model
```
### Analyze your notebook's code context:
```python

%analyze_code
```

### Magic Commands
```markdown

%set_api_key: Set API keys for different providers.
%set_llm_provider: Configure the LLM provider (e.g., OpenAI, Anthropic, or local models).
%analyze_code: Analyze and build context from your notebook’s code.
%generate_code: Generate new code based on the current context.
%%debug_cell: Debug a cell with AI assistance.
%set_code_theme: Change the background theme of the code solutions.
%set_persona: Change the LLM behaviour to various types including but not limited to detailed, consise, beginnerfriendly etc.
```
To understand each individual magic command functionality and operations, see [Magic function Documentation](magic_func_documentation.md).

## Example Usage
Set up OpenAI as the provider:
```python

%set_api_key openai YOUR_API_KEY
%set_llm_provider openai
```
Set up a locally running model as provider:
```python
%set_llm_provider transformers_download facebook/opt-350m --8bit
```
OR
```python
%set_llm_provider transformers_local ./models/my_model
```
Analyze the current notebook:
```python

%analyze_code
```
Generate a new function:
```python

%generate_code create_data_pipeline
```
Debug a problematic cell:
```python

%%debug_cell
def process_data(df):
    result = df.groupby('category').mean()
    return result['value'] / 0  # Intentional error
```
Change the background theme:
```python
%set_code_theme rrt
```
Change the persona of the LLM:
```python
%set_persona expert
```


## Project Structure
```markdown

CodeAssist/
├── code_assist/
│   ├── __init__.py
│   ├── core.py
│   ├── magics.py
│   ├── providers.py
├── tests/
│   ├── test_ML.py
│   ├── test_setup.py
├── LICENSE
├── README.md
├── requirements.txt
├── setup.py
└── .gitignore

```
## Contributing
We welcome contributions! If you'd like to improve or add features to CodeAssist, please submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For inquiries, please contact us via:

 Email: [manangupta9901@gmail.com]
 
 GitHub: somethingreallycool123

