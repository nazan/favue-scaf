MY_UID = $$(id -u)
MY_GID = $$(id -g)

.PHONY: setup first-time create-volumes build pip up down migrate test logs

setup: first-time create-volumes build pip up migrate
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "✓ Setup complete!"
	@echo "═══════════════════════════════════════════════════════════"

first-time: touch-all
	@echo "First time setup complete."

touch-all:
	@if [ -f ./${BACKEND_NAME}/.env.example ] && [ ! -f ./${BACKEND_NAME}/.env ]; then \
		cp ./${BACKEND_NAME}/.env.example ./${BACKEND_NAME}/.env; \
	fi
	@if [ -f ./${BACKEND_NAME}/test.env.example ] && [ ! -f ./${BACKEND_NAME}/test.env ]; then \
		cp ./${BACKEND_NAME}/test.env.example ./${BACKEND_NAME}/test.env; \
	fi
	@if [ -f ./.env.example ] && [ ! -f ./.env ]; then \
		cp ./.env.example ./.env; \
	fi
	@if [ -f ./.env ]; then \
		if ! grep -q "^UID=" ./.env 2>/dev/null; then \
			echo "UID=$(MY_UID)" >> ./.env; \
		else \
			sed -i "s/^UID=.*/UID=$(MY_UID)/" ./.env; \
		fi; \
		if ! grep -q "^GID=" ./.env 2>/dev/null; then \
			echo "GID=$(MY_GID)" >> ./.env; \
		else \
			sed -i "s/^GID=.*/GID=$(MY_GID)/" ./.env; \
		fi; \
	fi
	@mkdir -p ./${BACKEND_NAME}/logs
	@touch ./${BACKEND_NAME}/logs/app.log

create-volumes:
	@echo "Creating Docker volumes..."
	@docker volume create ${PROJECT_NAME}_dbdata 2>/dev/null || echo "Volume already exists"
	@docker volume create ${PROJECT_NAME}_sitepack 2>/dev/null || echo "Volume already exists"
	@echo "✓ Docker volumes ready."

build: touch-all
	@echo "Building Docker images..."
	@docker compose build
	@echo "✓ Images built."

pip: build
	@echo "Installing Python dependencies..."
	@docker compose run --rm --no-deps ${BACKEND_NAME} sh -c "python -m venv /home/appuser/venv 2>/dev/null || true && pip install --no-cache-dir -r requirements.txt"
	@echo "✓ Dependencies installed."

up: touch-all create-volumes
	@echo "Starting services..."
	@docker compose up -d
	@echo "✓ Services started."

down:
	@docker compose down

migrate:
	@echo "Running database migrations..."
	@docker compose exec ${BACKEND_NAME} alembic upgrade head
	@echo "✓ Migrations complete."

test:
	@docker compose exec ${BACKEND_NAME} pytest

logs:
	@docker compose logs -f ${BACKEND_NAME} ${FRONTEND_NAME}

