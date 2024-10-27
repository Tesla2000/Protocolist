## FunctionDef add_markdowns
**add_markdowns**: The function of add_markdowns is to add references to Markdown files in specified reStructuredText files.

**parameters**:
- markdown_file_path: A Path object representing the path to the Markdown file.
- source_path: A Path object representing the source directory containing the reStructuredText files.

**Code Description**:
The add_markdowns function first defines an inner function _conv2ref, which converts the path of a Markdown file to a relative reference. It then sets the source_path to the "docs/source" directory. The function iterates over the reStructuredText files in the source_path, reads the content of each file, and locates a specific header within the content. It then extracts the content before and after the header, determines the path for the documentation, finds all Markdown files in that path, converts their paths to references using _conv2ref, and appends these references to the file content. Finally, it writes the updated content back to the file.

**Note**:
- This function assumes a specific directory structure where Markdown files are located within subdirectories corresponding to the reStructuredText files.
- Ensure that the additional_documents_header variable is defined and contains the header used to locate the insertion point for the Markdown file references.

**Output Example**:
If the content of a reStructuredText file before modification is:
```
Some content before
.. additional_documents_header

Some content after
```

After running add_markdowns, the content will be updated to include Markdown file references:
```
Some content before
.. additional_documents_header

   path/to/markdown/file1
   path/to/markdown/file2

Some content after
```
### FunctionDef _conv2ref(markdown_file_path)
**_conv2ref**: The function of _conv2ref is to convert the input markdown file path to a relative path from a specified source path without a file extension.

**parameters**:
- markdown_file_path: The path to the markdown file.
  
**Code Description**:
The _conv2ref function takes a markdown file path as input and returns the relative path of the file from a specified source path without the file extension. It uses the relative_to method to get the relative path from the source path and the with_suffix method to remove the file extension.

**Note**:
Ensure that the source_path variable is defined before calling this function to get the correct relative path.

**Output Example**:
If markdown_file_path = "/path/to/file/example.md" and source_path = "/path/to", the function will return "file/example".
***
