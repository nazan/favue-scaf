MY_UID = $$(id -u)
MY_GID = $$(id -g)

.PHONY: setup first-time create-volumes build pip up down migrate test logs clean-volumes

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
	@if docker volume inspect ${PROJECT_NAME}_dbdata >/dev/null 2>&1; then \
		echo "⚠ Warning: Volume ${PROJECT_NAME}_dbdata already exists (may contain old data)"; \
		echo "   Run 'make clean-volumes' to remove volumes and start fresh"; \
	else \
		docker volume create ${PROJECT_NAME}_dbdata; \
	fi
	@if docker volume inspect ${PROJECT_NAME}_dbdata_test >/dev/null 2>&1; then \
		echo "⚠ Warning: Volume ${PROJECT_NAME}_dbdata_test already exists (may contain old data)"; \
		echo "   Run 'make clean-volumes' to remove volumes and start fresh"; \
	else \
		docker volume create ${PROJECT_NAME}_dbdata_test; \
	fi
	@if docker volume inspect ${PROJECT_NAME}_sitepack >/dev/null 2>&1; then \
		echo "⚠ Warning: Volume ${PROJECT_NAME}_sitepack already exists"; \
	else \
		docker volume create ${PROJECT_NAME}_sitepack; \
	fi
	@echo "✓ Docker volumes ready."

build: touch-all
	@echo "Building Docker images..."
	@docker compose build
	@echo "✓ Images built."

pip: build
	@echo "Installing Python dependencies..."
	@docker compose run --rm --no-deps ${BACKEND_NAME} sh -c "python -m venv /home/appuser/venv 2>/dev/null || true && pip install --no-cache-dir -r requirements.txt"
	@echo "✓ Dependencies installed."

up: touch-all
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
	@echo "Running test database migrations and tests..."
	@docker compose run --rm --no-deps ${BACKEND_NAME} ./run-tests.sh
	@echo "✓ Tests complete."

logs:
	@docker compose logs -f ${BACKEND_NAME} ${FRONTEND_NAME}

clean-volumes:
	@echo "⚠ WARNING: This will delete all database data in the Docker volumes!"
	@echo "Database volumes to be removed:"
	@echo "  - ${PROJECT_NAME}_dbdata"
	@echo "  - ${PROJECT_NAME}_dbdata_test"
	@echo ""
	@echo "Note: Python packages volume (${PROJECT_NAME}_sitepack) will be preserved."
	@echo ""
	@echo "To proceed, run: make clean-volumes CONFIRM=yes"
	@if [ "$(CONFIRM)" != "yes" ]; then \
		echo "Cancelled. Set CONFIRM=yes to proceed."; \
		exit 1; \
	fi
	@echo "Removing database volumes..."
	@docker volume rm ${PROJECT_NAME}_dbdata 2>/dev/null || echo "Volume ${PROJECT_NAME}_dbdata not found"
	@docker volume rm ${PROJECT_NAME}_dbdata_test 2>/dev/null || echo "Volume ${PROJECT_NAME}_dbdata_test not found"
	@echo "✓ Database volumes removed."

