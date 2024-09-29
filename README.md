
# Confumo

Confumo is a flexible configuration management library for Python applications. It provides:

- **Singleton Pattern Implementation**: Ensures that only one instance of your configuration class exists throughout your application.
- **Module-Level Attribute Promotion**: Allows instance attributes to be accessed directly from the module level, simplifying access to configuration properties.
- **Platform-Aware Configuration Directory Management**: Automatically determines and uses the appropriate configuration directory based on the operating system (Windows, Linux, macOS).
- **YAML-Based Configuration Loading**: Supports loading configuration from YAML files.
- **Command-Line Argument Parsing**: Integrates with argparse to parse command-line arguments, including custom arguments specific to your application.

## Installation

```bash
pip install confumo
```

## Basic Usage

```python
from confumo.confumo import Confumo

# Initialize the singleton instance
config = Confumo.get_instance(app_name='my_app')

# Access configuration attributes
print(config.log_level)
print(config.config_dir)
```

### Example Usage in Python Shell

```bash
$ python
>>> from confumo.confumo import Confumo
>>> config = Confumo.get_instance(app_name='my_app')
>>> config
<Confumo platform_name=Windows, config_dir=C:\Users\your_user\AppData\Local\my_app>
>>> config.log_level
'INFO'
>>> config.config_dir
'C:\Users\your_user\AppData\Local\my_app'
```

Confumo automatically detects the platform and sets the `config_dir` accordingly.

### Module-Level Attribute Access

After initializing the singleton instance, you can access configuration attributes directly from the module level, thanks to module-level attribute promotion.

```python
# confumo_example.py
from confumo.confumo import Confumo

# Initialize the singleton instance
Confumo.get_instance(app_name='my_app')

# Now, you can access attributes directly from the module
import confumo.confumo as confumo_module

print(confumo_module.log_level)     # Outputs: 'INFO'
print(confumo_module.config_dir)    # Outputs: Platform-specific config directory
```

## Extending Confumo with Custom Subclasses

### 1. Subclass with Custom Methods and Logic

You can subclass Confumo to add custom methods and properties specific to your application.

```python
# ui_config.py
from confumo.confumo import Confumo

class UIConfiguration(Confumo):
    """Subclass of Confumo that handles UI-related configuration."""

    def __init__(self, app_name='ui_app', additional_args=None):
        super().__init__(app_name=app_name, additional_args=additional_args)
        self.font_face = "Helvetica"
        self.font_size = 12

        # After initialization, set up module-level attributes
        self._setup_module_attributes()

    def update_font(self, new_face, new_size):
        self.font_face = new_face
        self.font_size = new_size
```

#### Usage:

```python
# main.py
import ui_config

# Initialize the singleton instance
ui_config.UIConfiguration.get_instance(app_name='ui_app')

# Access attributes directly from the module
print(ui_config.font_face)  # Outputs: 'Helvetica'

# Update font settings
ui_config.update_font('Arial', 14)
print(ui_config.font_face)  # Outputs: 'Arial'
```

### 2. Subclass with Custom Command-Line Arguments

You can extend the base argument parsing to include additional command-line flags specific to your application.

```python
# backend_service_config.py
from confumo.confumo import Confumo

class BackendServiceConfig(Confumo):
    """Subclass that adds backend-related command-line arguments."""

    def __init__(self, app_name='backend_service_name', additional_args=None):
        if additional_args is None:
            additional_args = []
        additional_args.extend([
            {
                'flags': ['--upstream_api_provider_ip'],
                'kwargs': {
                    'type': str,
                    'nargs': '*',
                    'help': 'IP address for API service'
                }
            },
            {
                'flags': ['--upstream_api_provider_port'],
                'kwargs': {
                    'type': str,
                    'help': 'Port for API service'
                }
            }
        ])
        super().__init__(app_name=app_name, additional_args=additional_args)

        # After initialization, set up module-level attributes
        self._setup_module_attributes()
```

#### Usage:

```bash
$ python main.py --upstream_api_provider_ip 192.168.1.100 --upstream_api_provider_port 8080
```

```python
# main.py
import backend_service_config

# Initialize the singleton instance
backend_service_config.BackendServiceConfig.get_instance()

# Access command-line arguments directly
print(backend_service_config.upstream_api_provider_ip)    # Outputs: ['192.168.1.100']
print(backend_service_config.upstream_api_provider_port)  # Outputs: '8080'
```

### Why This Works

The Confumo class is designed to be flexible and extensible:

- **Singleton Behavior**: Ensures a single instance of your configuration class exists, accessible throughout your application.
- **Module-Level Attribute Promotion**: Allows you to access configuration attributes directly from the module, simplifying access patterns.
- **Customizable Configuration**: By subclassing Confumo, you can define new properties, methods, and extend command-line arguments to suit your application's needs.

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

## Copying Configuration Instances

If you need to create a copy of the configuration instance, you can use the `copy()` method.

```python
# Create a copy of the configuration instance
config_copy = config.copy()

# Modify the copy without affecting the original
config_copy.log_level = 'DEBUG'

print(config.log_level)       # Outputs: 'INFO' (original remains unchanged)
print(config_copy.log_level)  # Outputs: 'DEBUG' (copy is modified)
```

## Supported Platforms

Confumo supports different platforms and automatically manages configuration directories:

- **Windows**: Uses `%LOCALAPPDATA%` environment variable.
- **Linux**: Uses `~/.config` directory.
- **macOS**: Uses `~/Library/Application Support` directory.

## License

This project is licensed under the MIT License.
