"""
Turns per-expense calculator results into a per-expense decision, and rolls
per-expense decisions up into a single claim-level decision.
"""


def build_expense_decision(expense, calc_result, policy_source):
    claimed = expense["amount"]
    approved = calc_result["approved_amount"]

    if approved == 0 and calc_result.get("reason"):
        decision = "REJECT"
        reason = calc_result["reason"]
    elif approved < claimed:
        decision = "PARTIAL"
        reason = f"Exceeds policy limit of {calc_result.get('policy_limit')}"
    else:
        decision = "APPROVE"
        reason = "Within policy limit"

    return {
        "expense_id": expense["expense_id"],
        "category": expense["category"],
        "claimed": claimed,
        "approved": approved,
        "decision": decision,
        "reason": reason,
        "policy_reference": policy_source,
    }


def manual_review_expense(expense, reason):
    return {
        "expense_id": expense["expense_id"],
        "category": expense["category"],
        "claimed": expense["amount"],
        "approved": 0,
        "decision": "MANUAL_REVIEW",
        "reason": reason,
        "policy_reference": None,
    }


def reject_expense(expense, reason, policy_source=None):
    return {
        "expense_id": expense["expense_id"],
        "category": expense["category"],
        "claimed": expense["amount"],
        "approved": 0,
        "decision": "REJECT",
        "reason": reason,
        "policy_reference": policy_source,
    }


def aggregate_results(claim_id, expense_decisions, currency="INR"):
    claimed_total = sum(e["claimed"] for e in expense_decisions)
    approved_total = sum(e["approved"] for e in expense_decisions)
    rejected_total = claimed_total - approved_total

    if approved_total == claimed_total and claimed_total > 0:
        decision = "APPROVE"
    elif approved_total == 0:
        decision = "REJECT"
    else:
        decision = "PARTIALLY_APPROVE"

    return {
        "claim_id": claim_id,
        "decision": decision,
        "claimed_amount": claimed_total,
        "approved_amount": approved_total,
        "rejected_amount": rejected_total,
        "currency": currency,
        "expense_decisions": expense_decisions,
    }


def policy_references(expense_decisions):
    seen = set()
    refs = []
    for e in expense_decisions:
        ref = e.get("policy_reference")
        if ref and ref not in seen:
            seen.add(ref)
            refs.append({"policy_id": ref.split("#")[0], "reference": ref})
    return refs


def overall_confidence(expense_decisions):
    if not expense_decisions:
        return 0.0
    scores = [0.5 if e["decision"] == "MANUAL_REVIEW" else 0.99 for e in expense_decisions]
    return round(sum(scores) / len(scores), 2)
