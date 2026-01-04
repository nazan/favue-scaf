.PHONY: build run clean

DOCKER_IMAGE = favue-scaf
PROJECTS_DIR ?= $$HOME/projects

build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .
	@echo "✓ Docker image built: $(DOCKER_IMAGE)"

run: build
	@echo "Running scaffolder..."
	@echo "Projects will be created in: $(PROJECTS_DIR)"
	@echo "Files will be owned by your user (UID: $$(id -u), GID: $$(id -g))"
	@echo ""
	docker run --rm -it \
		-e USER_ID=$$(id -u) \
		-e GROUP_ID=$$(id -g) \
		-v "$(PROJECTS_DIR):/workspace" \
		-w /workspace \
		$(DOCKER_IMAGE) \
		python -m scaffolder

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"

