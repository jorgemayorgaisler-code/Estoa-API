# Mares Chile API Prototype v1

Prototype backend for the five-tab app.

## Run
`pip install -r requirements.txt`
`uvicorn app:app --reload`

## Endpoints
- `GET /stations`
- `GET /conditions/at?station_id=CUR011&local_datetime=2026-10-04T18:30:00`
- `GET /conditions/now?station_id=CUR011`
- `GET /forecast?station_id=CUR011&start=2026-10-04T18:00:00&hours=12`

This prototype exposes the current engine first. Tide and astronomy fields are contract placeholders except for the separately validated Kirke integrated payload in RC1.
