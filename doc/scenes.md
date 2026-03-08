# Claw-Vault Scenarios

> [中文版](./zh/scenarios.md)

## Overview

Claw-Vault acts as a security gateway ("vault") for AI tool traffic. It intercepts, inspects, and protects API calls between your AI tools and external providers.

**Current release scope:** Gateway interception + behavior monitoring + sensitive content detection.

## Implemented Scenarios

### A. Input Protection

| # | Scenario | Description |
|---|----------|-------------|
| A1 | **Sensitive Data Interception** | Detect API keys, passwords, private IPs, PII, connection strings in user messages |
| A2 | **Auto-Sanitize & Restore** | Replace secrets with placeholders before sending to AI; restore in response |
| A3 | **Prompt Injection Detection** | Detect role hijacking, instruction override, data exfiltration attempts |

**Example — A1 in action:**

```
User: "Connect to DB, password is MyP@ss, at 192.168.1.100"
 → Detected: password + private IP
 → Action depends on guard mode (block / sanitize / warn)
```

### B. Output Monitoring

| # | Scenario | Description |
|---|----------|-------------|
| B1 | **Response Safety Scan** | Detect dangerous commands or credential leaks in AI responses |
| B4 | **Dangerous Command Guard** | Intercept `rm -rf`, `curl|bash`, privilege escalation commands |

### C. Asset Protection

| # | Scenario | Description |
|---|----------|-------------|
| C1 | **Sensitive File Discovery** | Auto-discover `.env`, `.aws/credentials`, SSH keys, etc. |

### D. Observability

| # | Scenario | Description |
|---|----------|-------------|
| D1 | **Security Dashboard** | Real-time web UI with interception stats, events, agent config |
| D2 | **Token Budget Monitoring** | Daily/monthly token limits with cost alerts |

## Planned (Future Releases)

| Category | Scenarios |
|----------|-----------|
| **Input** | File upload scanning, context overflow protection |
| **Output** | Data exfiltration blocking, code leak prevention |
| **Asset** | Encrypted credential storage, API key lifecycle, multi-env isolation |
| **Observability** | Anomaly detection, compliance audit logs, alert push |
| **Advanced** | Session privacy mode, supply chain scanning, honeypot credentials, team audit |

## Roadmap

| Phase | Focus | Highlight |
|-------|-------|-----------|
| **v0.1 (current)** | A1 + A2 + A3 + B1 + B4 + C1 + D1 + D2 | "Install and protect" |
| **v0.2** | File scanning, data exfiltration blocking, skill permissions | "Full vault" |
| **v0.3+** | Encrypted storage, anomaly detection, team features | "Enterprise-ready" |
