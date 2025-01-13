# Magic Functions Documentation

## Overview

The CodeAssist module provides a suite of IPython magic commands and helper functions for analyzing, debugging, and enhancing Python code within a Jupyter Notebook environment. This documentation covers the usage, functionality, and details of all the provided magic commands and supporting methods.

## Magic Commands

## Code Theme
```bash
%set_code_theme <style_name>
```
### Description:
Sets the Pygments style dynamically for syntax highlighting.

Usage:
```bash
%set_code_theme <style_name>
```

### Example:
```bash
%set_code_theme monokai
```
### Notes:

If <style_name> is omitted, it prints the URL to check available styles.

Styles can be explored at https://pygments.org/styles/.

## LLM Persona
```bash
%set_persona <persona>
```
### Description:
Sets the LLM persona for generating responses dynamically.

### Usage:
```bash
%set_persona <persona>
```
### Example:
```bash
%set_persona friendly
```
#### Supported Personas:

beginnerfriendly

detailed

concise

normal

technical

expert

creative

## Set API Key
```bash
%set_api_key <provider> <key> [model]
```
### Description:
Sets the API key for a specified LLM provider.

### Usage:
```bash
%set_api_key <provider> <key> [model]
```
### Example:
```bash
%set_api_key openai your_api_key_here gpt-3.5-turbo
```
### Notes:

<provider>: The name of the LLM provider (e.g., openai).

[model]: Optionally specify the model to use.

Returns a success message if the key is set correctly.

## Set LLM provider
```bash
%set_llm_provider <provider> [model_path] [options] # for local transformers
```

``` bash
%set_llm_provider <provider> [model_name]  # for LLMS
```
### Description:
Sets the LLM provider and optionally loads a model.

Usage:
```bash
%set_llm_provider <provider> [model_path] [options]
or
%set_llm_provider <provider> [model_name]
```
### Example:
```bash
%set_llm_provider transformers_local /path/to/model
or
%set_llm_provider openai gpt-4
```

### Options:

--8bit: Load the model in 8-bit mode (if supported).

--device=<device>: Specify the device (e.g., cpu, cuda).

### Notes:

Supports providers like transformers_local and transformers_download.

For downloading models, the model path is mandatory.

## Analyze Code
```bash
%analyze_code 
```
### Description:
Analyzes the code in the specified Jupyter Notebook and builds a context tree.
Mandatory to run before any other commands in the notebook and if you add new functions after running the command please run again to help the model gain full context.

### Usage:
```bash
%analyze_code 
```
### Example:
```bash
%analyze_code (ideally)
if that fails then:
%analyze_code my_notebook.ipynb

```
### Notes:

If <notebook_path> is omitted, it tries to determine the current notebook path automatically.

Extracts functions, variables, and their bodies into a context tree.

## Generate Code
```bash
%generate_code <function_name>
```
### Description:
Generates Python code for a specified function using the context tree.

### Usage:
```bash
%generate_code <function_name>
```
### Example:
```bash
%generate_code find prime numbers between two numbers 
```
### Notes:

Requires an LLM provider to be set.

The context tree must be built beforehand using %analyze_code.

## Debugging cells
```bash
%%debug_cell
```
### Description:
Debugs a cell with AI assistance.

### Usage:
```bash
%%debug_cell
<cell content>
```
### Example:
```bash
%%debug_cell
x = 1 / 0
```
### Notes:

Captures output and errors from the cell.

Provides AI-generated suggestions for resolving errors based on the current context tree.
