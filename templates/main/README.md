# ${PROJECT_NAME}

FastAPI + Vue.js full-stack application.

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

- Backend API: http://localhost:${API_PORT}
- Frontend: http://localhost:${WEB_PORT}
- Database: localhost:${DB_PORT}

## Project Structure

- \`${BACKEND_NAME}/\` - FastAPI backend (git submodule)
- \`${FRONTEND_NAME}/\` - Vue.js frontend (git submodule)

## Testing

Run tests with:
\`\`\`bash
make test
\`\`\`

## Viewing Logs

View service logs with:
\`\`\`bash
make logs
\`\`\`

