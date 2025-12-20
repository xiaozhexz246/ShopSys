# 文件名: services/backup_service.py
import os
import shutil
from datetime import datetime, timedelta

class BackupService:
    BACKUP_DIR = "backups"
    DB_PATH = "shop.db"
    RETENTION_DAYS = 7  # 保留最近7天的备份

    @staticmethod
    def backup_db():
        """
        备份数据库文件
        :return: (成功标志, 消息)
        """
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(BackupService.DB_PATH):
                return False, "数据库文件不存在"

            # 创建备份目录（如果不存在）
            if not os.path.exists(BackupService.BACKUP_DIR):
                os.makedirs(BackupService.BACKUP_DIR)

            # 生成备份文件名（带时间戳）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BackupService.BACKUP_DIR, f"shop_{timestamp}.db")

            # 复制数据库文件
            shutil.copy2(BackupService.DB_PATH, backup_file)

            # 清理旧备份
            BackupService._cleanup_old_backups()

            return True, f"数据库已备份至: {backup_file}"

        except Exception as e:
            return False, f"备份失败: {str(e)}"

    @staticmethod
    def _cleanup_old_backups():
        """清理超过保留期限的旧备份文件"""
        try:
            if not os.path.exists(BackupService.BACKUP_DIR):
                return

            # 计算删除阈值时间
            threshold_time = datetime.now() - timedelta(days=BackupService.RETENTION_DAYS)

            # 遍历备份目录
            for filename in os.listdir(BackupService.BACKUP_DIR):
                if filename.startswith("shop_") and filename.endswith(".db"):
                    file_path = os.path.join(BackupService.BACKUP_DIR, filename)

                    # 获取文件修改时间
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # 如果文件早于阈值时间，则删除
                    if file_mtime < threshold_time:
                        os.remove(file_path)
                        print(f"已清理旧备份: {filename}")

        except Exception as e:
            print(f"清理旧备份时出错: {e}")

    @staticmethod
    def get_backup_list():
        """
        获取所有备份文件列表
        :return: 备份文件列表（按时间倒序）
        """
        try:
            if not os.path.exists(BackupService.BACKUP_DIR):
                return []

            backups = []
            for filename in os.listdir(BackupService.BACKUP_DIR):
                if filename.startswith("shop_") and filename.endswith(".db"):
                    file_path = os.path.join(BackupService.BACKUP_DIR, filename)
                    file_mtime = os.path.getmtime(file_path)
                    file_size = os.path.getsize(file_path)

                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'time': datetime.fromtimestamp(file_mtime),
                        'size': file_size
                    })

            # 按时间倒序排序
            backups.sort(key=lambda x: x['time'], reverse=True)
            return backups

        except Exception as e:
            print(f"获取备份列表时出错: {e}")
            return []
