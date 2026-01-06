#!/bin/bash
# ============================================
# 数据库备份脚本
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="/var/backups/zentea-license"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "  ZenTea License 数据库备份"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
echo "[INFO] 正在备份数据库..."

docker exec zentea-license-db pg_dump \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    -F c \
    -f "/tmp/backup_${DATE}.dump"

docker cp "zentea-license-db:/tmp/backup_${DATE}.dump" "$BACKUP_DIR/"

# 清理容器内临时文件
docker exec zentea-license-db rm -f "/tmp/backup_${DATE}.dump"

# 保留最近 7 天的备份
find "$BACKUP_DIR" -name "backup_*.dump" -mtime +7 -delete

echo "[INFO] 备份完成: $BACKUP_DIR/backup_${DATE}.dump"

# 显示备份列表
echo ""
echo "最近备份："
ls -lh "$BACKUP_DIR"/*.dump 2>/dev/null | tail -5

