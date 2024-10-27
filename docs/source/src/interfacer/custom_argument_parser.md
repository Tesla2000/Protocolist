## ClassDef CustomArgumentParser
**CustomArgumentParser**: The function of CustomArgumentParser is to extend the functionality of the argparse.ArgumentParser class by customizing the behavior of adding arguments.

**attributes**:
- add_argument: A method that customizes the behavior of adding arguments by checking if the argument type is a boolean and converting it accordingly.
- _str2bool: A method that converts a string representation of a boolean value to a boolean type.

**Code Description**:
The CustomArgumentParser class extends the argparse.ArgumentParser class and overrides the add_argument method to handle boolean arguments more effectively. When adding an argument, if the argument type is a boolean, it converts the string representation of the boolean value to a boolean type using the _str2bool method. The _str2bool method checks if the input string represents a boolean value and converts it accordingly.

In the project, the CustomArgumentParser class is utilized in the parse_arguments function defined in src/config.py. The parse_arguments function takes a config_class parameter, creates an instance of CustomArgumentParser, adds arguments based on the fields of the config_class, and then parses the arguments.

**Note**:
Developers using the CustomArgumentParser class should be aware of the custom behavior implemented for boolean arguments and ensure that the input values are compatible with the conversion logic provided.

**Output Example**:
If a boolean argument "--enable_feature" with a value of "true" is added using CustomArgumentParser, it will be converted to a boolean type True during parsing.
### FunctionDef add_argument(self)
**add_argument**: The function of add_argument is to handle the addition of arguments to the argument parser, specifically converting string representations of boolean values to boolean types when the argument type is bool.

**parameters**:
- self: The instance of the CustomArgumentParser class.
- *args: Variable length argument list.
- **kwargs: Arbitrary keyword arguments.

**Code Description**: 
The add_argument function first checks if the type of the argument is bool. If it is, the function utilizes the _str2bool method from the CustomArgumentParser class to convert the string representation to a boolean value before adding the argument using the super() method. This approach ensures that boolean type arguments are correctly processed and added to the argument parser.

The _str2bool method is responsible for converting string representations of boolean values to boolean types. It checks if the input value is already a boolean and converts strings like "yes", "true", "t", "y", "1" to True, and strings like "no", "false", "f", "n", "0" to False. If the input value does not match any of these, an ArgumentTypeError is raised to indicate an invalid boolean value.

The add_argument function plays a crucial role in the CustomArgumentParser class by facilitating the correct handling of boolean type arguments during the argument addition process. By utilizing the _str2bool method, it ensures that the arguments are appropriately converted and added to the argument parser, enhancing the overall functionality and usability of the CustomArgumentParser class.

**Note**: Developers using the add_argument function should ensure that the input string represents a valid boolean value to prevent errors and ensure the accurate processing of boolean type arguments.
***
### FunctionDef _str2bool(self, v)
**_str2bool**: The function of _str2bool is to convert a string representation of a boolean value to a boolean type.

**parameters**:
- self: The instance of the class.
- v: The string value to be converted to a boolean.

**Code Description**: 
The _str2bool function first checks if the input value is already a boolean. If not, it converts the string representation of a boolean value to a boolean type. It accepts strings like "yes", "true", "t", "y", "1" as True, and strings like "no", "false", "f", "n", "0" as False. If the input value does not match any of these, it raises an ArgumentTypeError.

This function is called within the CustomArgumentParser class to handle boolean type arguments passed to the add_argument method. When the type of the argument is bool, the _str2bool function is used to convert the string representation to a boolean value before adding the argument.

**Note**: 
Developers should ensure that the input string represents a valid boolean value to avoid raising an ArgumentTypeError.

**Output Example**: 
If the input value is "yes", the function will return True.
***
