from setuptools import setup, find_packages
import pathlib
import os

# Get the current directory
current_dir = pathlib.Path(__file__).parent

# Add debug prints
print(f"Current directory: {current_dir}")
print(f"Files in directory: {os.listdir(current_dir)}")

try:
    readme_path = current_dir / "README.md"
    print(f"README path: {readme_path}")
    print(f"README exists: {readme_path.exists()}")
    
    if not readme_path.exists():
        # Provide a fallback description if README.md is missing
        long_description = "CodeMate - A Python package for code assistance"
    else:
        long_description = readme_path.read_text(encoding='utf-8')
except Exception as e:
    print(f"Error reading README: {e}")
    long_description = "CodeMate - A Python package for code assistance"

setup(
    name="codemate_ai",
    version="0.1.4",
    author="Manan Gupta",
    author_email="manangupta9901@gmail.com",
    description="CodeMate",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/codemate-ai",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "huggingface_hub",
        "google-generativeai",
        "requests",
        "IPython",
        "nbformat",
        "pytest",
        "pytorch-lightning",
        "jupyter_server",
        "astor",
        "pygments"
    ],
    entry_points={
        "console_scripts": [
            "codemate_ai=codemate_ai.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
