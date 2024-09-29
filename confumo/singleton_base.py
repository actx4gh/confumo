# singleton_base.py

import abc
import sys


class SingletonBase(abc.ABC):
    """
    Abstract base class that provides singleton behavior and module-level attribute promotion.

    Subclasses should implement specific functionality related to configuration,
    argument parsing, platform detection, etc.
    """

    _instances = {}  # Class-level dictionary to hold singleton instances per subclass

    def __init__(self):
        """Initialize the BaseConfumo instance."""
        pass  # The base class doesn't need to initialize any attributes

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """
        Return or create a singleton instance per subclass.

        :return: Singleton instance of the subclass
        """
        if cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)
        return cls._instances[cls]

    def __repr__(self):
        """
        Return a string representation of the instance.

        :return: String representation
        """
        return f"<{self.__class__.__name__}>"

    @abc.abstractmethod
    def __getattr__(self, name):
        """
        Abstract method to allow access to attributes.

        Subclasses must implement this method to handle attribute access.

        :param name: Name of the attribute
        :return: Value of the attribute
        """
        pass

    def _setup_module_attributes(self):
        """
        Sets up module-level __getattr__ and __dir__ after the instance is initialized.

        This allows the instance's attributes to be accessed as if they were module-level attributes.
        """
        module = sys.modules[self.__class__.__module__]

        if not hasattr(module, '__getattr__'):
            def __getattr__(name):
                try:
                    return getattr(self, name)
                except AttributeError:
                    raise AttributeError(f"Module '{module.__name__}' has no attribute '{name}'")

            module.__getattr__ = __getattr__

        if not hasattr(module, '__dir__'):
            def __dir__():
                instance_attrs = dir(self)
                module_attrs = list(module.__dict__.keys())
                return sorted(set(instance_attrs + module_attrs))

            module.__dir__ = __dir__
