import pytest
from heroku_applink.context import AppLinkContext

def test_context_initialization():
    """Test that the context can be initialized."""
    context = AppLinkContext()
    assert context is not None

def test_context_attributes():
    """Test that context has the expected attributes."""
    context = AppLinkContext()
    # Add assertions for expected attributes 