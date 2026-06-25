# 🛒 Ecom Support Agent

A **multi-agent e-commerce support system** built with LangGraph's **Supervisor + Parallel Workers** pattern. A supervisor LLM intelligently routes queries to specialized worker agents that run in parallel when tasks are independent.

---

## Architecture

```
User Query (POST /agent)
        │
        ▼
  ┌─────────────────┐
  │  supervisor_node │  ← Routes via structured output
  └────────┬────────┘
           │
    parallel_router
     ┌─────┴─────┐
     ▼           ▼
inventory_    logistic_       ← Run in PARALLEL if tasks
  worker        worker          are independent
     │           │
  ReAct loop  ReAct loop
     │           │
     └─────┬─────┘
           ▼
  supervisor_node  ← Evaluates results, may loop or FINISH
```

**Key design decisions:**
- Supervisor uses `with_structured_output` to always return valid worker names
- `Send()` API enables true parallel worker dispatch
- Each worker is an isolated ReAct subgraph — scoped to its domain only
- Workers ignore out-of-domain questions silently (no apologies)

---

## Project Structure

```
P14-Ecom-Support-Agent/
├── app/
│   ├── main.py
│   ├── models.py                          # AgentQuery / AgentResponse
│   ├── api/
│   │   └── router.py                      # POST /agent, GET /health
│   ├── core/
│   │   └── config.py                      # Pydantic settings (GROQ_API_KEY)
│   └── agent/
│       ├── supervisor/
│       │   └── supervisor.py              # Supervisor graph + parallel router
│       └── workers/
│           ├── inventory_worker/
│           │   ├── inventory_graph.py     # Inventory ReAct subgraph
│           │   └── inventory_tools.py     # check_stock tool
│           └── logistic_worker/
│               ├── logistic_graph.py      # Logistics ReAct subgraph
│               └── logistic_tools.py      # track_order tool
├── requirements.txt
└── pyproject.toml
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph `StateGraph` + `Send` API |
| LLM | `openai/gpt-oss-120b` via Groq |
| Structured Routing | Pydantic `BaseModel` + `with_structured_output` |
| API | FastAPI + Uvicorn |
| Settings | Pydantic Settings v2 |
| Python | 3.12 |

---

## Workers

### 🏬 Inventory Worker
Handles stock-related queries via a ReAct loop.

| Tool | Description |
|---|---|
| `check_stock(product_name)` | Returns in-stock / out-of-stock status |

Mock data: `laptop`, `phone` → In Stock. Everything else → Out of Stock.

### 🚚 Logistics Worker
Handles order tracking queries via a ReAct loop.

| Tool | Description |
|---|---|
| `track_order(order_id)` | Returns delivery status for an order ID |

---

## Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/pushphans/P14-Ecom-Support-Agent.git
cd P14-Ecom-Support-Agent

# Using uv (recommended)
uv sync

# Or pip
pip install -r requirements.txt
```

### 2. Configure Environment

```env
# .env
GROQ_API_KEY=your-groq-api-key-here
```

### 3. Run

```bash
uvicorn app.main:app --reload
```

---

## API Reference

### `POST /agent`

```json
// Request
{ "user_input": "Is the laptop in stock? Also track order #ORD123." }

// Response
{ "response": "Laptop is In Stock.\n\nOrder #ORD123 is out for delivery.", "error": null }
```

### `GET /health`

```json
{ "status": "ok" }
```

Swagger UI → `http://localhost:8000/docs`

---

## Routing Logic

The supervisor uses structured output to decide which workers to call:

| Query Type | Workers Dispatched |
|---|---|
| Stock check only | `["inventory_worker"]` |
| Order tracking only | `["logistics_worker"]` |
| Both (independent) | `["inventory_worker", "logistics_worker"]` — **parallel** |
| Fully resolved | `["FINISH"]` → graph exits |

---

## Extending

**Add a new worker** (e.g., refund agent):

```python
# 1. Create app/agent/workers/refund_worker/refund_graph.py
# 2. Register in supervisor.py
graph.add_node("refund_worker", refund_workflow)
graph.add_edge("refund_worker", "supervisor_node")

# 3. Update supervisor system prompt to mention refund_worker
```

---

## Author

**Pushp Hans** — AI Engineer · LangGraph · FastAPI  
GitHub: [@pushphans](https://github.com/pushphans)
