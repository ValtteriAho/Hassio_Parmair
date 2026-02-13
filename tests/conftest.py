"""Pytest configuration and fixtures for Parmair integration tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from tools.mock_coordinator import MockCoordinator, load_dump  # noqa: E402

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def discover_fixture_files() -> list[Path]:
    """Discover all JSON fixture files in the fixtures directory."""
    if not FIXTURES_DIR.exists():
        return []
    return sorted(FIXTURES_DIR.glob("*.json"))


def get_fixture_ids() -> list[str]:
    """Get human-readable IDs for fixture files."""
    return [f.stem for f in discover_fixture_files()]


# Parametrize helper for fixture files
FIXTURE_FILES = discover_fixture_files()
FIXTURE_IDS = get_fixture_ids()


@pytest.fixture(params=FIXTURE_FILES, ids=FIXTURE_IDS)
def fixture_file(request: pytest.FixtureRequest) -> Path:
    """Parametrized fixture that yields each fixture file path."""
    return request.param


@pytest.fixture
def coordinator(fixture_file: Path) -> MockCoordinator:
    """Create a MockCoordinator from a fixture file."""
    return load_dump(fixture_file)


@pytest.fixture
def fixture_data(fixture_file: Path) -> dict[str, Any]:
    """Load raw fixture data as a dictionary."""
    with open(fixture_file, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def fixture_metadata(fixture_data: dict[str, Any]) -> dict[str, Any]:
    """Extract metadata from fixture data."""
    return fixture_data.get("metadata", {})


@pytest.fixture
def fixture_registers(fixture_data: dict[str, Any]) -> dict[str, Any]:
    """Extract registers from fixture data."""
    return fixture_data.get("registers", {})


# Single coordinator fixtures for specific machine types (useful for targeted tests)
@pytest.fixture
def mac120_v2_coordinator() -> MockCoordinator | None:
    """Load the MAC120 V2 fixture if available."""
    fixture_path = FIXTURES_DIR / "MAC120-full-v2.json"
    if fixture_path.exists():
        return load_dump(fixture_path)
    pytest.skip("MAC120-full-v2.json fixture not available")
    return None


# Helper fixtures for version detection
@pytest.fixture
def is_v2_device(coordinator: MockCoordinator) -> bool:
    """Check if the current fixture is a V2.x device."""
    sw_ver = coordinator.data.get("software_version", 0)
    return sw_ver >= 2.0 if isinstance(sw_ver, int | float) else False


# Collect all fixture files at module load time for test discovery
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:  # noqa: ARG001
    """Skip tests if no fixture files are available."""
    if not FIXTURE_FILES:
        skip_marker = pytest.mark.skip(reason="No fixture files found in tests/fixtures/")
        for item in items:
            # Skip parametrized tests that depend on fixtures
            if "fixture_file" in item.fixturenames or "coordinator" in item.fixturenames:
                item.add_marker(skip_marker)


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "v1_only: mark test to run only on V1.x devices")
    config.addinivalue_line("markers", "v2_only: mark test to run only on V2.x devices")
