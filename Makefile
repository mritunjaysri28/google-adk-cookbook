# ==============================================================================
# GoogleADK Cross-Platform Makefile (Windows & Linux/macOS Compatible)
# ==============================================================================

# Ensure project root is always included in Python import path
export PYTHONPATH := $(CURDIR)

# OS & Python Binary Detection
ifeq ($(OS),Windows_NT)
    SYS_PYTHON ?= python
    VENV_DIR = .venv
    VENV_BIN = $(VENV_DIR)/Scripts
    PYTHON = $(CURDIR)/$(VENV_BIN)/python.exe
else
    SYS_PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python3)
    VENV_DIR = .venv
    VENV_BIN = $(VENV_DIR)/bin
    PYTHON = $(CURDIR)/$(VENV_BIN)/python
endif

PIP = $(PYTHON) -m pip
ADK = $(PYTHON) -m google.adk.cli
CHAINLIT = $(PYTHON) -m chainlit

.PHONY: help venv install run-web run-agent run-ui clean check activate deactivate shell

# Default target
help:
	@echo "=============================================================================="
	@echo "Google ADK Project Commands (Windows & Linux Compatible)"
	@echo "=============================================================================="
	@echo "  make venv                  Create Python virtual environment (.venv)"
	@echo "  make setup                 Complete setup: venv, packaging tools & pyproject.toml"
	@echo "  make install               Install project dependencies from pyproject.toml"
	@echo "  make activate              Activate venv by spawning an active subshell session"
	@echo "  make deactivate            Show command to deactivate virtual environment"
	@echo "  make check                 Verify installed packages and dependencies"
	@echo "  make run-web [DIR=...]     Start ADK Web UI (default: DIR=01_foundation_agents)"
	@echo "  make run-agent AGENT=name  Run a specific agent via ADK CLI (e.g., AGENT=first_agent)"
	@echo "  make run-ui                Start the Cymbal Shops Paint Agent Chainlit Web UI"
	@echo "  make clean                 Cross-platform removal of __pycache__ and temp files"
	@echo "=============================================================================="

# Create virtual environment if it does not exist
$(VENV_DIR):
	@echo "[INFO] Creating virtual environment using $(SYS_PYTHON)..."
	$(SYS_PYTHON) -m venv $(VENV_DIR)
	@echo "[OK] Virtual environment created in $(VENV_DIR)"

venv: $(VENV_DIR)

# Activate virtual environment by launching an interactive session (Poetry / Pipenv pattern)
activate:
ifeq ($(OS),Windows_NT)
	@if [ -f .venv/Scripts/activate ]; then \
		echo "[INFO] Entering activated virtual environment (type 'exit' to leave)..."; \
		bash --init-file <(echo ". ~/.bashrc 2>/dev/null || true; source .venv/Scripts/activate"); \
	else \
		echo "[INFO] Entering activated virtual environment in PowerShell (type 'exit' to leave)..."; \
		powershell -NoExit -ExecutionPolicy Bypass -Command "if (Test-Path .venv/Scripts/Activate.ps1) { .\.venv\Scripts\Activate.ps1 } else { Write-Host 'Error: .venv not found. Run make venv first.' }"; \
	fi
else
	@echo "[INFO] Entering activated virtual environment (type 'exit' to leave)..."
	@bash --init-file <(echo ". ~/.bashrc 2>/dev/null || true; if [ -f .venv/bin/activate ]; then source .venv/bin/activate; fi")
endif

# Deactivate instructions
deactivate:
	@echo "=============================================================================="
	@echo "To deactivate, run directly in your terminal (or type 'exit' if using make activate):"
	@echo "  deactivate"
	@echo "=============================================================================="

# Alias for activate
shell: activate

# Complete project setup: creates venv, upgrades packaging tools, and installs from pyproject.toml
setup: $(VENV_DIR)
	@echo "[INFO] Upgrading packaging tools (pip, setuptools, wheel)..."
	@$(PIP) install --upgrade pip setuptools wheel
	@echo "[INFO] Installing project and dependencies from pyproject.toml..."
	@$(PIP) install -e .
	@echo "[OK] Environment setup complete."

# Install dependencies from pyproject.toml (auto-creates venv if needed)
install: $(VENV_DIR)
	@echo "[INFO] Installing dependencies from pyproject.toml..."
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -e .
	@echo "[OK] All dependencies installed successfully."

check:
	@echo "[INFO] Checking package compatibility..."
	$(PIP) check

