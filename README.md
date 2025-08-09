# RocketNet Client Portal

A modern, award-winning client portal for RocketNet customers, powered by FastAPI and a world-class Next.js frontend. Integrates seamlessly with the Splynx BSS/OSS platform.

## Features

* View current and historical invoices
* Monitor data usage in near-real-time
* Run speed tests directly from the portal
* Browse and upgrade to faster packages
* Guided downgrade/cancellation path with retention fee enforcement

---

## Quick start

### Prerequisites

* Python 3.11+
* Node.js 20+
* Yarn or npm
* Splynx instance with API access

### 1. Clone and configure env

```bash
git clone <repo-url>
cd rocketnet-portal
cp .env.example .env
# Edit .env with your Splynx URL and API credentials
```

### 2. Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 to explore the portal.

---

## Project structure

```
.
├── backend/          # FastAPI backend + Splynx API wrapper
├── frontend/         # Next.js 14 app with Material UI design system
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── .env.example      # Environment variable template
```

---

## License

MIT © RocketNet
