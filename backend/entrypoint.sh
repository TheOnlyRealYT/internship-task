#!/bin/bash
set -e

alembic upgrade head
fastapi run backend/app.py --port 80