run-web:
	@TARGET_DIR="$(DIR)"; \
	if [ -z "$$TARGET_DIR" ]; then \
		echo "=============================================================================="; \
		echo " Select directory to launch ADK Web UI:"; \
		echo "=============================================================================="; \
		echo "  1) 01_foundation_agents        (first_agent, app_agent)"; \
		echo "  2) 02_tool_agents              (function, langchain, crewai, search, rag)"; \
		echo "  3) 03_workflow_agents          (loop_agent, parent_and_subagents)"; \
		echo "  4) 04_supervisor_agent         (critic & reviser auditor)"; \
		echo "  5) 05_mcp_agents               (MCP server & Maps client)"; \
		echo "  6) 06_a2a_protocol_agents      (slide_content & illustration)"; \
		echo "  7) 09_multi_agent_application  (paint_agent)"; \
		echo "=============================================================================="; \
		read -rp "Enter choice [1-7] or directory name (default: 1): " choice; \
		case "$$choice" in \
			2|02*|tool*)       TARGET_DIR="02_tool_agents" ;; \
			3|03*|workflow*)   TARGET_DIR="03_workflow_agents" ;; \
			4|04*|supervisor*) TARGET_DIR="04_supervisor_agent" ;; \
			5|05*|mcp*)        TARGET_DIR="05_mcp_agents" ;; \
			6|06*|a2a*)        TARGET_DIR="06_a2a_protocol_agents" ;; \
			7|09*|multi*|paint*) TARGET_DIR="09_multi_agent_application" ;; \
			q|quit|exit)       echo "[INFO] Canceled."; exit 0 ;; \
			1|01*|foundation*|*) TARGET_DIR="01_foundation_agents" ;; \
		esac; \
	elif [ -d "$$TARGET_DIR" ]; then \
		TARGET_DIR="$$TARGET_DIR"; \
	else \
		echo "[ERROR] Directory '$$TARGET_DIR' not found."; \
		echo "Available options: DIR=01_foundation_agents | DIR=02_tool_agents | DIR=03_workflow_agents | DIR=04_supervisor_agent | DIR=05_mcp_agents | DIR=06_a2a_protocol_agents | DIR=09_multi_agent_application"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "[INFO] Launching ADK Web Interface in $$TARGET_DIR on http://localhost:8000 ..."; \
	cd "$$TARGET_DIR" && $(ADK) web .

run-agent:
ifndef AGENT
	@echo "[ERROR] Please specify an agent name. Example: make run-agent AGENT=first_agent"
else
ifeq ($(AGENT),paint_agent)
	@echo "[INFO] Running $(AGENT) via ADK CLI in 09_multi_agent_application..."
	cd 09_multi_agent_application && $(ADK) run paint_agent
else
	@echo "[INFO] Running agent $(AGENT) via ADK CLI..."
	@if [ -d "01_foundation_agents/$(AGENT)" ]; then \
		$(ADK) run "01_foundation_agents/$(AGENT)"; \
	elif [ -d "02_tool_agents/$(AGENT)" ]; then \
		$(ADK) run "02_tool_agents/$(AGENT)"; \
	elif [ -d "03_workflow_agents/$(AGENT)" ]; then \
		$(ADK) run "03_workflow_agents/$(AGENT)"; \
	elif [ -d "04_supervisor_agent" ] && [ "$(AGENT)" = "sub_agents" -o "$(AGENT)" = "supervisor" -o "$(AGENT)" = "auditor" -o "$(AGENT)" = "04_supervisor_agent" ]; then \
		$(ADK) run "04_supervisor_agent"; \
	elif [ -d "05_mcp_agents/$(AGENT)" ]; then \
		$(ADK) run "05_mcp_agents/$(AGENT)"; \
	elif [ -d "06_a2a_protocol_agents/$(AGENT)" ]; then \
		$(ADK) run "06_a2a_protocol_agents/$(AGENT)"; \
	elif [ -d "$(AGENT)" ]; then \
		$(ADK) run "$(AGENT)"; \
	else \
		echo "[ERROR] Agent '$(AGENT)' not found."; exit 1; \
	fi
endif
endif

run-ui:
	@echo "[INFO] Starting Chainlit Web UI on http://localhost:8000 ..."
	cd 09_multi_agent_application/chainlit_ui && $(CHAINLIT) run app.py

clean:
	@echo "[INFO] Cleaning up bytecode and cache files (cross-platform)..."
	@$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [p.unlink(missing_ok=True) for p in pathlib.Path('.').rglob('*.py[cod]')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.pytest_cache')]" 2>/dev/null || true
	@echo "[OK] Cleanup complete."
