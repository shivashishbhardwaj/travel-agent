from agent.agent import process_claim


def test_fully_approved_claim():
    claim = {
        "claim_id": "TR-TEST-APPROVE",
        "employee_id": "EMP-200",
        "trip_type": "DOMESTIC",
        "travel_start": "2026-08-15",
        "travel_end": "2026-08-15",
        "expenses": [
            {"expense_id": "EXP-001", "category": "TAXI", "amount": 500, "receipt_id": "REC-005"},
        ],
    }

    result = process_claim(claim, employee_grade="G5")

    assert result["decision"] == "APPROVE"
    assert result["approved_amount"] == 500
    assert result["rejected_amount"] == 0
    assert result["manual_review_required"] is False
