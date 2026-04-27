#!/usr/bin/env bash
# =============================================================
# Development setup script
# Run once after cloning to get the backend running locally.
# =============================================================
set -e

echo "=== AcadémicoPro Backend — Development Setup ==="

# 1. Virtual environment
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate

# 2. Dependencies
echo "Installing dependencies..."
pip install --quiet -r requirements/development.txt

# 3. Environment file
if [ ! -f ".env" ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo "  Edit .env with your local database credentials before continuing."
  exit 1
fi

# 4. Database
echo "Running migrations..."
python manage.py migrate

# 5. Superuser
echo ""
echo "Create a superuser (global admin):"
python manage.py createsuperuser

# 6. Dev server
echo ""
echo "Starting development server..."
python manage.py runserver
