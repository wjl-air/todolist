# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack TodoList app: Vue 3 frontend + FastAPI backend + MySQL database. UI is in Chinese.

## Commands

### Frontend
```bash
npm install          # install deps
npm run dev          # start dev server (port 5173)
npm run build        # production build → dist/
npm run preview      # preview production build
```

### Backend
```bash
pip install fastapi uvicorn pymysql pydantic
python init_db.py          # create MySQL database + table (run once)
uvicorn backend.main:app --reload --port 8000   # start dev server
```

### Database
- MySQL required on localhost, user `root`, password `root`, database `1111`
- `init_db.py` creates the database and `todos` table automatically

## Architecture

**Frontend** (`src/`): Vue 3 SPA with Composition API (`<script setup>`).
- `App.vue` — orchestrator: owns `todos` array, all API calls (`fetch` to `http://localhost:8000/api/todos`), event handlers
- `TodoForm.vue` — add/edit form, emits `add` / `update` / `cancel`
- `TodoList.vue` — renders todo items with checkbox, edit, delete; emits `toggle` / `edit` / `delete`

**Backend** (`backend/`): FastAPI app with raw PyMySQL (no ORM).
- `main.py` — all routes + DB config + Pydantic schemas (duplicated inline; `models.py` and `database.py` exist but are **not imported**)
- REST API: `GET/POST /api/todos`, `PUT/DELETE /api/todos/{id}`

**Key data flow**: Frontend `fetch` → FastAPI (CORS enabled for localhost:5173) → MySQL (`completed` stored as TINYINT 0/1, converted to boolean by frontend's `toBool()`).

## Deployment

`DEPLOY.md` documents a Docker + GitHub Actions CI/CD plan (nginx reverse proxy, GHCR images). Not yet implemented — no Dockerfiles or compose file exist yet.
