# 开发环境搭建

> [English](../INSTALL_DEV.md)

## 前置要求

- Python 3.10+
- Git

## 克隆与安装

```bash
git clone https://github.com/tophant-ai/ClawVault.git
cd ClawVault
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## 验证安装

```bash
claw-vault --version
claw-vault demo           # 交互式检测演示
claw-vault scan "sk-proj-abc123 password=secret 192.168.1.1"
```

## 运行测试

```bash
pytest
pytest --cov               # 带覆盖率
```

## 启动服务（本地）

```bash
claw-vault start           # 代理 :8765 + 仪表盘 :8766
```

- **代理**: `http://127.0.0.1:8765`
- **仪表盘**: `http://127.0.0.1:8766`

默认安全模式为 `permissive`（仅记录日志，不拦截）。可通过仪表盘 Config 页面切换，或：

```bash
claw-vault start --mode interactive
```

## 配置

```bash
claw-vault config init     # 从模板创建 ~/.ClawVault/config.yaml
claw-vault config show     # 显示当前配置
claw-vault config path     # 显示配置文件路径
```

编辑 `~/.ClawVault/config.yaml` 自定义配置。所有选项见 [`config.example.yaml`](../../config.example.yaml)。

## 代码风格

```bash
ruff check src/            # 代码检查
ruff format src/           # 代码格式化
mypy src/                  # 类型检查
```

## CLI 参考

```bash
claw-vault --help          # 所有命令
claw-vault start --help    # 启动选项
claw-vault scan --help     # 扫描选项
claw-vault skill list      # 列出可用 Skill
claw-vault skill export    # 导出 Skill 为 OpenAI function-calling JSON
