import argparse
import copy as deepcopy_module
import os
import platform
import subprocess
import sys

import yaml

from .singleton_base import SingletonBase


class ConfumoError(Exception):
    """Custom exception for Confumo errors.

    :param message: Error message describing the exception.
    :type message: str
    """

    def __init__(self, message: str = "An error occurred in Confumo"):
        self.message = message
        super().__init__(self.message)


class Confumo(SingletonBase):
    """
    Subclass of BaseConfumo that implements configuration functionality,
    including argument parsing, platform detection, and YAML configuration loading.
    """

    def __init__(self, app_name='confumo', additional_args=None):
        """
        Initialize the Confumo instance.

        :param app_name: Name of the application, defaults to 'confumo'
        :param additional_args: List of additional arguments for argparse
        """
        super().__init__()
        self.app_name = app_name
        self.platform_name = platform.system()
        self.config_dir = os.path.join(self._get_default_config_dir(), self.app_name)
        self.additional_args = additional_args

        # Initialize self.args and self.config before any attribute access
        self.args = self._parse_args(additional_args=self.additional_args)
        self.config = self._initialize_configuration()

    def _get_default_config_dir(self):
        """
        Get the default configuration directory based on the platform.

        :return: Default configuration directory path
        :raises ConfumoError: If the operating system is unsupported or necessary environment variables are missing.
        """
        if self.platform_name == 'Darwin':
            return os.path.expanduser("~/Library/Application Support")
        elif self.platform_name in ['Linux', 'CYGWIN']:
            return os.path.expanduser("~/.config")
        elif self.platform_name == 'Windows':
            local_app_data = os.getenv('LOCALAPPDATA')
            if local_app_data:
                return local_app_data
            raise ConfumoError("LOCALAPPDATA environment variable is not set on Windows")
        else:
            raise ConfumoError(f"Unsupported OS: {self.platform_name}")

    def _parse_args(self, args=None, additional_args=None):
        """
        Parse command-line arguments.

        :param args: List of arguments to parse, defaults to None (sys.argv)
        :param additional_args: List of dictionaries defining additional arguments
        :return: Namespace of parsed arguments
        """
        parser = argparse.ArgumentParser(description=f"{self.app_name} Configuration")
        parser.add_argument('--config', type=str, help="Path to the YAML configuration file")
        parser.add_argument('--log_level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            default='INFO', help="Logging level")
        parser.add_argument('--config_dir', type=str, default=self.config_dir,
                            help=f"Where to load/save config data. Defaults to {self.config_dir}")
        if additional_args:
            for add_arg in additional_args:
                parser.add_argument(*add_arg['flags'], **add_arg['kwargs'])
        parsed_args = parser.parse_args(args)
        return parsed_args

    def _initialize_configuration(self):
        """
        Initialize the configuration dictionary.

        :return: Configuration dictionary
        """
        config_dir = self._ensure_windows_path(self.args.config_dir)
        config = {
            'log_level': self.args.log_level,
            'app_name': self.app_name,
            'config_dir': config_dir
        }
        if self.args.config:
            file_config = self._read_config_file(self.args.config)
            config.update({k: v for k, v in file_config.items() if v is not None})
        self._setup_module_attributes()
        return config

    def _read_config_file(self, config_path):
        """
        Read the configuration from a YAML file.

        :param config_path: Path to the YAML configuration file
        :return: Configuration dictionary loaded from the file
        """
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def _ensure_windows_path(self, path):
        """
        Ensure that the given path is a Windows-compatible path.

        :param path: The path to ensure compatibility for
        :return: Windows-compatible path
        """
        if not self._is_cygwin():
            return os.path.abspath(path)
        else:
            return self._cygwin_to_windows_path(path)

    def _is_cygwin(self):
        """
        Determine if the current environment is Cygwin.

        :return: True if Cygwin, False otherwise
        """
        ostype = os.getenv('OSTYPE', '').lower()
        return 'cygwin' in ostype

    def _cygwin_to_windows_path(self, cygwin_path):
        """
        Convert a Cygwin path to a Windows path.

        :param cygwin_path: The Cygwin path to convert
        :return: Converted Windows path
        """
        result = subprocess.run(['cygpath', '-w', cygwin_path], capture_output=True, text=True)
        return result.stdout.strip()

    def save_config(self):
        """
        Save the current configuration as a YAML file in the config directory.

        :return: The path to the saved configuration file.
        """
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        config_path = os.path.join(self.config_dir, f"{self.app_name}_config.yaml")
        with open(config_path, 'w') as file:
            yaml.dump(self.config, file)
        return config_path

    def copy(self) -> 'Confumo':
        """
        Create a deep copy of the current configuration instance, including dynamic attributes,
        while excluding any module-level or uncopyable attributes like modules.

        :return: Deep copy of the configuration instance
        :rtype:Confumo
        """
        # Ensure the instance is updated with all dynamically added module-level attributes
        module = sys.modules[self.__class__.__module__]

        # Dynamically add module-level attributes
        for attr_name in dir(module):
            if not attr_name.startswith('__') and hasattr(module, attr_name):
                setattr(self, attr_name, getattr(module, attr_name))

        # Shallow copy the instance's dictionary to exclude un-copyable objects
        shallow_copy = {k: v for k, v in self.__dict__.items() if not isinstance(v, type(sys))}

        # Create a new instance and update it with the shallow copy
        copied_instance = deepcopy_module.copy(self)  # Use shallow copy here
        copied_instance.__dict__.update(shallow_copy)  # Update the instance's dictionary with the shallow copy

        return copied_instance  # Add this line to return the copied instance

    def __getattr__(self, name):
        """
        Allow access to config keys and parsed arguments as attributes.
        """
        # Avoid recursion during deepcopy
        if name in ('__getstate__', '__setstate__'):
            raise AttributeError

        if 'config' in self.__dict__ and name in self.config:
            return self.config[name]
        elif 'args' in self.__dict__ and hasattr(self.args, name):
            return getattr(self.args, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __repr__(self):
        """
        Return a string representation of the configuration instance.

        :return: String representation
        """
        return f"<{self.__class__.__name__} platform_name={self.platform_name}, config_dir={self.config_dir}>"
