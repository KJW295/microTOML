# micropython-toml

A minimal and lightweight TOML parser for MicroPython.  
Supports global key-value pairs and sectioned tables with easy callable access.

## ✨ Features

- No dependencies
- Global and table-scoped keys
- Supports strings, integers, floats
- Callable access syntax: `config.section("key")`

## 📦 Installation (with `mip`)

```python
import mip
mip.install("github:yourusername/micropython-toml")
