# Development Setup

> [中文版](./zh/INSTALL_DEV.md)

## Prerequisites

- Python 3.10+
- Git

## Clone & Install

```bash
git clone https://github.com/tophant-ai/ClawVault.git
cd ClawVault
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Verify

```bash
claw-vault --version
claw-vault demo           # Interactive detection demo
claw-vault scan "sk-proj-abc123 password=secret 192.168.1.1"
```

## Run Tests

```bash
pytest
pytest --cov               # With coverage
```

## Start Services (Local)

```bash
claw-vault start           # Proxy :8765 + Dashboard :8766
```

- **Proxy**: `http://127.0.0.1:8765`
- **Dashboard**: `http://127.0.0.1:8766`

Default guard mode is `permissive` (pass-through + logging). Change via Dashboard Config tab or:

```bash
claw-vault start --mode interactive
```

## Configuration

```bash
claw-vault config init     # Create ~/.claw-vault/config.yaml from template
claw-vault config show     # Show current settings
claw-vault config path     # Show config file location
```

Edit `~/.claw-vault/config.yaml` to customize. See [`config.example.yaml`](../config.example.yaml) for all options.

## Code Style

```bash
ruff check src/            # Lint
ruff format src/           # Format
mypy src/                  # Type check
```

## CLI Reference

```bash
claw-vault --help          # All commands
claw-vault start --help    # Start options
claw-vault scan --help     # Scan options
claw-vault skill list      # List available skills
claw-vault skill export    # Export skills as OpenAI function-calling JSON
