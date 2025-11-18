class TOML:
    """
    Very small TOML reader aimed at MicroPython.

    Supported subset:
      - Global key/value pairs:   key = value
      - Simple tables:            [table_name]
      - Array-of-tables:          [[table_name]]
      - Value types:
          * strings (single or double quoted)
          * integers and floats (with optional underscores)
          * booleans: true / false (case-insensitive)
      - Whole-line comments starting with '#'
      - Leading / trailing whitespace around keys and values

    Not supported:
      - Arrays of values, inline tables, nested tables (foo.bar), dates/times
      - Multi-line strings
      - Inline comments after values
    """

    def __init__(self, toml_str):
        self._data = self._parse_toml(toml_str)

    # ---------- Public API ----------

    def __call__(self, key, default=None):
        """
        Look up a global (top-level) key.

        Example:
            title = config("title")
        """
        value = self._data.get(key)
        if isinstance(value, dict) or isinstance(value, list):
            # Tables / arrays are not considered scalar values
            return default
        return value if value is not None else default

    def __getattr__(self, attr):
        """
        Attribute access for tables and arrays-of-tables.

        Examples:
            host = config.database("host")      # for [database]
            sensors = config.SENSOR            # for [[SENSOR]]
        """
        data = self._data
        table = data.get(attr)

        # Normal table -> return callable getter
        if isinstance(table, dict):
            def getter(key, default=None):
                return table.get(key, default)
            return getter

        # Array-of-tables -> return the list directly
        if isinstance(table, list):
            return table

        raise AttributeError("No such section: " + attr)

    # ---------- Parsing internals ----------

    def _parse_toml(self, toml_str):
        result = {}
        current_section = result  # start at global level

        for raw_line in toml_str.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue

            # Array-of-tables: [[name]]
            if line.startswith("[[") and line.endswith("]]"):
                section_name = line[2:-2].strip()
                if not section_name:
                    current_section = result
                    continue

                arr = result.get(section_name)
                if not isinstance(arr, list):
                    arr = []
                    result[section_name] = arr

                new_table = {}
                arr.append(new_table)
                current_section = new_table
                continue

            # Simple table: [name]
            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip()
                if not section_name:
                    current_section = result
                    continue

                table = result.get(section_name)
                if not isinstance(table, dict):
                    table = {}
                    result[section_name] = table

                current_section = table
                continue

            # Key/value line
            eq_index = line.find("=")
            if eq_index == -1:
                # Not a valid line in our subset, ignore
                continue

            key = line[:eq_index].strip()
            value_str = line[eq_index + 1:].strip()

            if not key:
                continue

            value = self._parse_value(value_str)
            current_section[key] = value

        return result

    def _parse_value(self, value_str):
        """
        Parse a TOML value from a stripped string.
        Handles strings, ints, floats, and booleans.
        """
        if not value_str:
            return ""

        # Quoted string (single or double)
        if (value_str[0] == '"' and value_str[-1] == '"') or \
           (value_str[0] == "'" and value_str[-1] == "'"):
            return value_str[1:-1]

        # Booleans: true / false (case-insensitive)
        lower = value_str.lower()
        if lower == "true":
            return True
        if lower == "false":
            return False

        # Numbers: try int, then float. Strip underscores for TOML-style numbers.
        num_candidate = value_str.replace("_", "")

        try:
            return int(num_candidate)
        except Exception:
            pass

        try:
            return float(num_candidate)
        except Exception:
            # Fallback: keep as string
            return value_str
