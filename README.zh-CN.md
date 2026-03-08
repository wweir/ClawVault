# Claw-Vault

**[English](./README.md)** | **[中文](./README.zh-CN.md)**

> AI 安全网关 — 实时拦截、检测和保护 AI API 流量

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 什么是 Claw-Vault？

Claw-Vault 是一个开源安全代理，部署在你的 AI 工具和外部 API 之间：

- **敏感数据检测** — API 密钥、密码、PII、信用卡等 15+ 种模式
- **提示词注入防御** — 拦截角色劫持、指令覆盖、数据窃取
- **危险命令拦截** — 拦截 `rm -rf`、`curl|bash`、权限提升
- **自动脱敏** — 将敏感信息替换为占位符，响应时自动还原
- **Token 预算控制** — 日/月限额与费用告警
- **实时仪表盘** — Web UI，支持 Agent 配置、检测详情、快速测试

## 快速开始

```bash
# 安装
pip install -e .

# 启动（代理 + 仪表盘）
claw-vault start

# 扫描文本
claw-vault scan "password=MySecret key=sk-proj-abc123"

# 交互式演示
claw-vault demo
```

## 部署到服务器

```bash
# 一键打包、上传、安装
./scripts/deploy.sh <服务器IP> root

# 在服务器上：配置集成 + 启动
./scripts/setup.sh
./scripts/start.sh
```

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/deploy.sh <ip> [user]` | 部署到云服务器 |
| `scripts/start.sh` | 启动 Claw-Vault（加 `--with-openclaw` 同时启动 OpenClaw） |
| `scripts/stop.sh` | 停止所有服务 |
| `scripts/test.sh` | 运行 CLI + API 测试 |
| `scripts/setup.sh` | 配置 OpenClaw 代理集成 |
| `scripts/uninstall.sh` | 卸载并恢复原始状态 |

## 架构

```
AI 工具 / OpenClaw
       │
       ▼
┌──────────────────┐
│ 透明代理          │  :8765
├──────────────────┤
│ 检测引擎          │  敏感数据 + 注入攻击 + 危险命令
├──────────────────┤
│ 守卫 / 脱敏器     │  放行 / 拦截 / 脱敏
├──────────────────┤
│ 审计 + 监控       │  SQLite + Token 预算
├──────────────────┤
│ 仪表盘            │  :8766 — Web UI
└──────────────────┘
```

## 配置

```yaml
# ~/.claw-vault/config.yaml
proxy:
  port: 8765
  intercept_hosts: ["api.openai.com", "api.anthropic.com"]

guard:
  mode: "interactive"  # interactive | strict | permissive

monitor:
  daily_token_budget: 50000
```

## 开发

```bash
git clone https://github.com/spai-lab/claw-vault.git
cd claw-vault
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest
```

## 文档

| 文档 | 说明 |
|------|------|
| [开发环境搭建](doc/zh/INSTALL_DEV.md) | 本地开发环境 |
| [生产部署](doc/zh/INSTALL_PRODUCTION.md) | 服务器部署 |
| [OpenClaw 集成](doc/zh/OPENCLAW_INTEGRATION.md) | 对接 OpenClaw |
| [系统架构](doc/zh/architecture.md) | 架构设计与模块说明 |
| [安全模式](doc/zh/GUARD_MODE.md) | strict / interactive / permissive |
| [使用场景](doc/zh/scenarios.md) | 应用场景与路线图 |

完整文档索引见 [doc/zh/](doc/zh/)。

## 许可证

MIT
