# 文件名: services/product_service.py
from database import SessionLocal
from models import Product

class ProductService:
    @staticmethod
    def get_all_products():
        """获取所有商品列表"""
        session = SessionLocal()
        try:
            return session.query(Product).all()
        finally:
            session.close()

    @staticmethod
    def add_product(id, name, cost, price, stock):
        """添加新商品"""
        session = SessionLocal()
        try:
            # 检查编号是否重复
            existing = session.query(Product).filter(Product.id == id).first()
            if existing:
                return False, "商品编号已存在！"
            
            new_product = Product(
                id=id, name=name, 
                cost_price=cost, sell_price=price, stock=stock
            )
            session.add(new_product)
            session.commit()
            return True, "添加成功"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
            
    # 后续会添加 update 和 delete 方法
    @staticmethod
    def delete_product(product_id):
        """删除指定编号的商品"""
        session = SessionLocal()
        try:
            # 查找
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                session.delete(product)
                session.commit()
                return True, "删除成功"
            return False, "商品不存在"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    @staticmethod
    def get_product_by_id(product_id):
        """根据ID查找单个商品"""
        session = SessionLocal()
        try:
            return session.query(Product).filter(Product.id == product_id).first()
        finally:
            session.close()
    @staticmethod
    def search_products_by_name(keyword):
        """
        根据商品名称模糊搜索
        :param keyword: 搜索关键字
        :return: Product 对象列表
        """
        session = SessionLocal()
        try:
            # 使用 ILIKE (如果不区分大小写) 或者 LIKE
            # SQLite 默认 LIKE 不区分大小写 (对 ASCII 字符)
            return session.query(Product).filter(Product.name.like(f"%{keyword}%")).all()
        finally:
            session.close()