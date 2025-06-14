# Testing Documentation for VETA

This document describes the comprehensive testing setup for the VETA (Textual Emotion Assessment) package.

## 🧪 Test Suite Overview

The test suite includes:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows and component interactions
- **Coverage Reporting**: Measure test coverage across the codebase
- **Performance Tests**: Benchmark critical operations

## 📁 Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                   # Shared fixtures and configuration
├── test_wordlist.py             # Wordlist class tests
├── test_item.py                 # Item class tests
├── test_respondent.py           # Respondent class tests
├── test_survey.py               # Survey class tests
├── test_scoring_module.py       # Base scoring module tests
├── test_auto_self_other_item.py # Auto classification tests
├── test_integration.py          # End-to-end integration tests
├── test_scoring_modules_extended.py # Extended scoring tests
└── scoring_modules/
    ├── __init__.py
    ├── test_count.py            # Count scoring module tests
    └── test_allsum.py           # Allsum scoring module tests
```

## 🏃‍♂️ Running Tests

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Or use pytest directly
pytest
```

### Advanced Usage

```bash
# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_wordlist.py

# Run specific test method
pytest tests/test_wordlist.py::TestWordlist::test_init_with_xlsx_file

# Run tests with coverage
pytest --cov=veta --cov-report=html

# Run only unit tests (excluding integration/slow tests)
pytest -m "not integration and not slow"

# Run only integration tests
pytest -m integration

# Run tests in parallel (if pytest-xdist installed)
pytest -n auto
```

## 📊 Coverage Reporting

The test suite generates multiple coverage reports:

1. **Terminal Output**: Shows coverage summary in terminal
2. **HTML Report**: Detailed coverage report in `htmlcov/index.html`
3. **XML Report**: Machine-readable coverage data in `coverage.xml`

### Coverage Goals
- **Target**: 80% minimum coverage (enforced by pytest)
- **Current Status**: Run `pytest --cov=veta` to see current coverage
- **Focus Areas**: Core functionality should have >90% coverage

## 🏷️ Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, full workflows)
- `@pytest.mark.slow` - Tests that take significant time
- `@pytest.mark.scoring` - Tests related to scoring modules
- `@pytest.mark.wordlist` - Tests related to wordlist functionality
- `@pytest.mark.survey` - Tests related to survey functionality

### Using Markers

```bash
# Run only fast unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run scoring-related tests only
pytest -m scoring
```

## 🔧 Test Configuration

### pytest.ini
The `pytest.ini` file contains:
- Coverage settings and thresholds
- Test discovery patterns
- Warning filters
- Logging configuration
- Marker definitions

### conftest.py
Shared fixtures include:
- `sample_wordlist_data` - Test wordlist data
- `sample_wordlist_file` - Temporary Excel wordlist file
- `wordlist_instance` - Configured Wordlist object
- `sample_item` - Test Item object
- `sample_respondent` - Test Respondent object
- `sample_survey` - Test Survey object
- `sample_survey_data` - Test survey data matrix

## 📈 Test Coverage by Module

| Module | Coverage Target | Key Test Areas |
|--------|----------------|----------------|
| `wordlist.py` | 95% | File loading, data validation, cleaning |
| `item.py` | 95% | Text processing, scoring storage |
| `respondent.py` | 90% | Item management, scoring aggregation |
| `survey.py` | 85% | Data processing, export functionality |
| `scoring_modules/` | 90% | Algorithm correctness, edge cases |
| `auto_self_other_item.py` | 80% | NLP processing, language detection |

## 🐛 Debugging Failed Tests

### Common Issues and Solutions

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **SpaCy Models Not Installed**
   ```bash
   python -m spacy download en_core_web_sm
   python -m spacy download de_core_news_sm
   ```

3. **File Path Issues**
   - Tests use temporary files and absolute paths
   - Check `tmp_path` fixture usage in failing tests

4. **Mock/Patch Issues**
   - Verify mock paths match actual import structure
   - Check that mocked methods return expected types

### Debugging Commands

```bash
# Run with detailed output and no capture
pytest -vvv -s tests/test_failing_module.py

# Drop into debugger on failure
pytest --pdb tests/test_failing_module.py

# Show local variables in tracebacks
pytest --tb=long tests/test_failing_module.py
```

## 📝 Writing New Tests

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestWordlist`)
- Test methods: `test_*` (e.g., `test_load_from_excel`)

### Test Structure Template
```python
import pytest
from unittest.mock import Mock, patch
from veta.module import ClassToTest

class TestClassName:
    """Test cases for ClassName"""
    
    def test_basic_functionality(self):
        """Test basic functionality with clear description"""
        # Arrange
        instance = ClassToTest()
        
        # Act
        result = instance.method()
        
        # Assert
        assert result == expected_value
    
    def test_edge_case(self):
        """Test edge case behavior"""
        # Test implementation
        pass
    
    @pytest.mark.slow
    def test_performance_case(self):
        """Test that might be slow"""
        # Implementation for time-consuming tests
        pass
```

### Using Fixtures
```python
def test_with_fixture(self, sample_wordlist_file):
    """Test using shared fixture"""
    wordlist = Wordlist(sample_wordlist_file)
    assert len(wordlist.words) > 0
```

### Mocking External Dependencies
```python
@patch('veta.module.external_dependency')
def test_with_mock(self, mock_dependency):
    """Test with mocked external dependency"""
    mock_dependency.return_value = "mocked_result"
    # Test implementation
```

## 🚀 Continuous Integration

### GitHub Actions (Recommended)
Create `.github/workflows/tests.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=veta --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

## 🔍 Test Maintenance

### Regular Tasks
1. **Update Coverage Targets**: Increase as code matures
2. **Review Slow Tests**: Optimize or mark appropriately
3. **Fixture Cleanup**: Remove unused fixtures
4. **Mock Updates**: Keep mocks in sync with real implementations
5. **Integration Test Expansion**: Add new workflow scenarios

### Performance Monitoring
```bash
# Benchmark tests (if pytest-benchmark installed)
pytest --benchmark-only

# Profile test execution time
pytest --durations=10
```
