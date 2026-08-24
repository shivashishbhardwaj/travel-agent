# Travel Reimbursement Agent

A small, complete reference implementation of a GenAI-orchestrated, rules-backed
travel expense reimbursement system. The design principle behind it:

> The agent reasons and orchestrates. Tools and rules validate and calculate.
> The agent never invents policy or computes a reimbursement amount itself.

See `architecture.md` for the full write-up of the design decisions.

## Project layout

```
travel-reimbursement-agent/
├── agent/           # orchestrator + deterministic tools
│   ├── agent.py         # TravelReimbursementAgent orchestrator
│   ├── tools.py         # validate_receipt, check_duplicate, get_approval_matrix
│   ├── policy.py        # retrieve_policy
│   └── calculator.py    # calculate_reimbursement (the only place amounts are computed)
├── api/
│   └── main.py      # FastAPI service: POST /v1/reimbursements
├── policies/        # versioned policy + approval matrix data
├── data/            # sample claims and receipts
├── tests/           # approval / partial / rejection / manual-review test suites
├── demo.py          # runs the TR-10045 sample claim end to end
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the demo

```bash
python demo.py
```

Expected output:

```
================================================
Travel Reimbursement Approval Agent
================================================
Claim ID: TR-10045
Claimed Amount: ₹19,200
Approved Amount: ₹15,100
Rejected Amount: ₹4,100
Decision: PARTIALLY_APPROVE

Evidence:
✓ Flight: Within policy limit
⚠ Hotel: Exceeds policy limit of 5000
⚠ Meal: Exceeds policy limit of 2000
✓ Taxi: Within policy limit

Policy: DOM-TRAVEL-2026
Sections: flight-2.1, hotel-3.1, meals-4.2, taxi-5.1
Manual Review: NO
Confidence: 0.99
================================================
```

## Run the API

```bash
uvicorn api.main:app --reload
```

Submit a claim:

```bash
curl -X POST http://127.0.0.1:8000/v1/reimbursements \
  -H "Content-Type: application/json" \
  -d '{
        "employee_id": "EMP-123",
        "trip_type": "DOMESTIC",
        "travel_start": "2026-08-10",
        "travel_end": "2026-08-12",
        "expenses": [
          {"category": "HOTEL", "amount": 8500, "receipt_id": "REC-002"}
        ]
      }'
```

## Run the tests

```bash
pytest -v
```

Test suites cover four scenarios directly, matching the evaluation strategy
in `architecture.md`:

- `test_approval.py` — a claim fully within policy
- `test_partial.py` — the TR-10045 sample claim (hotel + meal over limit)
- `test_rejection.py` — duplicate receipts and unsupported categories
- `test_manual_review.py` — missing receipts, low OCR confidence,
  business-class flights, high-value claims, and missing travel dates

## What's deliberately mocked

This is a demo-scale reference implementation, not a production system:

- **Policy retrieval** is a JSON file lookup rather than a RAG pipeline over a
  vector store — the tool contract (`retrieve_policy`) is the same either way.
- **Receipt validation** reads from a fixed `data/receipts.json` instead of
  calling an OCR/Document AI service.
- **Duplicate detection** uses an in-memory ledger instead of a database.
- **The LLM orchestration layer** (Gemini/Claude + ADK-style tool calling) is
  represented by the `trace` list `process_claim()` returns — swap in a real
  model call that decides *which* tool to invoke next, and the tool contracts
  underneath don't need to change.

None of these mocks affect the one architectural rule that matters: amounts
are always computed by `calculator.py`, never by a language model.
