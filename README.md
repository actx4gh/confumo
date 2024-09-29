
# Confumo

Confumo is a flexible configuration management library for Python applications. It provides:

- **Singleton Pattern Implementation**: Ensures that only one instance of your configuration class exists throughout your application.
- **Platform-Aware Configuration Directory Management**: Automatically determines and uses the appropriate configuration directory based on the operating system (Windows, Linux, macOS).
- **YAML-Based Configuration Loading**: Supports loading configuration from YAML files.
- **Command-Line Argument Parsing**: Integrates with `argparse` to parse command-line arguments, including custom arguments specific to your application.

## Installation

```bash
pip install confumo
```

## Basic Usage

```python
from confumo import Confumo

# Initialize the singleton instance
config = Confumo.get_instance(app_name='my_app')

# Access configuration attributes
print(config.log_level)
print(config.config_dir)
```

### Example Usage in Python Shell

```bash
$ python
>>> from confumo import Confumo
>>> config = Confumo.get_instance(app_name='my_app')
>>> config
<Confumo platform_name=Windows, config_dir=C:\Users\your_user\AppData\Local\my_app>
>>> config.log_level
'INFO'
>>> config.config_dir
'C:\Users\your_user\AppData\Local\my_app'
```

Confumo automatically detects the platform and sets the `config_dir` accordingly.

### Note on Module-Level Attribute Access
If you want to enable module-level access for certain attributes (like `log_level` or `config_dir`), you need to ensure that these attributes are explicitly promoted to the module level after initializing the `Confumo` instance. However, by default, you should access these attributes through the `config` object (i.e., `config.log_level`).

## Saving and Loading Configuration

You can save the current configuration to a YAML file and load configurations from a YAML file.

```python
# Save the current configuration to a YAML file
config.save_config()

# The configuration file will be saved as 'my_app_config.yaml' in the config directory
```

If you have a YAML configuration file, you can load it using the `--config` command-line argument.

```bash
$ python main.py --config path/to/config.yaml
```

## License

This project is licensed under the MIT License.
