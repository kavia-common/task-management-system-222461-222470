# Todo Backend (Flask)

A minimal Flask REST API providing CRUD operations for tasks with OpenAPI docs via flask-smorest.

- Binds to: 0.0.0.0:3001
- CORS: Allows requests from http://localhost:3000
- Docs: Available under /docs and /docs/openapi.json

## Endpoints

- GET /health
- GET /api/tasks
- POST /api/tasks
- GET /api/tasks/<id>
- PUT /api/tasks/<id>
- PATCH /api/tasks/<id>
- DELETE /api/tasks/<id>

Task model:
- id: integer
- title: string (required)
- completed: boolean (default false)
- created_at: ISO string
- updated_at: ISO string

## Run locally

```
python run.py
# The server listens on 0.0.0.0:3001
```

## Sample curl sequence (CRUD)

```
# Health
curl -s http://localhost:3001/ | jq .

# List (initially empty)
curl -s http://localhost:3001/api/tasks | jq .

# Create
curl -s -X POST http://localhost:3001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"First task"}' | jq .

# Create another one (completed true)
curl -s -X POST http://localhost:3001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Second task","completed":true}' | jq .

# List
curl -s http://localhost:3001/api/tasks | jq .

# Get single task (id=1)
curl -s http://localhost:3001/api/tasks/1 | jq .

# Update (PUT) id=1
curl -s -X PUT http://localhost:3001/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"First task updated","completed":true}' | jq .

# Partial update (PATCH) id=2
curl -s -X PATCH http://localhost:3001/api/tasks/2 \
  -H "Content-Type: application/json" \
  -d '{"completed":false}' | jq .

# Delete id=1
curl -s -X DELETE http://localhost:3001/api/tasks/1 -i

# List to confirm
curl -s http://localhost:3001/api/tasks | jq .
```

## Notes

- This implementation uses an in-memory store for simplicity and preview compatibility.
- To switch to a persistent SQLite DB in the future, keep the API the same and swap the storage layer.
