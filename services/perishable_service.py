# 文件名: services/perishable_service.py
from database import SessionLocal
from models import PerishableBatch, Product
from datetime import datetime, timedelta
from sqlalchemy import desc

class PerishableService:
    @staticmethod
    def add_batch(product_id, prod_date, shelf_life, qty):
        """
        添加易过期批次
        :param product_id: 商品编号
        :param prod_date: 生产日期 (date对象)
        :param shelf_life: 保质期天数
        :param qty: 批次数量
        :return: (success: bool, message: str)
        """
        session = SessionLocal()
        try:
            # 检查商品是否存在
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False, "商品不存在"

            # 计算过期日期
            expiration_date = prod_date + timedelta(days=shelf_life)

            # 创建批次记录
            batch = PerishableBatch(
                product_id=product_id,
                production_date=prod_date,
                shelf_life=shelf_life,
                expiration_date=expiration_date,
                quantity=qty,
                created_at=datetime.now()
            )
            session.add(batch)
            session.commit()
            return True, "批次登记成功"
        except Exception as e:
            session.rollback()
            return False, f"登记失败: {str(e)}"
        finally:
            session.close()

    @staticmethod
    def get_last_shelf_life(product_id):
        """
        获取该商品最近一次录入的保质期天数
        :param product_id: 商品编号
        :return: 保质期天数，如果没有历史记录则返回 None
        """
        session = SessionLocal()
        try:
            # 查询该商品最近一次的批次记录，按创建时间倒序
            latest_batch = session.query(PerishableBatch).filter(
                PerishableBatch.product_id == product_id
            ).order_by(desc(PerishableBatch.created_at)).first()

            if latest_batch:
                return latest_batch.shelf_life
            return None
        finally:
            session.close()

    @staticmethod
    def get_all_batches():
        """
        获取所有批次记录
        :return: PerishableBatch 对象列表
        """
        session = SessionLocal()
        try:
            return session.query(PerishableBatch).order_by(
                desc(PerishableBatch.created_at)
            ).all()
        finally:
            session.close()

    @staticmethod
    def check_expirations():
        """
        检查所有批次的过期状态
        :return: 列表，每个元素为字典 {batch_id, product_name, prod_date, shelf_life, exp_date, quantity, status, days_left}
        """
        session = SessionLocal()
        try:
            batches = session.query(PerishableBatch).all()
            result = []
            today = datetime.now().date()

            for batch in batches:
                # 获取商品名称
                product = session.query(Product).filter(Product.id == batch.product_id).first()
                product_name = product.name if product else "未知商品"

                # 计算剩余天数
                days_left = (batch.expiration_date - today).days

                # 判断状态
                if days_left < 0:
                    status = "已过期"
                elif days_left <= 7:
                    status = "临期"
                else:
                    status = "正常"

                result.append({
                    'batch_id': batch.id,  # v1.6: 添加batch_id用于删除和编辑
                    'product_name': product_name,
                    'production_date': batch.production_date,
                    'shelf_life': batch.shelf_life,
                    'expiration_date': batch.expiration_date,
                    'quantity': batch.quantity,
                    'status': status,
                    'days_left': days_left
                })

            return result
        finally:
            session.close()

    @staticmethod
    def delete_batch(batch_id):
        """
        v1.6: 删除指定批次
        :param batch_id: 批次ID
        :return: (success: bool, message: str)
        """
        session = SessionLocal()
        try:
            batch = session.query(PerishableBatch).filter(PerishableBatch.id == batch_id).first()
            if not batch:
                return False, "批次不存在"

            session.delete(batch)
            session.commit()
            return True, "批次删除成功"
        except Exception as e:
            session.rollback()
            return False, f"删除失败: {str(e)}"
        finally:
            session.close()

    @staticmethod
    def update_batch(batch_id, production_date, shelf_life, quantity):
        """
        v1.6: 更新批次信息
        :param batch_id: 批次ID
        :param production_date: 生产日期 (date对象)
        :param shelf_life: 保质期天数
        :param quantity: 批次数量
        :return: (success: bool, message: str)
        """
        session = SessionLocal()
        try:
            batch = session.query(PerishableBatch).filter(PerishableBatch.id == batch_id).first()
            if not batch:
                return False, "批次不存在"

            # 更新字段
            batch.production_date = production_date
            batch.shelf_life = shelf_life
            batch.quantity = quantity
            # 重新计算过期日期
            batch.expiration_date = production_date + timedelta(days=shelf_life)

            session.commit()
            return True, "批次更新成功"
        except Exception as e:
            session.rollback()
            return False, f"更新失败: {str(e)}"
        finally:
            session.close()
