from setuptools import setup, find_packages

setup(
    name="code_assist",  # The name of your package
    version="0.1.0",    # The version of your package
    packages=find_packages(),  # Automatically find all the subpackages in the code_assist directory
    install_requires=[  # List of dependencies that need to be installed
        "torch",
        "transformers",
        "huggingface_hub",
        "google-generativeai",
        "requests",
        "IPython",
        "nbformat",
        "pytest",
        "pytorch-lightning",
    ],
    entry_points={  # If you want to create a command-line tool
        "console_scripts": [
            "code-assist=code_assist.main:main",  # Modify based on your project's entry point
        ],
    },
    classifiers=[  # Optional: help categorize your project
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Optional: specify Python version requirement
)
