# Saathi AI 3.0 - Backend

"The Financial Future Operating System"

This package contains Phases 1-6 of the MVP:

1. Project structure
2. Synthetic banking dataset generator (`app/data/generator.py`)
3. Feature engineering pipeline (`app/features/pipeline.py`)
4. Financial DNA engine (`app/engines/dna.py`)
5. Life Event Knowledge Graph (`app/engines/life_event_graph.py`)
6. Financial Future Index / FFI (`app/engines/ffi.py`)

The Agentic RM, Financial GPS and SBI dashboard backends build on top of these.

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Generate synthetic dataset (creates data/customers.csv, data/transactions.csv)
python -m app.data.generator

# 2. Train the FFI model on the synthetic data
python -m app.ml.train_ffi

# 3. Run the API
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000/docs

## Demo story (Rahul)

```bash
curl http://localhost:8000/api/v1/customers/rahul/dna
curl http://localhost:8000/api/v1/customers/rahul/ffi
curl http://localhost:8000/api/v1/customers/rahul/life-events
```
