"""Test basic project setup."""

import pytest
from network_investigator.core.schemas import NetworkQuery, ContextEnhancementDecision
from network_investigator.utils.helpers import extract_device_names, extract_time_references


def test_basic_imports():
    """Test that basic imports work."""
    from network_investigator.core import NetworkQuery, ContextEnhancementDecision
    assert NetworkQuery is not None
    assert ContextEnhancementDecision is not None


def test_network_query_creation():
    """Test NetworkQuery schema creation."""
    query = NetworkQuery(
        raw_query="Router X is down since 2 hours ago",
        devices_mentioned=["Router X"],
        timeframe_mentioned="2 hours ago",
        additional_remarks="Noticed high CPU before failure"
    )
    assert query.raw_query == "Router X is down since 2 hours ago"
    assert "Router X" in query.devices_mentioned


def test_device_extraction():
    """Test device name extraction utility."""
    text = "Router X and switch-core-01 are having issues"
    devices = extract_device_names(text)
    assert len(devices) > 0


def test_time_extraction():
    """Test time reference extraction."""
    text = "Issues started 2 hours ago at 14:30"
    time_refs = extract_time_references(text)
    assert len(time_refs) > 0


if __name__ == "__main__":
    pytest.main([__file__])