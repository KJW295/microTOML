class TOML:
    def __init__(self, toml_str):
        """
        Initialize the TOML instance by parsing the provided TOML string.
        Global key/value pairs are stored at the top level, and sections are
        stored as dictionaries.
        """
        self._data = self._parse_toml(toml_str)

    def _parse_toml(self, toml_str):
        """
        A minimal TOML parser.
        
        Supports:
          - Global key-value pairs.
          - Table sections (lines between '[' and ']').
          - Key-value pairs with strings (quoted), integers, and floats.
          - Ignores blank lines and comments (lines starting with '#').

        Returns:
          dict: Parsed TOML data.
        """
        result = {}
        current_section = result  # Start with global scope

        for line in toml_str.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for table header.
            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip()
                if section_name:
                    result[section_name] = {}
                    current_section = result[section_name]
                continue

            # Process key = value lines.
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Handle quoted strings.
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                else:
                    # Try to convert to a number (int or float).
                    try:
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except Exception:
                        # If conversion fails, leave as string.
                        pass

                current_section[key] = value

        return result

    def __getattr__(self, attr):
        """
        Enable attribute access for sections.
        
        If the attribute name matches a section (i.e. its value is a dictionary),
        then return a callable that accepts a key and returns the corresponding
        value from that section.
        """
        if attr in self._data and isinstance(self._data[attr], dict):
            table = self._data[attr]
            def getter(key):
                return table.get(key, None)
            return getter
        else:
            raise AttributeError(f"No such section: {attr}")

    def __call__(self, key):
        """
        Enable global key lookup. For example, if you have a global key 'title',
        you can do: toml('title')
        """
        # Only returns a value if it is a global key (non-dict).
        if key in self._data and not isinstance(self._data[key], dict):
            return self._data[key]
        else:
            return None

# # Example usage:
# if __name__ == "__main__":
#     #toml_str =
#     """
#     # Example configuration
# 
#     title = "Example Config"
# 
#     [database]
#     host = "127.0.0.1"
#     port = 3306
#     timeout = 30.5
# 
#     [server]
#     enable_logging = "true"
#     """
#     
#     with open('config.toml', 'r') as file:
#         configFile = file.read()
#         #print(contents)
#         config = TOML(configFile)
#     
#     
# 
#     # Accessing a value from the global scope:
#     print("Title:", config("title"))  # Output: Example Config
# 
#     # Accessing values from sections using attribute-call syntax:
#     print("Database host:", config.database("host"))   # Output: 127.0.0.1
#     print("Database port:", config.database("port"))   # Output: 3306
#     print("Server logging enabled:", config.server("enable_logging"))  # Output: true

