import pytest
import sys
import json
import urllib.request
import subprocess
import os
from pathlib import Path
import importlib.metadata
import tempfile
import shutil

def get_latest_version(pypi_type="testpypi"):
    """Get the latest version from PyPI or TestPyPI."""
    package_name = "heroku_applink"
    base_url = "https://test.pypi.org" if pypi_type == "testpypi" else "https://pypi.org"
    url = f"{base_url}/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            versions = sorted(data["releases"].keys())
            return versions[-1] if versions else None
    except Exception as e:
        print(f"Error fetching versions from {pypi_type}: {e}")
        return None

def test_latest_package():
    """Test that the latest package from PyPI/TestPyPI works as expected."""
    pypi_type = os.getenv("PYPI_TYPE", "testpypi")
    version = get_latest_version(pypi_type)
    if not version:
        pytest.skip(f"No versions found on {pypi_type}")
    
    print(f"\nTesting version {version} from {pypi_type}")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Install the package using pip (simulating user installation)
            print(f"Installing package version {version} from {pypi_type}...")
            base_url = "https://test.pypi.org/simple/" if pypi_type == "testpypi" else "https://pypi.org/simple/"
            extra_url = "https://pypi.org/simple/" if pypi_type == "testpypi" else "https://test.pypi.org/simple/"
            
            subprocess.run([
                sys.executable,
                "-m",
                "pip",
                "install",
                "--index-url",
                base_url,
                "--extra-index-url",
                extra_url,
                f"heroku_applink=={version}"
            ], check=True, capture_output=True)

            # Test package metadata
            print("\nChecking package metadata...")
            dist = importlib.metadata.distribution("heroku_applink")
            installed_version = dist.version
            assert installed_version == version, f"Installed version {installed_version} doesn't match expected version {version}"
            
            # Test package dependencies
            print("\nChecking package dependencies...")
            requires = [str(r) for r in dist.requires]
            print(f"Package requires: {requires}")
            
            # Test package functionality in a clean environment
            print("\nTesting package functionality...")
            test_code = """
import heroku_applink
from heroku_applink.data_api import DataAPI, Record, UnitOfWork

# Test required classes exist
assert hasattr(heroku_applink.data_api, 'DataAPI'), "DataAPI class missing"
assert hasattr(heroku_applink.data_api, 'Record'), "Record class missing"
assert hasattr(heroku_applink.data_api, 'UnitOfWork'), "UnitOfWork class missing"

# Test DataAPI methods
assert hasattr(DataAPI, 'query'), "DataAPI.query method missing"
assert hasattr(DataAPI, 'commit_unit_of_work'), "DataAPI.commit_unit_of_work method missing"

# Test Record functionality
record = Record(type="Account", fields={"Name": "Test"})
assert record.type == "Account", "Record.type not set correctly"
assert record.fields == {"Name": "Test"}, "Record.fields not set correctly"

# Test UnitOfWork functionality
uow = UnitOfWork()
assert hasattr(uow, 'register_create'), "UnitOfWork.register_create method missing"
assert hasattr(uow, 'register_update'), "UnitOfWork.register_update method missing"
assert hasattr(uow, 'register_delete'), "UnitOfWork.register_delete method missing"

# Test method signatures
import inspect
query_sig = inspect.signature(DataAPI.query)
assert 'soql' in query_sig.parameters, "DataAPI.query missing 'soql' parameter"

commit_sig = inspect.signature(DataAPI.commit_unit_of_work)
assert 'unit_of_work' in commit_sig.parameters, "DataAPI.commit_unit_of_work missing 'unit_of_work' parameter"
"""
            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True,
                text=True,
                check=False
            )
            assert result.returncode == 0, f"Tests failed for version {version}:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            print("Functionality tests passed!")
            
            # Test package can be imported in a new Python process
            print("\nTesting package import in new process...")
            import_result = subprocess.run(
                [sys.executable, "-c", "import heroku_applink; print('Import successful')"],
                capture_output=True,
                text=True,
                check=False
            )
            assert import_result.returncode == 0, f"Package import failed:\nstdout: {import_result.stdout}\nstderr: {import_result.stderr}"
            print("Import test passed!")
            
            # Run the package's test suite
            print("\nRunning package test suite...")
            
            # Copy tests from current directory
            tests_dir = os.path.join(os.path.dirname(__file__))
            shutil.copytree(tests_dir, os.path.join(temp_dir, "tests"))
            
            # Install test dependencies
            subprocess.run([
                sys.executable,
                "-m",
                "pip",
                "install",
                "pytest>=8.0.0",
                "pytest-cov>=4.1.0",
                "pytest-asyncio>=0.21.0"
            ], check=True, capture_output=True)
            
            # Run the tests
            test_result = subprocess.run(
                [sys.executable, "-m", "pytest", os.path.join(temp_dir, "tests"), "-v"],
                capture_output=True,
                text=True,
                check=False
            )
            assert test_result.returncode == 0, f"Package test suite failed:\nstdout: {test_result.stdout}\nstderr: {test_result.stderr}"
            print("Package test suite passed!")
            
        finally:
            # Uninstall the package
            print("\nCleaning up...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "heroku_applink"], check=True)
