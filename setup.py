from setuptools import setup, find_packages

setup(
    name="codemate_ai",
    version="0.1.2",
    author="Manan Gupta",
    author_email="manangupta9901@gmail.com",
    description="CodeMate",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Set to Markdown
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
