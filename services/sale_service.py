# 文件名: services/sale_service.py
from database import SessionLocal
from models import Product, SaleRecord
from datetime import datetime

class SaleService:
    @staticmethod
    def checkout(cart_items):
        """
        结算功能
        :param cart_items: 列表，格式 [{'id': '1001', 'qty': 2, 'price': 3.0}, ...]
        """
        session = SessionLocal()
        try:
            for item in cart_items:
                pid = item['id']
                qty = item['qty']
                price = item['price'] # 使用销售时的快照价格
                
                # 1. 查询商品并锁定 (简单查询)
                product = session.query(Product).filter(Product.id == pid).first()
                
                if not product:
                    raise Exception(f"商品 {pid} 不存在")
                
                if product.stock < qty:
                    raise Exception(f"商品 {product.name} 库存不足 (剩余 {product.stock})")
                
                # 2. 扣减库存
                product.stock -= qty
                
                # 3. 创建销售记录
                record = SaleRecord(
                    product_id=pid,
                    quantity=qty,
                    total_amount=qty * price,
                    sale_time=datetime.now()
                )
                session.add(record)
            
            # 4. 提交事务 (原子操作：要么全成功，要么全失败)
            session.commit()
            return True, "结算成功！"
            
        except Exception as e:
            session.rollback() # 出错回滚
            return False, str(e)
        finally:
            session.close()