import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest  # noqa: E402
from agent import tools  # noqa: E402


@pytest.fixture(autouse=True)
def reset_duplicate_ledger():
    tools.reset_duplicate_ledger()
    yield
