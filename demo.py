"""
Run with: python demo.py

Loads the sample claim (TR-10045) from data/claims.json, runs it through the
agent, and prints the decision the way it would show up in an architecture
review demo.
"""
import json
from pathlib import Path

from agent.agent import process_claim

SYMBOLS = {"APPROVE": "\u2713", "PARTIAL": "\u26a0", "REJECT": "\u2717", "MANUAL_REVIEW": "?"}


def main():
    claims_path = Path(__file__).parent / "data" / "claims.json"
    with open(claims_path) as f:
        claims = json.load(f)

    claim = claims[0]
    result = process_claim(claim, employee_grade=claim.get("employee_grade", "G5"))

    print("=" * 48)
    print("Travel Reimbursement Approval Agent")
    print("=" * 48)
    print(f"Claim ID: {result['claim_id']}")
    print(f"Claimed Amount: \u20b9{result['claimed_amount']:,}")
    print(f"Approved Amount: \u20b9{result['approved_amount']:,}")
    print(f"Rejected Amount: \u20b9{result['rejected_amount']:,}")
    print(f"Decision: {result['decision']}")
    print()
    print("Evidence:")
    for e in result["expense_decisions"]:
        symbol = SYMBOLS.get(e["decision"], "-")
        print(f"{symbol} {e['category'].title()}: {e['reason']}")
    print()

    if result["policy_references"]:
        policy_id = result["policy_references"][0]["policy_id"]
        sections = ", ".join(r["reference"].split("#")[1] for r in result["policy_references"])
        print(f"Policy: {policy_id}")
        print(f"Sections: {sections}")

    print(f"Manual Review: {'YES' if result['manual_review_required'] else 'NO'}")
    print(f"Confidence: {result['confidence']}")
    print("=" * 48)


if __name__ == "__main__":
    main()
