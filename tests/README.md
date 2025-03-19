# Unit Tests for UNS-MCP

This directory contains unit tests for the Unstructured API MCP Server components.

## Running Tests

To run the tests, you'll need pytest and pytest-asyncio installed. If you don't have them already, you can install them with:

```bash
pip install pytest pytest-asyncio
```

### Running All Tests

From the project root directory, run:

```bash
pytest
```

### Running Specific Test Files

To run tests from a specific file:

```bash
pytest tests/connectors/source/test_firecrawl.py
```

### Running Specific Test Classes or Methods

To run a specific test class:

```bash
pytest tests/connectors/source/test_firecrawl.py::TestEnsureValidS3Uri
```

To run a specific test method:

```bash
pytest tests/connectors/source/test_firecrawl.py::TestEnsureValidS3Uri::test_valid_s3_uri
```

## Test Structure

The tests follow a structure that mirrors the project's structure:

- `tests/conftest.py` - Contains common fixtures and setup for all tests
- `tests/connectors/source/` - Tests for source connectors (e.g., firecrawl, s3)

## Mocking

Many tests use unittest.mock to mock external dependencies like boto3, FirecrawlApp, and external API calls.
This allows testing the components in isolation without actually calling external services.

## Environment Variables

Some tests require environment variables to be set. The `mock_environment` fixture in `conftest.py` handles this 
by setting test values for these variables during tests and restoring the original values afterward. 