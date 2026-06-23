# DarkAtlas — Attack Surface Monitoring Platform

A backend Asset Management System built for the DarkAtlas ASM platform — tracks internet-facing assets (domains, subdomains, IPs, services, certificates, technologies), their lifecycle, and the relationships between them.

---

## Setup

1. Clone the GitHub repo
2. Run `docker compose up` in the root directory
3. Seed an admin user:
   ```bash
   docker exec <container_name> python -m backend.scripts.seed_admin
   ```
   This can be run from the command line or via the **Exec** tab in Docker Desktop.

---

## Environment Variables

Two example env files are provided (`.env.example` and `.env.db.example`) and work out of the box with a fresh Docker image.

To get started, simply remove the `.example` suffix from both files — the application will start without any further configuration.

---

## Run Instructions

- The API runs on `0.0.0.0:80` inside the container. Access it from your browser at `http://localhost/`.
- The database runs on port `5432` and is provisioned automatically as part of the Compose stack.

### Schema changes

If you modify the data schema (adding/removing columns, tables, etc.), run:

```bash
alembic revision --autogenerate -m "describe your change"
alembic stamp head
```

We use `stamp head` (rather than `upgrade head`) to preserve existing data in the database rather than re-running migrations against it.

### Bulk import (ingest)

Submit asset data as JSON in the format shown in the provided example input. Note: asset IDs are **always** server-generated as UUIDs — even if an ID is supplied in the input, it will be ignored and a new one assigned, to guarantee uniqueness and data integrity.

### Lifecycle / "touch" behavior

Accessing an asset also **reactivates** it (the same mechanism used for re-sighting during ingest). This happens on:
- Any `GET` request for a single asset
- Any `GET` request for assets in bulk
- Re-sighting an asset during a bulk ingest
- A conflict during asset creation (i.e. the asset already exists)

## API Documentation

Once running, interactive API docs (Swagger UI) are available at:
http://localhost/docs

## Running Tests

docker compose exec app pytest -v

## Relationship Graph Visualization (Bonus)

A simple static visualization of the asset relationship graph is available at:
http://localhost/graph-viewer

Enter an asset's UUID (and a bearer token if the endpoint requires auth) to render
that asset and its connected neighborhood, color-coded by asset type.

---

## Design Choices

**Async throughout (asyncpg + FastAPI)**
The application is fully async, leveraging FastAPI's async capabilities end-to-end. This introduces more boilerplate than a sync setup, but meaningfully improves overall application performance under concurrent load.

**Multi-tenancy model**
We assume this application is operated at the organization level: `admin` and `analyst` roles belong to DarkAtlas itself (the platform operator), while `viewer` represents any external entity — other organizations or consumers with access. This gives us a sensible authorization model across most endpoints, ensuring organizations can never access assets that aren't theirs.

**Organizations as a first-class entity**
Including organizations in the data model lets us track and analyze them far more easily — they're used directly for filtering and for dashboard aggregations.

**Aggregation endpoint**
An aggregation/summary endpoint was added since it's a near-requirement for building a frontend dashboard, for both external viewers and elevated (admin/analyst) users.

**No manual archiving**
Since lifecycle is handled semi-automatically (see below), exposing a manual "archive" action seemed more likely to introduce a security vulnerability than to provide meaningful quality-of-life value — so it was intentionally left out.

**Semi-automatic lifecycle reaping**
A background scheduler (e.g. APScheduler) was considered for automatically marking stale/archived assets over time. For this project's scope, we opted instead for a manual reaping endpoint — both approaches are valid, but the manual endpoint keeps behavior explicit and easy to test within the time available.

**Forced UUIDs on assets**
Asset IDs are always server-generated, never accepted from input — even during bulk import. This guarantees data integrity and ensures all lookup/search operations behave predictably. Attempting to force a specific ID is not supported and is strongly discouraged.

**Simple JWT (no refresh tokens)**
We use a straightforward password-flow JWT setup rather than full OAuth2 with refresh tokens. This fits the project's scope well — less boilerplate, less complexity — while still satisfying the task's authentication requirements.