import json
from pathlib import Path

from agent.agent import process_claim


def test_partial_approval_sample_claim():
    claims_path = Path(__file__).parent.parent / "data" / "claims.json"
    with open(claims_path) as f:
        claim = json.load(f)[0]

    result = process_claim(claim, employee_grade=claim.get("employee_grade", "G5"))

    assert result["decision"] == "PARTIALLY_APPROVE"
    assert result["claimed_amount"] == 19200
    assert result["approved_amount"] == 15100
    assert result["rejected_amount"] == 4100
    assert result["manual_review_required"] is False

    hotel_line = next(e for e in result["expense_decisions"] if e["category"] == "HOTEL")
    assert hotel_line["decision"] == "PARTIAL"
    assert hotel_line["approved"] == 5000
