# Super Study

Plataforma de estudo adaptativo para alunos do 2.o ciclo, com quizzes gerados por IA, progressao por niveis e analitica de desempenho por conceito.

## Visao Geral

- Frontend em React 19 + Vite 6 + Tailwind.
- Backend em FastAPI + SQLAlchemy (SQLite por defeito, PostgreSQL via `DATABASE_URL`).
- Fluxo principal: upload de material -> extracao de topicos/conceitos -> geracao de quiz -> avaliacao -> registo analitico.
- Modulos de dominio no backend: `auth`, `materials`, `quizzes`, `analytics`, `gamification`, `usage`.

## Estado Tecnico (snapshot local)

Validado localmente em `2026-02-06`:

- Backend: `141/141` testes a passar (`backend/.venv/bin/pytest`).
- Frontend: `84/84` testes a passar (`npm run test -- --run`).
- Build frontend: `npm run build` com sucesso.
- Lint frontend configurado com flat config (`frontend/eslint.config.js`) e a executar sem erros/avisos.

## Funcionalidades Principais

- Quizzes por tipo: `multiple-choice`, `short_answer`, `open-ended`.
- Selecao adaptativa de topicos/conceitos com base em historico (pontos fracos e dominio).
- Biblioteca de materiais por aluno com ativacao e remocao.
- Registo de metricas por sessao: score, tempo total, tempo ativo, distribuicao por tipo.
- Dashboard de analitica:
  - pontos fracos por conceito
  - tempo ativo por dia
  - evolucao de aprendizagem por nivel
- Gamificacao: XP, avatar atual, high score.
- Autenticacao por JWT.

## Arquitetura

### Backend (`backend/`)

- `main.py`: bootstrap da app, `load_dotenv`, criacao de tabelas, pequenos ajustes de schema.
- `app_factory.py`: middlewares, CORS, rate limiting e registo de rotas.
- `dependencies.py`: injeccao de dependencias (`Depends`) e autenticacao de utilizador atual.
- `database.py`: engine/session SQLAlchemy e normalizacao de `DATABASE_URL`.
- `security.py`: hash de password com `bcrypt`, JWT e validacao de `SECRET_KEY`.
- `modules/*`: organizacao por dominio com `router`, `service`, `repository`, `use_cases`, `ports`, `models`.

Padroes relevantes:

- Arquitetura modular com ports/protocols.
- Estrategias de quiz via registry/factory (`modules/quizzes/registry.py`).
- Politicas de selecao adaptativa de conceitos (`modules/quizzes/policies.py`).

### Frontend (`frontend/`)

- SPA em React com estado encapsulado em custom hooks.
- Hooks principais:
  - `useMaterial`: upload/ativacao/gestao de materiais.
  - `useQuiz` + `useQuizEngine`: ciclo de quiz, pontuacao, submissao de resultados.
  - `useAnalytics`: consumo de metricas.
  - `useGamification`: XP, niveis e avatar.
  - `useStudent`: sessao autenticada (token em `localStorage`).
- Cliente API centralizado em `src/services/api.js` (Axios + bearer token interceptor).

## Estrutura do Repositorio

```text
.
├── backend/
│   ├── app_factory.py
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   ├── security.py
│   ├── modules/
│   │   ├── auth/
│   │   ├── materials/
│   │   ├── quizzes/
│   │   ├── analytics/
│   │   ├── gamification/
│   │   └── usage/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── public/
└── .github/workflows/
```

## Requisitos

- Node.js 20+ (recomendado).
- Python 3.11+ (o projeto tem sido executado com 3.14 localmente).
- Chave OpenAI (`OPENAI_API_KEY`) para funcionalidades de IA.

## Setup Local

### 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

Criar `backend/.env`:

```env
# Obrigatorias para runtime normal
SECRET_KEY=troca_esta_chave_por_uma_forte
OPENAI_API_KEY=sk-...

# Comportamento da app
REGISTER_ENABLED=true
INVITE_CODE=opcional
DAILY_AI_CALL_LIMIT=50
AI_RATE_LIMIT=20/minute
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=false

# DB e ambiente
DATABASE_URL=sqlite:///./study_app.db
APP_ENV=staging
```

Iniciar API:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
```

Criar `frontend/.env` (ou ajustar conforme ambiente):

```env
VITE_API_URL=http://localhost:8000
VITE_BASE_PATH=/
VITE_REGISTER_ENABLED=true
```

Iniciar frontend:

```bash
cd frontend
npm run dev
```

Aplicacao disponivel em `http://localhost:5173`.

