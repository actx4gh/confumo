import os
import platform
from unittest import mock

import pytest

from confumo import Confumo, ConfumoError


def test_singleton_instance():
    """Test that Confumo class implements the singleton pattern."""
    instance1 = Confumo.get_instance(app_name="testapp")
    instance2 = Confumo.get_instance(app_name="testapp")
    assert instance1 is instance2, "Confumo is not maintaining singleton behavior"


def test_platform_name():
    """Test that the platform name is correctly identified."""
    instance = Confumo.get_instance()
    assert instance._get_platform_name() == platform.system(), "Platform name mismatch"


def test_default_config_dir():
    """Test that the default config directory is correct based on the platform."""
    instance = Confumo.get_instance()
    platform_name = instance._get_platform_name()

    if platform_name == 'Darwin':
        expected_path = os.path.expanduser("~/Library/Application Support")
    elif platform_name == 'Linux':
        expected_path = os.path.expanduser("~/.config")
    elif platform_name == 'Windows':
        expected_path = os.getenv('LOCALAPPDATA')
        if not expected_path:
            with pytest.raises(ConfumoError, match="LOCALAPPDATA environment variable is not set on Windows"):
                instance._get_default_config_dir()
            return
    else:
        with pytest.raises(ConfumoError, match=f"Unsupported OS: {platform_name}"):
            instance._get_default_config_dir()
        return

    assert instance._get_default_config_dir() == expected_path, "Config directory mismatch"


def test_parse_args_default():
    """Test that default arguments are correctly parsed."""
    instance = Confumo.get_instance(additional_args=None)
    parsed_args = instance._parse_args(args=[])

    assert parsed_args.log_level == 'INFO', "Default log level should be INFO"
    assert parsed_args.config_dir == instance.config_dir, "Config dir should match default"


def test_parse_args_with_config():
    """Test that arguments are parsed when a configuration file is provided."""
    instance = Confumo.get_instance()
    args = ['--config', '/path/to/config.yaml', '--log_level', 'DEBUG']
    parsed_args = instance._parse_args(args)

    assert parsed_args.config == '/path/to/config.yaml', "Config path should match"
    assert parsed_args.log_level == 'DEBUG', "Log level should be DEBUG"


def test_initialize_configuration_without_file():
    """Test that the configuration is correctly initialized without a config file."""
    instance = Confumo.get_instance()
    config = instance._initialize_configuration()

    assert config['log_level'] == 'INFO', "Log level should default to INFO"
    assert config['app_name'] == instance.app_name, "App name should match"
    assert config['config_dir'] == instance.config_dir, "Config dir should match"


@mock.patch('builtins.open', new_callable=mock.mock_open, read_data="log_level: DEBUG\n")
def test_read_config_file(mock_open):
    """Test that the configuration is read correctly from a YAML file."""
    instance = Confumo.get_instance()
    config = instance._read_config_file('/path/to/config.yaml')

    mock_open.assert_called_once_with('/path/to/config.yaml', 'r')
    assert config['log_level'] == 'DEBUG', "Log level in the config file should be DEBUG"


@mock.patch('os.path.abspath')
@mock.patch('confumo.Confumo._is_cygwin', return_value=False)
def test_ensure_windows_path(mock_is_cygwin, mock_abspath):
    """Test that Windows path compatibility is ensured."""
    mock_abspath.return_value = '/absolute/path'
    instance = Confumo.get_instance()
    result = instance._ensure_windows_path('/some/path')

    mock_abspath.assert_called_once_with('/some/path')
    assert result == '/absolute/path', "Path should be converted to an absolute path"


@mock.patch('subprocess.run')
def test_cygwin_to_windows_path(mock_subprocess):
    """Test that Cygwin paths are correctly converted to Windows paths."""
    mock_subprocess.return_value.stdout = 'C:\\Windows\\Path\n'
    instance = Confumo.get_instance()
    result = instance._cygwin_to_windows_path('/cygwin/path')

    mock_subprocess.assert_called_once_with(['cygpath', '-w', '/cygwin/path'], capture_output=True, text=True)
    assert result == 'C:\\Windows\\Path', "Cygwin path should be converted to Windows path"


def test_copy_confumo():
    """Test that deep copying a Confumo instance works correctly."""
    instance = Confumo.get_instance()
    copied_instance = instance.copy()

    assert copied_instance is not instance, "Copied instance should not be the same object"
    assert copied_instance.app_name == instance.app_name, "Copied instance should have the same app name"
    assert copied_instance.config == instance.config, "Copied instance should have the same config"


def test_getattr_with_config_value():
    """Test that accessing config values as attributes works."""
    instance = Confumo.get_instance()
    instance.config['custom_value'] = 'test_value'

    assert instance.custom_value == 'test_value', "Should be able to access config values as attributes"


def test_getattr_with_missing_value():
    """Test that accessing a missing attribute raises an AttributeError."""
    instance = Confumo.get_instance()

    with pytest.raises(AttributeError, match="object has no attribute 'missing_attr'"):
        _ = instance.missing_attr


def test_repr():
    """Test the string representation of the Confumo instance."""
    instance = Confumo.get_instance()
    repr_str = repr(instance)

    assert f"<Confumo platform_name={instance.platform_name}, config_dir={instance.config_dir}>" in repr_str, \
        "String representation should include platform name and config dir"


@mock.patch('os.makedirs')
@mock.patch('builtins.open', new_callable=mock.mock_open)
def test_save_config(mock_open, mock_makedirs):
    """Test that the configuration is saved to the correct YAML file."""
    instance = Confumo.get_instance(app_name="testapp")

    # Mock config directory and file saving
    instance.config_dir = os.path.join("/mock/config/dir")
    config_path = instance.save_config()

    # Ensure the config directory was created
    mock_makedirs.assert_called_once_with(instance.config_dir)

    # Ensure the file was opened and written to
    expected_path = os.path.join('/mock/config/dir', 'testapp_config.yaml')
    mock_open.assert_called_once_with(expected_path, 'w')

    # Verify the file path returned
    assert config_path == expected_path, "Config path mismatch"
