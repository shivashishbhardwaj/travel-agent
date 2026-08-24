"""
TravelReimbursementAgent - the single orchestrator described in
docs/architecture.md.

It decides which tool to call and in what order, but it never computes a
reimbursement amount itself. That job belongs entirely to calculator.py.

Manual-review triggers are explicit and named (see MANUAL_REVIEW_REASONS
below) rather than driven by a single opaque confidence threshold.
"""
from . import calculator
from . import decision as decision_engine
from . import policy as policy_tool
from . import tools

OCR_CONFIDENCE_THRESHOLD = 0.90
HIGH_VALUE_THRESHOLD = 50000


def process_claim(claim, employee_grade="G5"):
    trace = []

    if not claim.get("travel_start") or not claim.get("travel_end"):
        return _manual_review_claim(claim, "Missing travel dates", trace)

    expense_decisions = []

    for expense in claim["expenses"]:
        category = expense["category"].lower()

        trace.append(f"RETRIEVE_POLICY category={expense['category']}")
        policy_result = policy_tool.retrieve_policy(expense["category"], employee_grade=employee_grade)

        if policy_result["rules"] is None:
            expense_decisions.append(
                decision_engine.reject_expense(expense, "Unsupported expense category")
            )
            continue

        trace.append(f"VALIDATE_RECEIPT receipt={expense['receipt_id']}")
        receipt = tools.validate_receipt(expense["receipt_id"])

        if not receipt["valid"]:
            expense_decisions.append(
                decision_engine.manual_review_expense(expense, "Missing or invalid receipt")
            )
            continue

        confidence = receipt.get("confidence", 1.0)
        if confidence < OCR_CONFIDENCE_THRESHOLD:
            expense_decisions.append(
                decision_engine.manual_review_expense(
                    expense, f"OCR confidence {confidence:.2f} below required {OCR_CONFIDENCE_THRESHOLD}"
                )
            )
            continue

        if category == "flight" and receipt.get("fare_class", "ECONOMY").upper() != "ECONOMY":
            expense_decisions.append(
                decision_engine.manual_review_expense(expense, "Business-class flight requires manual review")
            )
            continue

        trace.append(f"CHECK_DUPLICATE receipt={expense['receipt_id']}")
        dup = tools.check_duplicate(claim["employee_id"], expense["receipt_id"], expense["amount"])
        if dup["duplicate"]:
            expense_decisions.append(
                decision_engine.reject_expense(expense, "Duplicate receipt", policy_result["source"])
            )
            continue

        calc = calculator.calculate_reimbursement(
            category, expense["amount"], policy_result["rules"]
        )
        trace.append(f"CALCULATE claimed={expense['amount']} eligible={calc['approved_amount']}")

        expense_decisions.append(
            decision_engine.build_expense_decision(expense, calc, policy_result["source"])
        )

    result = decision_engine.aggregate_results(claim["claim_id"], expense_decisions)

    manual_reasons = [
        e["reason"] for e in expense_decisions if e["decision"] == "MANUAL_REVIEW"
    ]
    if result["claimed_amount"] > HIGH_VALUE_THRESHOLD:
        manual_reasons.append(f"High-value claim exceeds {HIGH_VALUE_THRESHOLD}")

    result["manual_review_required"] = bool(manual_reasons)
    if manual_reasons:
        result["decision"] = "MANUAL_REVIEW"
        result["manual_review_reasons"] = manual_reasons

    result["confidence"] = decision_engine.overall_confidence(expense_decisions)
    result["policy_references"] = decision_engine.policy_references(expense_decisions)
    result["trace"] = trace

    return result


def _manual_review_claim(claim, reason, trace):
    claimed_total = sum(e["amount"] for e in claim.get("expenses", []))
    return {
        "claim_id": claim.get("claim_id", "UNKNOWN"),
        "decision": "MANUAL_REVIEW",
        "claimed_amount": claimed_total,
        "approved_amount": 0,
        "rejected_amount": 0,
        "currency": "INR",
        "confidence": 0.0,
        "expense_decisions": [],
        "policy_references": [],
        "manual_review_required": True,
        "manual_review_reasons": [reason],
        "trace": trace,
    }
