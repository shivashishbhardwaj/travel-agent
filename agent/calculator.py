"""
The reimbursement calculator. This is the single most important file in the
project: the LLM is never allowed to produce the approved/rejected amounts
directly. It calls this function and reports the result.
"""


def calculate_reimbursement(category, claimed_amount, policy_rules):
    """
    Given a claimed amount and the policy rule for its category, returns the
    deterministic eligible amount.

    Mirrors the `calculate_reimbursement` tool contract: input is
    (category, claimed_amount, policy_limit-bearing rules), output is
    (approved_amount, rejected_amount).

    Note: hotel and meal expense lines are evaluated directly against the
    per-night / per-day cap (each line represents a single night or day's
    spend). A production system would instead pass in the itemized
    per-night/per-day amounts already split out by the extraction step.
    """
    category = category.lower()

    if policy_rules is None:
        return {
            "approved_amount": 0,
            "rejected_amount": claimed_amount,
            "policy_limit": 0,
            "reason": "Unsupported expense category",
        }

    if category == "hotel":
        limit = policy_rules["max_per_night"]
    elif category == "meal":
        limit = policy_rules["max_per_day"]
    elif category == "flight":
        limit = policy_rules["max_amount"]
    elif category == "taxi":
        limit = policy_rules["max_per_trip"]
    else:
        limit = claimed_amount

    approved = min(claimed_amount, limit)
    rejected = max(0, claimed_amount - limit)

    return {"approved_amount": approved, "rejected_amount": rejected, "policy_limit": limit}
