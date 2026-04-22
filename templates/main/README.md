# ${PROJECT_NAME}

FastAPI + Vue.js full-stack application (nginx gateway, Redis, Taskiq worker, cron hooks, JWT auth).

## Quick Setup

\`\`\`bash
make setup
\`\`\`

This will:
1. Create .env files
2. Create Docker volumes
3. Build Docker images
4. Start services
5. Run database migrations

## Manual Setup

1. \`make first-time\` - Create .env files
2. \`make build\` - Build Docker images
3. \`make up\` - Start services
4. \`make migrate\` - Run migrations

## Development

- **Gateway (recommended):** http://localhost (port from \`GATEWAY_PORT\`, default 80) — nginx routes \`/api/*\` to the API and \`/\` to Vite
- **Backend (direct):** http://localhost:${API_PORT}
- **Frontend (direct):** http://localhost:${WEB_PORT}
- **Database:** localhost:${DB_PORT}

Copy \`.env.example\` to \`.env\` and set \`CRON_SECRET\`; copy \`${BACKEND_NAME}/.env.example\` to \`${BACKEND_NAME}/.env\` and set \`INTERNAL_CRON_SECRET\` to the same value so scheduled and internal routes work. Set \`EMAIL_VERIFY_BASE_URL\` in \`${BACKEND_NAME}/.env\` to the URL users open in the browser (e.g. \`http://localhost\` with the gateway, or \`http://localhost:${WEB_PORT}\` for direct Vite). Transactional email uses a **log transport** in the scaffold: verification messages appear in the \`${BACKEND_NAME}\` container logs (\`make logs\` or \`docker compose logs -f ${BACKEND_NAME}\`).

## Project Structure

- \`${BACKEND_NAME}/\` - FastAPI backend (git submodule)
- \`${FRONTEND_NAME}/\` - Vue.js frontend (git submodule)
- \`nginx/\` - Gateway config (bind-mounted into the \`gateway\` service)

## Testing

\`\`\`bash
make test
\`\`\`

## Viewing Logs

\`\`\`bash
make logs
\`\`\`

## Infrastructure demo

After \`make up\`, register and log in via the UI, then open **Infrastructure demo** in the nav. It demonstrates JWT-protected APIs, Taskiq → WebSocket on \`user-<id>\`, cron → \`/api/internal/scheduler-beacon\` → WebSocket \`public\`, and Redis pub/sub.
