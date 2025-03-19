import pytest
import sys
import os
from pathlib import Path

# Add the project root to the Python path so that imports work correctly in tests
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, project_root)

# Define common fixtures here
@pytest.fixture
def mock_environment():
    """Fixture to set up environment variables for testing."""
    original_env = os.environ.copy()
    test_env = {
        "FIRECRAWL_API_KEY": "test-api-key",
        "AWS_KEY": "test-aws-key",
        "AWS_SECRET": "test-aws-secret"
    }
    
    # Add the test environment variables
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env) 