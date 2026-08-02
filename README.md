# IntelliMed

IntelliMed is an end-to-end educational healthcare decision-support and smart pharmacy prototype. It combines symptom-pattern classification, pharmacist-reviewable over-the-counter options, catalog and checkout workflows, purchase-driven inventory usage, and ML demand forecasting.

## Live demo

IntelliMed is deployed at [intellimed-gjnq.onrender.com](https://intellimed-gjnq.onrender.com).

- Application hosting: Render free web service
- Production database: Neon PostgreSQL
- Health check: [`/health`](https://intellimed-gjnq.onrender.com/health)

The free Render instance spins down after inactivity, so the first request may take about a minute. Production administrator credentials are stored only as Render environment secrets and are not included in this repository.

## Safety boundary

This project does not diagnose disease or prescribe medicine. Recommendations are explicit, reviewable mappings to demo OTC catalog entries. Chest pain and shortness of breath bypass inference and display urgent-care guidance. Any real deployment requires clinical governance, validated data, regulatory review, privacy controls, and qualified pharmacist oversight.

## End-to-end flow

1. A visitor selects symptoms.
2. A reproducible random-forest classifier returns a broad educational pattern and confidence.
3. Safe catalog options are selected through an explicit mapping for pharmacist review.
4. An authenticated customer checks out; stock decreases and monthly usage increases atomically.
5. An admin views next-month demand and suggested replenishment from a random-forest regressor using the latest three monthly totals.
6. Restocking updates current inventory.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts\train_models.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

Demo customer: `customer@intellimed.local` / `Customer123!`

Demo admin: `admin@intellimed.local` / `Admin123!`

Change all demo credentials and `INTELLIMED_SESSION_SECRET` outside local development.

## Verification

```powershell
pytest
ruff check .
```

The SQLite database is created at `data/intellimed.db`; trained artifacts are written to `artifacts/`. Both are generated and excluded from Git. Set `INTELLIMED_DATABASE_URL` to use another SQLAlchemy-compatible database in deployment.

## Deployment

The live demo uses a Render web service with a Neon PostgreSQL database. Do not use SQLite on Render's free tier: its filesystem is ephemeral, so accounts, orders, and inventory changes would be lost whenever the service restarts or spins down.

1. Push this project to a GitHub repository.
2. Create a free project at [Neon](https://console.neon.tech) and copy its PostgreSQL connection string from **Connect**.
3. In [Render](https://dashboard.render.com), choose **New > Blueprint** and select the GitHub repository. Render reads `render.yaml` automatically.
4. Enter these requested secret values:
	- `INTELLIMED_DATABASE_URL`: the Neon connection string, including `sslmode=require`
	- `INTELLIMED_ADMIN_EMAIL`: the private administrator email
	- `INTELLIMED_ADMIN_PASSWORD`: a unique password of at least 10 characters
5. Deploy, then open the generated `onrender.com` URL. Verify `/health` returns `{"status":"ok"}`.

The application creates its PostgreSQL tables and seeds the medicine catalog and forecasting history during first startup. Public users create their own customer accounts through `/signup`. Render free web services sleep after inactivity, so the first request after a pause can take about one minute; Neon keeps application data outside Render's ephemeral filesystem.

## Project map

- `app/main.py`: HTTP routes, session handling, CSRF checks, checkout, and admin workflow
- `app/ml.py`: feature contract, model training, safety interception, inference, and demand forecasts
- `app/models.py`: users, medicine, orders, line items, and monthly usage schema
- `app/seed.py`: deterministic demo catalog and training history
- `app/templates/`: responsive server-rendered interface
- `scripts/train_models.py`: reproducible training entry point
- `tests/`: safety, inference, checkout, inventory, and authorization coverage