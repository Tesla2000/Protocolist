## FunctionDef import_python(root)
**import_python**: The function of import_python is to recursively import Python modules from a specified root directory.

**parameters**:
- root: The root directory path from which to start importing Python modules.

**Code Description**:
The import_python function takes a root directory path as input and iterates through all files and subdirectories within the root directory. It skips certain directories such as "__init__.py", "pycache", and "__pycache__". For each file encountered, it determines the relative path, constructs the module path, imports the module, and yields the module name. If a subdirectory is encountered, the function recursively calls itself to import modules from that subdirectory.

**Note**:
- This function is useful for dynamically importing Python modules from a specified directory, which can be helpful for modularizing code and improving code organization.
- Ensure that the root directory provided contains valid Python modules to import, as the function relies on the presence of Python files for importing.
