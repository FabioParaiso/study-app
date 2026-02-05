# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Super Study is an adaptive learning platform for young students (ages 10-12, Portuguese-speaking). It uses AI-powered quiz generation with Bloom's Taxonomy progression and gamification. The app has a React/Vite frontend and FastAPI backend.

## Commands

### Backend
```bash
# Run all backend tests
cd backend && pytest

# Run a single test file
cd backend && pytest tests/test_quiz_policies.py

# Run a single test by name
cd backend && pytest tests/test_quiz_policies.py -k "test_name"

# Start dev server
cd backend && python -m uvicorn main:app --reload --port 8000

# Install dependencies
cd backend && pip install -r requirements.txt
```

### Frontend
```bash
# Run all frontend tests (watch mode)
cd frontend && npm test

# Run all frontend tests once (CI mode)
cd frontend && npm test -- --run

# Run a single test file
cd frontend && npx vitest run src/utils/xpCalculator.test.js

# Start dev server
cd frontend && npm run dev

# Lint
cd frontend && npm run lint

# Build
cd frontend && npm run build
```

## Architecture

### Backend (`/backend`)

Modular, Clean Architecture with feature-based organization:

- **`main.py`** / **`app_factory.py`** — App entry point, CORS, middleware, route registration
- **`database.py`** — SQLAlchemy engine and session factory
- **`dependencies.py`** — Dependency injection container (FastAPI `Depends()`)
- **`security.py`** — bcrypt password hashing, JWT token utilities
- **`rate_limiter.py`** — slowapi limiter instance

Each **module** (`modules/auth`, `modules/materials`, `modules/quizzes`, `modules/analytics`, `modules/gamification`, `modules/usage`) follows a consistent structure:
- `router.py` — FastAPI endpoints
- `service.py` — Business logic
- `repository.py` — Data persistence (SQLAlchemy)
- `models.py` — ORM entities
- `ports.py` — Protocol interfaces for dependency injection
- `use_cases.py` — Orchestration workflows (quizzes/materials)

**Key design patterns:**
- **Strategy + Registry** for quiz types: `QuizTypeRegistry` in `modules/quizzes/registry.py` registers generation/evaluation strategies per quiz type (multiple-choice, short_answer, open-ended). Strategies live in `modules/quizzes/engine.py`.
- **Ports (Protocols)** for all service boundaries — enables mocking in tests.
- **Adaptive learning engine**: `AdaptiveTopicSelector` and `ConceptWhitelistBuilder` in `modules/quizzes/policies.py` control quiz content selection based on mastery tracking per concept.

**LLM integration** — OpenAI calls abstracted via `services/openai_caller.py` and `services/openai_client.py`. Rate-limited by daily quota (`modules/usage`).

### Frontend (`/frontend`)

React 19 + Vite 6 + Tailwind CSS. State management via custom hooks (no Redux):
- `hooks/useQuiz.js` — Quiz engine state, answer tracking, active-seconds timing
- `hooks/useQuizEngine.js` — Lower-level game loop (scoring, streaks)
- `hooks/useGamification.js` — XP, levels, avatars
- `hooks/useMaterial.js` — Material upload/activation
- `hooks/useAnalytics.js` — Dashboard metrics

Tests are co-located with source files (e.g., `useQuiz.test.js` next to `useQuiz.js`). Uses vitest + jsdom + React Testing Library.

### Database Schema (Hierarchical)

Students → StudyMaterials → Topics → Concepts. Quiz results link to QuestionAnalytics per concept for granular mastery tracking.

### Domain Concepts

- **Quiz types** progress via Bloom's Taxonomy: multiple-choice (0 XP) → short_answer (300 XP) → open-ended (900 XP)
- **Concept mastery** tracked per concept using a sliding window of recent results (CONFIDENCE_WINDOW=7). States: exploring → confident → mastered.
- **XP gating** — `QuizUnlockPolicy` in `policies.py` enforces XP thresholds to unlock harder quiz types
- **Readiness gate** — Short answer unlocked only when >50% of concepts have confident MCQ data

### Testing

- **Backend**: pytest with in-memory SQLite. Fixtures in `conftest.py` provide `client`, `db_session`, `auth_headers`. `TEST_MODE=true` disables rate limiting.
- **Frontend**: vitest with jsdom. Setup in `vite.config.js` and `src/setupTests.js`.
- **CI**: GitHub Actions runs both test suites on PRs to main (Python 3.11, Node 20).

## Conventions

- UI strings and domain terms are in **Portuguese** (target audience)
- `Port` suffix for abstract Protocol interfaces, `UseCase` suffix for orchestrators
- Backend tests run from `backend/` directory (conftest.py adjusts `sys.path`)
