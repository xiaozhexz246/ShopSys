# 文件名: services/log_service.py
# v2.2: 全局日志服务
from database import SessionLocal
from models import OperationLog
from services.auth_service import AuthService
from datetime import datetime
from sqlalchemy import desc
import pandas as pd

class LogService:
    @staticmethod
    def add_log(module, action, content=""):
        """
        添加操作日志
        :param module: 模块名称 (如: 易过期管理)
        :param action: 操作类型 (如: 新增、修改、删除)
        :param content: 详细内容
        :return: (success: bool, message: str)
        """
        session = SessionLocal()
        try:
            # 获取当前用户 (如果未登录则记录为"系统/未登录")
            user = AuthService.current_user or "系统/未登录"

            # 创建日志记录
            log = OperationLog(
                username=user,
                module=module,
                action=action,
                content=content,
                log_time=datetime.now()
            )
            session.add(log)
            session.commit()
            return True, "日志记录成功"
        except Exception as e:
            session.rollback()
            return False, f"日志记录失败: {str(e)}"
        finally:
            session.close()

    @staticmethod
    def get_logs(keyword=None, limit=100):
        """
        查询日志记录
        :param keyword: 搜索关键词 (可选，支持用户名、模块、操作类型搜索)
        :param limit: 返回数量限制 (默认100条)
        :return: 日志记录列表
        """
        session = SessionLocal()
        try:
            query = session.query(OperationLog).order_by(desc(OperationLog.log_time))

            # 如果有关键词，进行模糊搜索
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.filter(
                    (OperationLog.username.like(search_pattern)) |
                    (OperationLog.module.like(search_pattern)) |
                    (OperationLog.action.like(search_pattern)) |
                    (OperationLog.content.like(search_pattern))
                )

            # 限制返回数量
            return query.limit(limit).all()
        finally:
            session.close()

    @staticmethod
    def export_logs_to_excel(save_path, keyword=None):
        """
        导出日志到 Excel 文件
        :param save_path: 保存文件路径 (如: "logs_2026.xlsx")
        :param keyword: 搜索关键词 (可选，导出符合条件的日志)
        :return: (success: bool, message: str)
        """
        session = SessionLocal()
        try:
            # 查询所有日志 (不限制数量，导出所有符合条件的)
            query = session.query(OperationLog).order_by(desc(OperationLog.log_time))

            # 如果有关键词，进行筛选
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.filter(
                    (OperationLog.username.like(search_pattern)) |
                    (OperationLog.module.like(search_pattern)) |
                    (OperationLog.action.like(search_pattern)) |
                    (OperationLog.content.like(search_pattern))
                )

            logs = query.all()

            if not logs:
                return False, "没有可导出的日志记录"

            # 转换为字典列表
            data = []
            for log in logs:
                data.append({
                    '操作时间': log.log_time.strftime('%Y-%m-%d %H:%M:%S'),
                    '操作人': log.username,
                    '模块': log.module,
                    '动作': log.action,
                    '详细内容': log.content or ""
                })

            # 使用 pandas 创建 DataFrame
            df = pd.DataFrame(data)

            # 导出到 Excel
            df.to_excel(save_path, index=False, engine='openpyxl')

            return True, f"成功导出 {len(logs)} 条日志记录"

        except Exception as e:
            return False, f"导出失败: {str(e)}"
        finally:
            session.close()
