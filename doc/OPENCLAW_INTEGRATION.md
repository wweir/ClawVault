# OpenClaw Integration Guide

> [中文版](./zh/OPENCLAW_INTEGRATION.md)

This guide explains how to connect Claw-Vault with [OpenClaw](https://github.com/spai-lab/openclaw) so that all AI API traffic from OpenClaw is automatically intercepted and protected.

## How It Works

```
OpenClaw IDE  →  HTTP_PROXY  →  Claw-Vault Proxy (:8765)  →  AI Provider APIs
                                      │
                                 Detection Engine
                                 (sensitive data, injection, commands)
                                      │
                                 Dashboard (:8766)
```

Claw-Vault runs as a transparent HTTP proxy. By setting `HTTP_PROXY` / `HTTPS_PROXY` environment variables for OpenClaw, all outgoing AI API requests pass through Claw-Vault for inspection.

## Prerequisites

- Claw-Vault installed and working ([Production](./INSTALL_PRODUCTION.md) or [Development](./INSTALL_DEV.md))
- OpenClaw installed on the same server

## Automatic Setup

The `setup.sh` script configures everything automatically:

```bash
cd ~/prj/claw-vault
source venv/bin/activate
./scripts/setup.sh
```

This script will:
1. Verify Claw-Vault is installed
2. Inject proxy environment variables into `openclaw-gateway.service` (systemd)
3. Initialize Claw-Vault config with `ssl_verify: false`

## Start with OpenClaw

```bash
# Start Claw-Vault, then auto-restart openclaw-gateway with proxy configured
./scripts/start.sh

# Or start Claw-Vault + launch OpenClaw TUI together
./scripts/start.sh --with-openclaw
```

## Manual Setup

If you prefer manual configuration or don't use systemd:

### 1. Start Claw-Vault

```bash
cd ~/prj/claw-vault
source venv/bin/activate
claw-vault start --dashboard-host 0.0.0.0
```

### 2. Set Proxy Environment Variables

Before starting OpenClaw, set these environment variables:

```bash
export HTTP_PROXY=http://127.0.0.1:8765
export HTTPS_PROXY=http://127.0.0.1:8765
export NO_PROXY=localhost,127.0.0.1
export NODE_TLS_REJECT_UNAUTHORIZED=0
```

### 3. Start OpenClaw

```bash
openclaw
```

All AI API calls from OpenClaw will now pass through Claw-Vault.

## Verify Integration

1. Open the Claw-Vault Dashboard: `http://<server-ip>:8766`
2. Use OpenClaw to send a message to an AI provider
3. Check the **Events** tab — you should see the intercepted request
4. Try sending a message containing a test secret (e.g. `sk-proj-test123`) and observe the detection

## Guard Mode for OpenClaw

Recommended modes:

| Environment | Guard Mode | Auto-Sanitize | Notes |
|-------------|-----------|---------------|-------|
| Development | `permissive` | off | Log only, no interference |
| Staging | `interactive` | on | Auto-sanitize secrets transparently |
| Production | `strict` | — | Block all threats |

Switch via Dashboard Config tab or API:

```bash
curl -X POST http://localhost:8766/api/config/guard \
  -H 'Content-Type: application/json' \
  -d '{"mode": "interactive", "auto_sanitize": true}'
```

## Supported AI Providers

Claw-Vault intercepts traffic to these hosts by default (configurable in `config.yaml`):

- `api.openai.com`
- `api.anthropic.com`
- `api.siliconflow.cn`
- `*.openai.azure.com`
- `generativelanguage.googleapis.com`

Add more hosts in `~/.claw-vault/config.yaml`:

```yaml
proxy:
  intercept_hosts:
    - "api.openai.com"
    - "api.anthropic.com"
    - "your-custom-endpoint.com"
```

## Troubleshooting

**OpenClaw not using proxy**: Ensure proxy env vars are set before OpenClaw starts. For systemd services, run `./scripts/setup.sh` to inject them.

**SSL/TLS errors**: Set `ssl_verify: false` in config and `NODE_TLS_REJECT_UNAUTHORIZED=0` in the OpenClaw environment.

**Proxy not reachable**: Confirm Claw-Vault is running:
```bash
curl -s http://127.0.0.1:8766/api/health
```

**Restart OpenClaw after config changes**:
```bash
systemctl --user restart openclaw-gateway
```
