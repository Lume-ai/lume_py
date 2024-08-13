<p align="center">
  <img src="https://app.lume.ai/assets/logo-256.png" width="300px">
</p>
<p align="center">
  📚
  <a href="https://docs.lume.ai/">Documentation</a>
  &nbsp;
  •
  &nbsp;
  🖥️
  <a href="https://app.lume.ai/">Application</a>
  &nbsp;
  •
  &nbsp;
  🏠
  <a href="https://www.lume.ai/">Home</a>
</p>
<p align="center">
  <img src="https://icon2.cleanpng.com/20190623/fpb/kisspng-python-computer-icons-programming-language-executa-1713885557346.webp" width="64px">
</p>


# Lume Python SDK (`lume_py`)

## Overview

`lume_py` is a Python SDK designed to facilitate seamless interaction with the Lume API. It provides an intuitive and straightforward interface for developers to integrate Lume's services into their Python applications, enabling efficient access to Lume's powerful features.

## Features

- **Easy API Integration:** Quickly connect to and interact with the Lume API.
- **Asynchronous Support:** Built on top of `httpx`, offering asynchronous capabilities for better performance.
- **Pydantic Integration:** Utilizes `Pydantic` for data validation and settings management.
- **Extensible:** Modular design allows for easy customization and extension.

## Installation

To install the `lume_py` SDK, use the following pip command:

```bash
pip install lume-py


```

## Quickstart

Retrieve your `source_data` and `target_schema`.

```python
target_schema = {
    "type": "object",
    "properties": {
        "f_name": {
            "type": "string",
            "description": "The first name of the user",
        },
        "l_name": {
            "type": "string",
            "description": "The last name of the user",
        },
    },
    "required": ["f_name", "l_name"],
}

source_data = [
    {"first_name": "John", "last_name": "Doe"},
    {"first_name": "Jane", "last_name": "Smith"},
]
```


## Status

The Lume Python SDK is currently in beta. 
Please reach out to support if you have any questions, encounter any bugs, or have any feature requests.


## Additional Resources

For detailed information on creating pipelines, running jobs, and managing other workflows, please refer to the `examples` folder.


