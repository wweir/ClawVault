# Claw-Vault Documentation

> [中文版](./zh/README.md)

## Getting Started

| Document | Description |
|----------|-------------|
| [INSTALL_DEV.md](./INSTALL_DEV.md) | Development environment setup |
| [INSTALL_PRODUCTION.md](./INSTALL_PRODUCTION.md) | Production server deployment |
| [OPENCLAW_INTEGRATION.md](./OPENCLAW_INTEGRATION.md) | OpenClaw integration guide |

## Reference

| Document | Description |
|----------|-------------|
| [architecture.md](./architecture.md) | System architecture and module design |
| [scenarios.md](./scenes.md) | Use cases and roadmap |
| [GUARD_MODE.md](./GUARD_MODE.md) | Guard modes: strict / interactive / permissive |

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/deploy.sh <ip> [user]` | Deploy to cloud server |
| `scripts/start.sh` | Start Claw-Vault (add `--with-openclaw` for OpenClaw) |
| `scripts/stop.sh` | Stop all services |
| `scripts/test.sh` | Run CLI + API tests |
| `scripts/setup.sh` | Configure OpenClaw proxy integration |
| `scripts/uninstall.sh` | Uninstall and restore |

## Archive

Historical documents and deprecated scripts are in [`archive/`](./archive/).

---

**Last updated**: 2026-03-09
