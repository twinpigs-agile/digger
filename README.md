# The Twin Pigs Python Project Skeleton

When you begin an own Python project, it is very important to start with a good project structure. This is a Python project skeleton. I frequently use it for my small to medium projects. It can be customised and already includes many of things you may need for most projects:

 - build scripts
 - Mypy (static type checking) and Flake8 (linting)
 - code formatting using Black
 - localisation using gettext
 - Jinja2 templates
 - unittest and doctest runs
 - building PyInstaller executables for Windows and Linux
 - GitHub Action with support for checking commits and pull requests (Linux)
 - GitHub Action doing version increments and releases for Windows and Linux (currently it includes only the executables; customise this when building an own project).

NB: It uses Bash scripts even on Windows, so use Git Bash. And it doesn't provide setup.py.