## Variaveis de Ambiente

### Backend

| Variavel | Obrigatoria | Default | Uso |
| --- | --- | --- | --- |
| `SECRET_KEY` | Sim (exceto `TEST_MODE=true`) | `super_secret_key_change_me` | Assinatura JWT |
| `OPENAI_API_KEY` | Sim para IA | vazio | Geracao/avaliacao via OpenAI |
| `REGISTER_ENABLED` | Nao | `true` | Liga/desliga registo |
| `INVITE_CODE` | Nao | vazio | Se definido, registo exige codigo |
| `DAILY_AI_CALL_LIMIT` | Nao | `50` | Limite diario por aluno |
| `AI_RATE_LIMIT` | Nao | `20/minute` | Rate limit por IP em endpoints IA |
| `ALLOWED_ORIGINS` | Nao | localhost:5173 | CORS allow origins |
| `CORS_ALLOW_CREDENTIALS` | Nao | `false` | CORS credentials |
| `DATABASE_URL` | Nao | `sqlite:///./study_app.db` | Ligacao DB |
| `APP_ENV` | Nao | `staging` | Selecao de modelos LLM |
| `TEST_MODE` | Nao | `false` | Desativa certos controlos em teste |
| `COOP_CHALLENGE_ENABLED` | Nao | `false` | Flag global do modo desafio cooperativo |
| `COOP_PAUSE_MODE_ENABLED` | Nao | `false` | Flag do modo pausa cooperativo |
| `CHALLENGE_LAUNCH_DATE` | Nao | vazio | Data de lancamento do desafio (`YYYY-MM-DD`) |

### Frontend

| Variavel | Obrigatoria | Default | Uso |
| --- | --- | --- | --- |
| `VITE_API_URL` | Nao | `http://localhost:8000` | URL base da API |
| `VITE_BASE_PATH` | Nao | `/` | Base path de deploy (GitHub Pages) |
| `VITE_REGISTER_ENABLED` | Nao | `true` | Mostra/esconde registo na UI |

## Scripts Operacionais (Sprint 0)

Backfill de `challenge_xp` em modo seguro (default `dry-run`):

```bash
cd backend
python -m scripts.backfill_challenge_xp --student-name "Nome Aluna"
```

Emparelhamento inicial em modo seguro (`--dry-run`):

```bash
cd backend
python -m scripts.pair_students --a-id 1 --b-name "Maria" --dry-run
```

Nota: as opcoes `--apply` dos dois scripts exigem backend atualizado com Sprint 1A (startup cria/ajusta colunas automaticamente).

## Testes e Qualidade

### Backend

```bash
cd backend
source .venv/bin/activate
ruff check .
pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run test -- --run
npm run build
```

Nota: para correcoes automaticas de lint no frontend, usa `npm run lint:fix`.

## Endpoints Principais

| Area | Endpoint |
| --- | --- |
| Health | `GET /health` |
| Auth | `POST /register`, `POST /login`, `GET /me` |
| Materiais | `GET /current-material`, `POST /upload`, `POST /analyze-topics`, `GET /materials`, `POST /materials/{id}/activate`, `DELETE /delete-material/{id}`, `POST /clear-material` |
| Quizzes | `POST /generate-quiz` (inclui `quiz_session_token`), `POST /evaluate-answer`, `POST /quiz/result` |
| Challenge | `GET /challenge/weekly-status` |
| Analitica | `GET /analytics/weak-points`, `GET /analytics/metrics`, `GET /analytics/learning-trend` |
| Gamificacao | `POST /gamification/xp`, `POST /gamification/avatar`, `POST /gamification/highscore` |

Documentacao interativa FastAPI em `/docs`.

## CI/CD (GitHub Actions)

- `main-tests.yml`: lint + testes de backend e frontend em `main` (push + PR).
- `staging-tests.yml`: lint + testes de staging em `staging` (backend sem integracao + frontend).
- `deploy-pages.yml`: build/deploy do frontend para GitHub Pages em `main/master`.

## Notas de Desenvolvimento

- Strings de produto e UX estao maioritariamente em portugues.
- O backend usa dependencia por ports para facilitar mocking em testes.
- O token JWT e armazenado no `localStorage` com chave `study_token`.
