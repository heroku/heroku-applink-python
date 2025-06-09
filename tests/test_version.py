import pytest
from unittest.mock import patch, mock_open
import importlib.metadata

class TestGetVersion:
    """Test the _get_version() function and related version detection logic."""

    def setup_method(self):
        """Reset the cached version before each test."""
        # Import here to avoid circular imports during test collection
        import heroku_applink
        heroku_applink._version = None

    def test_get_version_from_importlib_metadata(self):
        """Test successful version retrieval from importlib.metadata."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.return_value = "1.2.3"

            from heroku_applink import _get_version
            result = _get_version()

            assert result == "1.2.3"
            mock_version.assert_called_once_with("heroku_applink")

    def test_get_version_caching(self):
        """Test that version is cached after first call."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.return_value = "1.2.3"

            from heroku_applink import _get_version

            # First call
            result1 = _get_version()
            assert result1 == "1.2.3"

            # Second call should use cached value
            result2 = _get_version()
            assert result2 == "1.2.3"

            # importlib.metadata.version should only be called once
            mock_version.assert_called_once_with("heroku_applink")

    def test_get_version_fallback_to_pyproject_toml(self):
        """Test fallback to pyproject.toml when importlib.metadata fails."""
        pyproject_content = b"""
[project]
name = "heroku_applink"
version = "2.0.0"
description = "Test package"
"""

        with patch('importlib.metadata.version') as mock_version, \
             patch('builtins.open', mock_open(read_data=pyproject_content)), \
             patch('tomllib.load') as mock_tomllib:

            # Make importlib.metadata fail
            mock_version.side_effect = importlib.metadata.PackageNotFoundError("heroku_applink")

            # Mock tomllib.load return value
            mock_tomllib.return_value = {
                "project": {
                    "version": "2.0.0"
                }
            }

            from heroku_applink import _get_version
            result = _get_version()

            assert result == "2.0.0"
            mock_version.assert_called_once_with("heroku_applink")
            mock_tomllib.assert_called_once()

    def test_get_version_fallback_to_unknown(self):
        """Test fallback to 'unknown' when both methods fail."""
        with patch('importlib.metadata.version') as mock_version, \
             patch('builtins.open') as mock_open_file:

            # Make importlib.metadata fail
            mock_version.side_effect = importlib.metadata.PackageNotFoundError("heroku_applink")

            # Make file opening fail
            mock_open_file.side_effect = FileNotFoundError("pyproject.toml not found")

            from heroku_applink import _get_version
            result = _get_version()

            assert result == "unknown"
            mock_version.assert_called_once_with("heroku_applink")

    def test_get_version_tomllib_parse_error(self):
        """Test fallback to 'unknown' when pyproject.toml exists but can't be parsed."""
        with patch('importlib.metadata.version') as mock_version, \
             patch('builtins.open', mock_open(read_data=b"invalid toml")), \
             patch('tomllib.load') as mock_tomllib:

            # Make importlib.metadata fail
            mock_version.side_effect = importlib.metadata.PackageNotFoundError("heroku_applink")

            # Make tomllib.load fail
            mock_tomllib.side_effect = Exception("Invalid TOML")

            from heroku_applink import _get_version
            result = _get_version()

            assert result == "unknown"
            mock_version.assert_called_once_with("heroku_applink")
            mock_tomllib.assert_called_once()

    def test_get_version_missing_version_in_pyproject(self):
        """Test fallback to 'unknown' when pyproject.toml doesn't have version field."""
        pyproject_content = b"""
[project]
name = "heroku_applink"
description = "Test package"
"""

        with patch('importlib.metadata.version') as mock_version, \
             patch('builtins.open', mock_open(read_data=pyproject_content)), \
             patch('tomllib.load') as mock_tomllib:

            # Make importlib.metadata fail
            mock_version.side_effect = importlib.metadata.PackageNotFoundError("heroku_applink")

            # Mock tomllib.load to return content without version
            mock_tomllib.return_value = {
                "project": {
                    "name": "heroku_applink"
                }
            }

            from heroku_applink import _get_version
            result = _get_version()

            assert result == "unknown"
            mock_version.assert_called_once_with("heroku_applink")
            mock_tomllib.assert_called_once()

    def test_get_version_keyerror_missing_project_section(self):
        """Test fallback to 'unknown' when pyproject.toml doesn't have project section."""
        pyproject_content = b"""
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

        with patch('importlib.metadata.version') as mock_version, \
             patch('builtins.open', mock_open(read_data=pyproject_content)), \
             patch('tomllib.load') as mock_tomllib:

            # Make importlib.metadata fail
            mock_version.side_effect = importlib.metadata.PackageNotFoundError("heroku_applink")

            # Mock tomllib.load to return content without project section
            mock_tomllib.return_value = {
                "build-system": {
                    "requires": ["hatchling"]
                }
            }

            from heroku_applink import _get_version
            result = _get_version()

            assert result == "unknown"
            mock_version.assert_called_once_with("heroku_applink")
            mock_tomllib.assert_called_once()

    def test_version_lazy_loading_via_getattr(self):
        """Test that __version__ is lazily loaded via module __getattr__."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.return_value = "3.0.0"

            # Import the module but don't access __version__ yet
            import heroku_applink

            # Version should not be computed yet
            mock_version.assert_not_called()

            # Access __version__ - should trigger lazy loading
            version = heroku_applink.__version__

            assert version == "3.0.0"
            mock_version.assert_called_once_with("heroku_applink")

    def test_getattr_unknown_attribute(self):
        """Test that __getattr__ raises AttributeError for unknown attributes."""
        import heroku_applink

        with pytest.raises(AttributeError, match="module 'heroku_applink' has no attribute 'nonexistent'"):
            _ = heroku_applink.nonexistent

    def test_version_accessed_multiple_times_uses_cache(self):
        """Test that accessing __version__ multiple times uses cached value."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.return_value = "4.0.0"

            import heroku_applink

            # Access __version__ multiple times
            version1 = heroku_applink.__version__
            version2 = heroku_applink.__version__
            version3 = heroku_applink.__version__

            assert version1 == "4.0.0"
            assert version2 == "4.0.0"
            assert version3 == "4.0.0"

            # Should only call the underlying function once due to caching
            mock_version.assert_called_once_with("heroku_applink")


