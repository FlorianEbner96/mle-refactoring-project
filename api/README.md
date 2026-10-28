# api: Houses CRUD API

A FastAPI app that stores houses in Postgres, described by five features: `bedrooms`, `bathrooms`, `sqft_living`, `grade`, `zipcode`. It is CRUD only; it does not use the trained model.

## Files

| File | What it does |
| --- | --- |
| `database.py` | Reads `DB_CONN`, creates the engine, provides one session per request (`get_db`) |
| `models.py` | The `houses` table (SQLAlchemy) |
| `schemas.py` | Validated request/response shapes (Pydantic), e.g. `grade` must be 1 to 13 |
| `main.py` | The routes |
| `Dockerfile`, `Dockerfile.dockerignore` | Builds the API image from the project root, installs only the `api` dependency group, runs as a non-root user |
| `docker-compose.yaml` | Starts the API and Postgres together; the API waits until the database is healthy |
| `.env.example` | Template for `.env` (database credentials and connection string) |

## Endpoints

| Method | Path | Result |
| --- | --- | --- |
| `GET` | `/` | health check |
| `GET` | `/houses` | all houses |
| `GET` | `/houses/{id}` | one house, or 404 |
| `POST` | `/houses` | creates a house, 201 |
| `PUT` | `/houses/{id}` | replaces a house, or 404 |
| `DELETE` | `/houses/{id}` | deletes a house, 204, or 404 |

Invalid data returns 422. Interactive docs: <http://localhost:8000/docs>.

## Run with Docker

From the project root:

```powershell
cp api/.env.example api/.env                              # first time only
docker compose -f api/docker-compose.yaml up --build --wait
docker compose -f api/docker-compose.yaml down            # stop, keep the data
docker compose -f api/docker-compose.yaml down --volumes  # stop and wipe the database
```

The API reaches the database at the host `db`. Postgres is not exposed to your machine.

## Example request

```powershell
curl -X POST http://localhost:8000/houses -H "Content-Type: application/json" `
  -d '{"bedrooms":3,"bathrooms":2.5,"sqft_living":1800,"grade":8,"zipcode":"98103"}'
```

## Tests

```powershell
uv run pytest tests/test_api.py
```

The tests swap the database for an in-memory SQLite one, so they never touch Postgres.

## Notes

- Tables are created on startup with `create_all`. A real project would use migrations (Alembic).
- `.env` holds a development password and is gitignored. Change it before any real deployment.
