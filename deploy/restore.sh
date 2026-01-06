#!/bin/bash
# ============================================
# 数据库恢复脚本
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="/var/backups/zentea-license"

echo "=========================================="
echo "  ZenTea License 数据库恢复"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

# 列出可用备份
echo "可用备份："
ls -lh "$BACKUP_DIR"/*.dump 2>/dev/null || {
    echo "[ERROR] 没有找到备份文件"
    exit 1
}

echo ""
read -p "请输入要恢复的备份文件名: " BACKUP_FILE

BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

if [ ! -f "$BACKUP_PATH" ]; then
    echo "[ERROR] 备份文件不存在: $BACKUP_PATH"
    exit 1
fi

echo ""
echo "[WARN] 恢复操作将覆盖当前数据库数据！"
read -p "确定要继续吗？(yes/no) " confirm

if [ "$confirm" != "yes" ]; then
    echo "已取消"
    exit 0
fi

echo "[INFO] 正在恢复数据库..."

# 复制备份到容器
docker cp "$BACKUP_PATH" "zentea-license-db:/tmp/restore.dump"

# 恢复数据库
docker exec zentea-license-db pg_restore \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    -c \
    "/tmp/restore.dump"

# 清理
docker exec zentea-license-db rm -f "/tmp/restore.dump"

echo "[INFO] 数据库恢复完成"

