"""
Policy retrieval tool.

This is a deterministic lookup, not an LLM call. In a production system this
would sit behind a RAG pipeline (see docs/deployment.md), but the contract is
the same either way: given a category and some context, return the policy
rule that applies, plus a citation the agent can quote back to the user.
"""
import json
from pathlib import Path

POLICY_PATH = Path(__file__).parent.parent / "policies" / "domestic_travel_policy.json"


def load_policy():
    with open(POLICY_PATH) as f:
        return json.load(f)


def retrieve_policy(category, travel_type="DOMESTIC", employee_grade=None, travel_date=None):
    """
    Returns the policy rule for a given expense category.

    Response shape mirrors the `retrieve_policy` tool contract in
    docs/tool-contracts.md: policy_id, rules, source citation, effective_from.
    """
    policy = load_policy()
    category_key = category.lower()
    rule = policy["rules"].get(category_key)

    if rule is None:
        return {
            "policy_id": policy["policy_id"],
            "rules": None,
            "source": None,
            "effective_from": policy["effective_from"],
        }

    return {
        "policy_id": policy["policy_id"],
        "rules": rule,
        "source": f"{policy['policy_id']}#{rule['section']}",
        "effective_from": policy["effective_from"],
    }


def high_value_threshold():
    return load_policy()["high_value_threshold"]
