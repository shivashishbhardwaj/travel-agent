from agent.agent import process_claim


def _claim_with(expense, claim_id="TR-TEST-DUP", employee_id="EMP-300"):
    return {
        "claim_id": claim_id,
        "employee_id": employee_id,
        "trip_type": "DOMESTIC",
        "travel_start": "2026-08-20",
        "travel_end": "2026-08-20",
        "expenses": [expense],
    }


def test_duplicate_receipt_is_rejected_on_second_submission():
    expense = {"expense_id": "EXP-001", "category": "FLIGHT", "amount": 6000, "receipt_id": "REC-006"}

    first = process_claim(_claim_with(expense), employee_grade="G5")
    assert first["decision"] == "APPROVE"

    second = process_claim(_claim_with(expense), employee_grade="G5")
    assert second["decision"] == "REJECT"
    assert second["expense_decisions"][0]["reason"] == "Duplicate receipt"


def test_unsupported_category_is_rejected():
    expense = {"expense_id": "EXP-001", "category": "ENTERTAINMENT", "amount": 1000, "receipt_id": "REC-005"}

    result = process_claim(_claim_with(expense), employee_grade="G5")

    assert result["decision"] == "REJECT"
    assert result["expense_decisions"][0]["reason"] == "Unsupported expense category"
