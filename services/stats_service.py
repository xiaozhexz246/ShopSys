# 文件名: services/stats_service.py
import pandas as pd
import os
from datetime import datetime
from sqlalchemy import func
from database import SessionLocal
from models import SaleRecord, Product

class StatsService:
    @staticmethod
    def get_sales_and_profit_trend(start_date, end_date):
        """
        获取指定日期范围内的每日销售额和利润趋势
        :return: DataFrame (包含日期、销售额、利润)
        """
        session = SessionLocal()
        try:
            # v1.3优化：直接对 profit 字段求和，无需联表查询进价
            query = session.query(
                func.date(SaleRecord.sale_time).label('date'),
                func.sum(SaleRecord.total_amount).label('revenue'),
                func.sum(SaleRecord.profit).label('profit')
            ).filter(
                SaleRecord.sale_time >= start_date,
                SaleRecord.sale_time <= end_date
            ).group_by(
                func.date(SaleRecord.sale_time)
            ).order_by(
                func.date(SaleRecord.sale_time)
            )

            df = pd.read_sql(query.statement, session.bind)
            return df

        except Exception as e:
            print(f"数据分析出错: {e}")
            return pd.DataFrame()
        finally:
            session.close()

    @staticmethod
    def get_category_stats(start_date, end_date):
        """
        获取指定日期范围内各商品类别的销售统计
        :return: DataFrame (包含类别、销售额)
        """
        session = SessionLocal()
        try:
            # 需要联表 Product 获取类别信息
            query = session.query(
                Product.category.label('category'),
                func.sum(SaleRecord.total_amount).label('revenue')
            ).join(
                Product, SaleRecord.product_id == Product.id
            ).filter(
                SaleRecord.sale_time >= start_date,
                SaleRecord.sale_time <= end_date
            ).group_by(
                Product.category
            ).order_by(
                func.sum(SaleRecord.total_amount).desc()
            )

            df = pd.read_sql(query.statement, session.bind)
            return df

        except Exception as e:
            print(f"类别统计出错: {e}")
            return pd.DataFrame()
        finally:
            session.close()

    @staticmethod
    def get_top_products(start_date, end_date, limit=10):
        """
        获取指定日期范围内的热销商品排行
        :param limit: 返回前N个商品
        :return: DataFrame (包含商品名、销售数量)
        """
        session = SessionLocal()
        try:
            query = session.query(
                Product.name.label('product_name'),
                func.sum(SaleRecord.quantity).label('total_quantity'),
                func.sum(SaleRecord.total_amount).label('revenue')
            ).join(
                Product, SaleRecord.product_id == Product.id
            ).filter(
                SaleRecord.sale_time >= start_date,
                SaleRecord.sale_time <= end_date
            ).group_by(
                Product.name
            ).order_by(
                func.sum(SaleRecord.quantity).desc()
            ).limit(limit)

            df = pd.read_sql(query.statement, session.bind)
            return df

        except Exception as e:
            print(f"热销排行统计出错: {e}")
            return pd.DataFrame()
        finally:
            session.close()

    @staticmethod
    def get_total_stats(start_date, end_date):
        """
        获取指定日期范围内的总营收和总利润
        :return: dict {'total_revenue': xxx, 'total_profit': xxx}
        """
        session = SessionLocal()
        try:
            # v1.3优化：直接对 profit 字段求和
            result = session.query(
                func.sum(SaleRecord.total_amount).label('total_revenue'),
                func.sum(SaleRecord.profit).label('total_profit')
            ).filter(
                SaleRecord.sale_time >= start_date,
                SaleRecord.sale_time <= end_date
            ).first()

            return {
                'total_revenue': result.total_revenue or 0.0,
                'total_profit': result.total_profit or 0.0
            }

        except Exception as e:
            print(f"总计统计出错: {e}")
            return {'total_revenue': 0.0, 'total_profit': 0.0}
        finally:
            session.close()

    # 保留旧的方法以兼容现有代码
    @staticmethod
    def get_daily_sales(start_date, end_date):
        """
        获取指定日期范围内的每日销售总额 (兼容旧版)
        :return: DataFrame (包含日期和销售额)
        """
        return StatsService.get_sales_and_profit_trend(start_date, end_date)[['date', 'revenue']].rename(columns={'revenue': 'total'})

    @staticmethod
    def get_raw_sales_records(start_date, end_date):
        """
        获取指定日期范围内的原始销售记录（用于明细查询和导出）
        :return: DataFrame (包含销售记录所有字段)
        """
        session = SessionLocal()
        try:
            # 联表查询 SaleRecord 和 Product，获取完整信息
            query = session.query(
                SaleRecord.id.label('流水号'),
                Product.name.label('商品名称'),
                Product.category.label('类别'),
                SaleRecord.total_amount.label('总金额'),
                SaleRecord.quantity.label('数量'),
                SaleRecord.profit.label('利润'),
                SaleRecord.sale_time.label('时间'),
                Product.id.label('商品编号')
            ).join(
                Product, SaleRecord.product_id == Product.id
            ).filter(
                SaleRecord.sale_time >= start_date,
                SaleRecord.sale_time <= end_date
            ).order_by(
                SaleRecord.sale_time.desc()
            )

            df = pd.read_sql(query.statement, session.bind)
            return df

        except Exception as e:
            print(f"获取销售明细出错: {e}")
            return pd.DataFrame()
        finally:
            session.close()

    @staticmethod
    def export_to_excel(dataframe):
        """
        将 DataFrame 导出为 Excel 文件
        :param dataframe: 要导出的数据
        :return: (成功标志, 保存路径或错误信息)
        """
        try:
            # 检查并创建 backups/sells/ 文件夹
            export_dir = "backups/sells"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)

            # 生成时间戳文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_record_{timestamp}.xlsx"
            filepath = os.path.join(export_dir, filename)

            # 导出到 Excel
            dataframe.to_excel(filepath, index=False, engine='openpyxl')

            return True, filepath

        except Exception as e:
            print(f"导出 Excel 出错: {e}")
            return False, f"导出失败: {str(e)}"
