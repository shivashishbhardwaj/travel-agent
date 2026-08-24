"""
Claim submission API.

    uvicorn api.main:app --reload

Then POST to /v1/reimbursements with a claim body (see README for an example).
"""
import itertools
import os
import sys
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.agent import process_claim  # noqa: E402

app = FastAPI(title="Travel Reimbursement Agent API", version="1.0.0")
_claim_counter = itertools.count(1)


class Expense(BaseModel):
    category: str
    amount: float
    receipt_id: str
    expense_id: Optional[str] = None


class ClaimRequest(BaseModel):
    employee_id: str
    trip_type: str
    travel_start: str
    travel_end: str
    expenses: List[Expense]
    employee_grade: Optional[str] = "G5"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/reimbursements")
def submit_claim(claim: ClaimRequest):
    claim_dict = claim.dict()
    employee_grade = claim_dict.pop("employee_grade") or "G5"

    for i, expense in enumerate(claim_dict["expenses"], start=1):
        if not expense.get("expense_id"):
            expense["expense_id"] = f"EXP-{i:03d}"

    claim_dict["claim_id"] = f"TR-{10000 + next(_claim_counter)}"

    result = process_claim(claim_dict, employee_grade=employee_grade)

    return {
        "claim_id": result["claim_id"],
        "status": "PROCESSED",
        "decision": result["decision"],
        "claimed_amount": result["claimed_amount"],
        "approved_amount": result["approved_amount"],
        "rejected_amount": result["rejected_amount"],
        "manual_review": result["manual_review_required"],
    }
