from agent.agent import process_claim


def _claim(claim_id, employee_id, expense, travel_start="2026-08-21", travel_end="2026-08-21"):
    return {
        "claim_id": claim_id,
        "employee_id": employee_id,
        "trip_type": "DOMESTIC",
        "travel_start": travel_start,
        "travel_end": travel_end,
        "expenses": [expense],
    }


def test_missing_receipt_triggers_manual_review():
    expense = {"expense_id": "EXP-001", "category": "MEAL", "amount": 500, "receipt_id": "REC-999"}

    result = process_claim(_claim("TR-TEST-MISSING", "EMP-400", expense), employee_grade="G5")

    assert result["decision"] == "MANUAL_REVIEW"
    assert result["manual_review_required"] is True


def test_business_class_flight_triggers_manual_review():
    expense = {"expense_id": "EXP-001", "category": "FLIGHT", "amount": 25000, "receipt_id": "REC-007"}

    result = process_claim(_claim("TR-TEST-BIZ", "EMP-401", expense), employee_grade="G5")

    assert result["manual_review_required"] is True
    assert any("Business-class" in r for r in result["manual_review_reasons"])


def test_low_ocr_confidence_triggers_manual_review():
    expense = {"expense_id": "EXP-001", "category": "MEAL", "amount": 1500, "receipt_id": "REC-008"}

    result = process_claim(_claim("TR-TEST-OCR", "EMP-402", expense), employee_grade="G5")

    assert result["manual_review_required"] is True


def test_high_value_claim_triggers_manual_review():
    expense = {"expense_id": "EXP-001", "category": "HOTEL", "amount": 60000, "receipt_id": "REC-009"}

    result = process_claim(
        _claim("TR-TEST-HIGH", "EMP-403", expense, travel_start="2026-08-23", travel_end="2026-08-25"),
        employee_grade="G5",
    )

    assert result["manual_review_required"] is True
    assert any("High-value" in r for r in result["manual_review_reasons"])


def test_missing_travel_dates_triggers_manual_review():
    claim = {
        "claim_id": "TR-TEST-NODATES",
        "employee_id": "EMP-404",
        "trip_type": "DOMESTIC",
        "travel_start": "",
        "travel_end": "",
        "expenses": [{"expense_id": "EXP-001", "category": "TAXI", "amount": 500, "receipt_id": "REC-005"}],
    }

    result = process_claim(claim, employee_grade="G5")

    assert result["decision"] == "MANUAL_REVIEW"
    assert result["manual_review_reasons"] == ["Missing travel dates"]
