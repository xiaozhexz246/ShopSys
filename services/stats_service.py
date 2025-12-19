# 文件名: services/stats_service.py
import pandas as pd
from sqlalchemy import func
from database import SessionLocal
from models import SaleRecord, Product

class StatsService:
    @staticmethod
    def get_daily_sales(start_date, end_date):
        """
        获取指定日期范围内的每日销售总额
        :return: DataFrame (包含日期和销售额)
        """
        session = SessionLocal()
        try:
            # 1. 基础查询：筛选日期范围
            # 注意：传入的 date 是 QDate 类型，需要转为 python datetime 或 string
            query = session.query(
                func.date(SaleRecord.sale_time).label('date'),
                func.sum(SaleRecord.total_amount).label('total')
            ).filter(
                SaleRecord.sale_time >= start_date,
                SaleRecord.sale_time <= end_date
            ).group_by(
                func.date(SaleRecord.sale_time)
            ).order_by(
                func.date(SaleRecord.sale_time)
            )

            # 2. 读取为 Pandas DataFrame
            df = pd.read_sql(query.statement, session.bind)
            return df
            
        except Exception as e:
            print(f"数据分析出错: {e}")
            return pd.DataFrame() # 出错返回空表
        finally:
            session.close()