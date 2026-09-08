# DataProbe

DataProbe is a CLI-first AI agent for investigating relational databases with SQL.

It is being built as a learning and portfolio project to understand how agentic systems work by implementing the runtime ourselves. The goal is not to hide the process behind a large framework, but to make each step visible: database discovery, tool calls, observations, hypotheses, recovery, and the evidence behind the final answer.

> **Project status:** DataProbe is currently an early scaffold. The repository contains a FastAPI server, a Next.js web app, and a PostgreSQL development service. The SQL investigation agent and its tool loop are planned capabilities, not complete functionality yet.

## What DataProbe is meant to do

A user should be able to ask a natural-language analytical question such as:

> Why did revenue drop in March?

DataProbe should then investigate the connected database rather than guessing:

```text
User question
    ↓
Discover available tables
    ↓
Inspect relevant schemas
    ↓
Construct a SQL query
    ↓
Execute the query
    ↓
Observe and interpret the result
    ↓
Form a hypothesis
    ↓
Run follow-up queries
    ↓
Recover from SQL errors when necessary
    ↓
Return an evidence-backed answer
```

The intended agent should be able to:

- understand analytical questions expressed in natural language
- inspect an unknown relational database
- discover relevant tables and schemas
- construct and execute SQL queries
- interpret query results
- perform multi-step investigations
- recover from SQL errors and refine its approach
- explain the evidence supporting its conclusion

## Design principles

- **Transparent runtime:** agent decisions, tool calls, observations, and errors should be inspectable.
- **Evidence over confidence:** answers should be grounded in query results, not unsupported assumptions.
- **Database-aware investigation:** the agent should inspect the database before writing complex queries.
- **Incremental reasoning:** follow-up queries should be driven by observations from earlier steps.
- **Simple foundations:** prefer understandable code and existing project patterns over abstractions that hide the agent loop.
- **Learning over premature productization:** this is an engineering and systems-learning project, not a SaaS product.

## Repository structure

```text
DataProbe/
├── apps/
│   ├── server/             # FastAPI backend scaffold
│   │   ├── main.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   └── web/                # Next.js frontend scaffold
│       ├── app/
│       ├── package.json
│       └── README.md
├── DBs/                    # Local database-related assets
├── docker-compose.yml      # Local PostgreSQL service
├── CLAUDE.md               # Project goals and engineering guidance
└── README.md
```

## Prerequisites

Install the following tools before working on the project:

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) for the Python server
- Node.js with [pnpm](https://pnpm.io/) for the web app
- Docker and Docker Compose for the local PostgreSQL database

## Getting started

### 1. Start PostgreSQL

From the repository root:

```bash
docker compose up -d postgres
```

The development database is configured with:

| Setting  | Value       |
| -------- | ----------- |
| Host     | `localhost` |
| Port     | `5432`      |
| Database | `chinook`   |
| User     | `dataprobe` |
| Password | `dataprobe` |

The database is persisted in the `postgres_data` Docker volume. These credentials are for local development only and must not be reused in production.

Stop the database with:

```bash
docker compose down
```

To also remove the persisted local database volume:

```bash
docker compose down -v
```

### 2. Run the backend

In a separate terminal:

```bash
cd apps/server
uv sync
uv run fastapi dev main.py
```

The server is available at `http://localhost:8000`.

Current endpoints:

- `GET /` — returns a basic server status message
- `GET /health` — returns `{ "status": "ok" }`

FastAPI's interactive API documentation is available at `http://localhost:8000/docs` while the development server is running.

### 3. Run the web app

In another terminal:

```bash
cd apps/web
pnpm install
pnpm dev
```

The web app is available at `http://localhost:3000`.

The frontend is currently the default Next.js scaffold. It will become the interactive surface for submitting questions and displaying investigation traces as the agent is implemented.

## Development commands

### Server

```bash
cd apps/server
uv run fastapi dev main.py       # Run the development server
uv run fastapi --help            # Inspect FastAPI CLI options
```

### Web

```bash
cd apps/web
pnpm dev                         # Start Next.js in development mode
pnpm lint                        # Run ESLint
pnpm build                       # Create a production build
pnpm start                       # Serve the production build
```

## Planned architecture

The project is expected to evolve around a small set of explicit components:

1. **Question interface** — accepts a natural-language analytical question.
2. **Database inspection tools** — list tables, inspect table definitions, and discover relationships.
3. **SQL execution tool** — executes a query against the configured database and returns structured results or an error.
4. **Agent loop** — decides which tool to call next based on the question and previous observations.
5. **Observation and trace model** — records tool calls, results, errors, hypotheses, and intermediate reasoning artifacts.
6. **Answer generator** — produces a concise final answer with the queries and results that support it.
7. **Web interface** — visualizes the question, investigation steps, and final evidence.

The exact module boundaries are intentionally not fixed yet. They should follow the behavior of the runtime and remain easy to inspect and test.

## Safety and data handling

DataProbe is intended for local development and experimentation. Until access controls, query validation, and resource limits are implemented:

- do not connect it to production databases
- do not place real credentials in `docker-compose.yml` or source files
- treat generated SQL as untrusted input
- add read-only database permissions before allowing an agent to query sensitive data
- consider query timeouts, row limits, and protection against expensive queries
- avoid exposing database results through a public development server

## Roadmap

- [x] Create the initial repository structure
- [x] Add a local PostgreSQL development service
- [x] Add a minimal FastAPI server
- [x] Add a Next.js frontend scaffold
- [ ] Define the database connection configuration
- [ ] Implement table and schema discovery tools
- [ ] Implement safe SQL execution
- [ ] Build the explicit agent/tool loop
- [ ] Add SQL error recovery and retry behavior
- [ ] Record investigation traces
- [ ] Produce evidence-backed final answers
- [ ] Build the web interface for investigations
- [ ] Add tests for tools, agent decisions, and end-to-end investigations

## Contributing

Keep changes focused and explain behavior in terms of the agent runtime. When adding an agent capability, prefer a small explicit implementation with tests and observable input/output over a framework abstraction that makes the behavior difficult to follow.

Before opening a change, run the relevant checks for the area you changed:

```bash
cd apps/server && uv run python -m compileall .
cd apps/web && pnpm lint && pnpm build
```

## License

No license has been specified yet.
