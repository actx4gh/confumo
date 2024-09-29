import pytest
import os
import tempfile

@pytest.fixture(scope="session")
def temp_dir():
    """
    Create a temporary directory for use in tests.
    
    The directory is automatically removed after the test session is done.
    """
    dirpath = tempfile.mkdtemp()
    yield dirpath
    os.rmdir(dirpath)

@pytest.fixture(scope="session")
def setup_environment():
    """
    Set up any environment variables or configurations needed for the tests.
    
    This fixture runs once per test session.
    """
    os.environ['APP_ENV'] = 'test'
    yield
    # Cleanup environment variables after test session
    del os.environ['APP_ENV']

