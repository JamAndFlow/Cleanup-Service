# OTP Cleanup Service

This service handles the automatic cleanup of expired OTPs in the JamAndFlow database.

## Setup

1. Create a `.env` file:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=PassWord
POSTGRES_DB=JamAndFlow
POSTGRES_HOST=db
POSTGRES_PORT=5432
CLEANUP_INTERVAL_SECONDS=300  # 5 minutes
```

2. Build and run with Docker Compose:
```bash
docker compose up --build
```

## Configuration

- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name
- `POSTGRES_HOST`: PostgreSQL host (default: `db` for Docker Compose)
- `POSTGRES_PORT`: PostgreSQL port (default: `5432`)
- `CLEANUP_INTERVAL_SECONDS`: Interval between cleanup runs (default: 300 seconds / 5 minutes)

## Docker Network

This service needs to be on the same network as your main JamAndFlow API:

```bash
# Create the network if it doesn't exist
docker network create jamandflows-network
```

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run locally:
```bash
python cleanup.py
```
