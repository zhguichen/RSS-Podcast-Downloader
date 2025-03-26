#!/bin/bash

# 获取当前目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 设置Python路径（如果使用虚拟环境，确保使用正确的Python路径）
PYTHON_PATH="/root/ENTER/envs/MyDrive/bin/python3"

# 创建crontab任务 - 默认每天凌晨2点运行
# 修改下面的时间以适应你的需求
CRON_TIME="30 13 * * *"

# 创建cron任务
(crontab -l 2>/dev/null || echo "") | grep -v "$SCRIPT_DIR/download.py" | \
    cat - <(echo "$CRON_TIME cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_DIR/download.py") | \
    crontab -

echo "定时任务已设置，将在每天 $(echo $CRON_TIME | awk '{print $2}') 点 $(echo $CRON_TIME | awk '{print $1}') 分运行"
echo "使用 crontab -l 命令查看当前的cron任务"
echo "使用 crontab -e 命令编辑cron任务" 