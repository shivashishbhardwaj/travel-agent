"""
Tools the agent can call. Each one has a single, narrow job and none of them
involve the LLM - that's the point. `validate_receipt`, `check_duplicate`, and
`get_approval_matrix` are the deterministic building blocks the orchestrator
composes.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RECEIPTS_PATH = DATA_DIR / "receipts.json"
APPROVAL_MATRIX_PATH = Path(__file__).parent.parent / "policies" / "approval_matrix.json"

# In-memory ledger of (employee_id, receipt_id, amount) tuples already seen in
# this process. A real implementation would back this with a database lookup
# (see docs/deployment.md) - this is enough to demonstrate the duplicate-check
# tool contract without standing up infrastructure.
_seen_receipts = set()


def _load_receipts():
    with open(RECEIPTS_PATH) as f:
        return json.load(f)


def validate_receipt(receipt_id):
    """Returns extracted receipt evidence, or valid=False if not found."""
    receipts = _load_receipts()
    receipt = receipts.get(receipt_id)
    if receipt is None:
        return {"valid": False, "reason": "Receipt not found or not yet extracted"}
    return {"valid": True, **receipt}


def check_duplicate(employee_id, receipt_id, amount):
    """Flags a receipt as duplicate if this employee has already claimed it."""
    key = (employee_id, receipt_id, amount)
    if key in _seen_receipts:
        return {"duplicate": True}
    _seen_receipts.add(key)
    return {"duplicate": False}


def reset_duplicate_ledger():
    """Test helper - clears the in-memory duplicate ledger between test cases."""
    _seen_receipts.clear()


def get_approval_matrix(employee_grade):
    with open(APPROVAL_MATRIX_PATH) as f:
        matrix = json.load(f)
    return matrix["grades"].get(employee_grade, matrix["grades"]["G5"])
