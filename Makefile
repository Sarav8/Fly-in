VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

MAIN = main.py
FILES = drone.py graph.py parser.py pathfinder.py simulation.py utils.py visualizer.py zones.py
CONFIG_FILE = maps/hard/03_ultimate_challenge.txt
PROJECT_CONFIG = pyproject.toml

all: banner install run

banner:
	@echo "**************************************"
	@echo "            DRONE LOGISTIC            "
	@echo "**************************************"

install: $(VENV)/bin/activate

$(VENV)/bin/activate: $(PROJECT_CONFIG)
	@echo "Initializing virtual environment and installing dependencies..."
	python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -e ".[dev]"
	@touch $(VENV)/bin/activate

run: install
	@echo "Running..."
	@$(PYTHON) $(MAIN) $(CONFIG_FILE)

debug: install
	@echo "Running in debug mode..."
	@$(PYTHON) -m pdb $(MAIN) $(CONFIG_FILE)

lint: install
	@echo "Linters"
	@echo "- Check flake8..."
	$(PYTHON) -m flake8 $(MAIN) $(FILES)
	@echo "- Check mypy..."
	@$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

clean:
	@echo "Cleaning temporary files..."
	@rm -rf __pycache__ .mypy_cache .venv venv
	@rm -rf build/ dist/ *.egg-info

.PHONY: all lint clean run debug banner install