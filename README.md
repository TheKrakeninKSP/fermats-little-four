# fermats-little-four

- before you start coding, setup the environment correctly.
- create your own branch
- git clone the branch onto your pc: git clone https://github.com/TheKrakeninKSP/fermats-little-four.git -b [your-branch-name] --single-branch [folder-name-to-clone-into]
- ensure you are on the correct branch using 'git branch' command
- commit with meaningful messages, and push with 'git push'. no need to specify branch, it will automatically push to your branch.
- make pull requests from github.com when you are ready to merge with the main branch.

# code editor setup
- for python code, please install the black-formatter, pylint and isort in your VSCode editor. This will ensure readability and help avoid bugs.
- in the directory, create a venv, and use python 3.12.3 for compatibility, use the requirements.txt file to ensure all dependencies are installed.
- if you forget to use requirements.txt during venv creation, then just do pip install -r requirements.txt
- activate the venv environment, and install pipreqs.
- run the build.py file periodically, as this will update the requirements.txt file
- please ensure you do all the pip installs after you activate the venv environment

# use the .gitignore file to keep the codebase clean
- please use the .gitignore file, dont push any videos/large files to git
- if you must keep some images in the codebase, please ensure you only keep the minimal amount
- have a separate 'data' folder for images, data, and videos and other stuff
- push only the code files and configs to git

this setup process will take a while, but please ensure you do it correctly. 
this will help us debug properly, and will avoid a million headaches later on.
