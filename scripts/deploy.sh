#!/bin/bash
# 一键部署并安装脚本（包含服务器端安装步骤）
# 使用方法: ./deploy_and_install.sh <server_ip> [server_user]

set -e

SERVER_IP="$1"
SERVER_USER="${2:-root}"
SERVER_PATH="/root/prj/claw-vault"
VENV_PATH="$SERVER_PATH/venv"
ARCHIVE_NAME="claw-vault.zip"

if [ -z "$SERVER_IP" ]; then
    echo "错误: 请提供服务器IP地址"
    echo "使用方法: $0 <server_ip> [server_user]"
    echo "示例: $0 123.45.67.89 root"
    exit 1
fi

echo "========================================"
echo "Claw-Vault 一键部署和安装"
echo "========================================"
echo "服务器: $SERVER_USER@$SERVER_IP"
echo "目标路径: $SERVER_PATH"
echo "========================================"
echo ""

# 步骤 1-4: 打包和上传（复用 deploy_to_server.sh 的逻辑）
echo "[1/6] 清理旧的打包文件..."
rm -f "$ARCHIVE_NAME"
rm -rf claw-vault-deploy

echo "[2/6] 准备项目文件..."
mkdir -p claw-vault-deploy
cp -r src claw-vault-deploy/
cp -r tests claw-vault-deploy/
cp -r doc claw-vault-deploy/
cp -r scripts claw-vault-deploy/
chmod +x claw-vault-deploy/scripts/*.sh 2>/dev/null || true
cp pyproject.toml claw-vault-deploy/
cp README.md claw-vault-deploy/
cp LICENSE claw-vault-deploy/
cp config.example.yaml claw-vault-deploy/
[ -f .gitignore ] && cp .gitignore claw-vault-deploy/

find claw-vault-deploy -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find claw-vault-deploy -name "*.pyc" -delete 2>/dev/null || true

echo "[3/6] 打包项目..."
cd claw-vault-deploy && zip -r "../$ARCHIVE_NAME" . -x "*.DS_Store" -x "__MACOSX/*" && cd ..

echo "[4/6] 上传到服务器..."
scp "$ARCHIVE_NAME" "$SERVER_USER@$SERVER_IP:/tmp/"

# 步骤 5-6: 在服务器上解压、创建虚拟环境并安装
echo "[5/6] 在服务器上解压..."
ssh "$SERVER_USER@$SERVER_IP" << ENDSSH
set -e
echo "→ 创建目录并解压..."
mkdir -p $SERVER_PATH
cd $SERVER_PATH
unzip -q -o /tmp/$ARCHIVE_NAME
rm /tmp/$ARCHIVE_NAME
echo "✓ 解压完成"
ENDSSH

echo "[6/6] 在服务器上安装..."
ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
set -e
cd /root/prj/claw-vault

echo "→ 检查 Python 版本..."
python3 --version

echo "→ 检查系统依赖..."
# 检测操作系统类型
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    if ! dpkg -l | grep -q python3-venv; then
        echo "  安装 python3-venv..."
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y python3-venv python3-pip > /dev/null 2>&1
        echo "✓ 系统依赖已安装"
    else
        echo "✓ 系统依赖已满足"
    fi
elif [ -f /etc/redhat-release ]; then
    # CentOS/RHEL
    if ! rpm -q python3-virtualenv > /dev/null 2>&1; then
        echo "  安装 python3-virtualenv..."
        yum install -y python3-virtualenv > /dev/null 2>&1
        echo "✓ 系统依赖已安装"
    else
        echo "✓ 系统依赖已满足"
    fi
fi

echo "→ 创建虚拟环境..."
# 检查虚拟环境是否存在且完整
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "  虚拟环境已存在且完整"
else
    if [ -d "venv" ]; then
        echo "  检测到损坏的虚拟环境，重新创建..."
        rm -rf venv
    fi
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
fi

echo "→ 激活虚拟环境并安装..."
source venv/bin/activate

echo "→ 升级 pip..."
pip install --upgrade pip setuptools wheel -q

echo "→ 安装 Claw-Vault（开发模式）..."
pip install -e . -q

echo "→ 验证安装..."
claw-vault --version

echo ""
echo "✅ 安装完成！"
echo ""
echo "可用命令:"
echo "  claw-vault --version"
echo "  claw-vault scan 'test text'"
echo "  claw-vault demo"
echo "  claw-vault start"
ENDSSH

# 清理本地临时文件
echo ""
echo "[清理] 删除本地临时文件..."
rm -rf claw-vault-deploy
rm -f "$ARCHIVE_NAME"

echo ""
echo "========================================"
echo "✅ 部署和安装完成！"
echo "========================================"
echo ""
echo "登录服务器测试:"
echo "  ssh $SERVER_USER@$SERVER_IP"
echo "  cd $SERVER_PATH"
echo "  source venv/bin/activate"
echo "  claw-vault --version"
echo ""
echo "运行快速测试:"
echo "  ./scripts/test.sh"
echo ""
