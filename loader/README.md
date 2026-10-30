# FinKids Content Loader

Reads markdown content files from this repo and seeds the FinKids database via the
admin bulk-upsert endpoints.

## Prerequisites

- Python 3.10+
- A running FinKids backend (`content-service`) with migrations V16 and V17 applied
- An admin JWT token

```bash
cd loader
pip install -r requirements.txt
```

## Getting an admin token

Use the FinKids local dev token minter or ask Dharmesh for a staging admin token.
Never hardcode the token.

## Run order

**Always dry-run first:**

```bash
python load_content.py --dry-run
```

Fix any validation errors reported, then run live:

```bash
python load_content.py --be-url http://localhost:8080 --token <admin-jwt>
```

## Re-run safety

All endpoints are idempotent — safe to re-run. Existing records are updated in place;
missing records are inserted. Running twice produces the same DB state.

## Wait for content fixes

Do NOT run the live load against staging until JP-ContentLoader1 sends
"Content-1 fixes done" via AgentCom. Dry-run is always safe.
