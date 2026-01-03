# 文件名: services/product_service.py
from database import SessionLocal
from models import Product, PurchaseRecord
from datetime import datetime
from services.log_service import LogService

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
    def add_product(id, name, cost, price, stock, category="未设置", location="未设置"):
        """添加新商品"""
        session = SessionLocal()
        try:
            # 检查编号是否重复
            existing = session.query(Product).filter(Product.id == id).first()
            if existing:
                return False, "商品编号已存在！"

            new_product = Product(
                id=id, name=name,
                cost_price=cost, sell_price=price, stock=stock,
                category=category, location=location
            )
            session.add(new_product)
            session.commit()

            # v2.2: 添加日志记录
            LogService.add_log(
                "商品管理",
                "新增商品",
                f"新增商品: {name} (编号:{id})"
            )

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
                product_name = product.name
                session.delete(product)
                session.commit()

                # v2.2: 添加日志记录
                LogService.add_log(
                    "商品管理",
                    "删除商品",
                    f"删除商品: {product_name} (编号:{product_id})"
                )

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

    @staticmethod
    def replenish_stock(cart_items):
        """
        进货入库
        :param cart_items: 进货清单列表，格式 [{"product_id": "xxx", "quantity": 10, "cost_price": 5.5}, ...]
        :return: (success: bool, message: str)
        """
        session = SessionLocal()
        try:
            # v2.2: 收集进货详细信息用于日志记录
            purchase_details = []
            total_qty = 0

            for item in cart_items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                cost_price = item["cost_price"]

                # 查找商品
                product = session.query(Product).filter(Product.id == product_id).first()
                if not product:
                    session.rollback()
                    return False, f"商品编号 {product_id} 不存在"

                # 更新库存
                product.stock += quantity

                # 更新进价（如果有变动）
                product.cost_price = cost_price

                # 插入进货记录
                purchase_record = PurchaseRecord(
                    product_id=product_id,
                    quantity=quantity,
                    cost_price=cost_price,
                    purchase_time=datetime.now()
                )
                session.add(purchase_record)

                # v2.2: 收集商品信息用于日志
                purchase_details.append(f"{product.name}(进价¥{cost_price:.2f}×{quantity}件)")
                total_qty += quantity

            session.commit()

            # v2.2: 添加详细日志记录
            detail_str = "、".join(purchase_details)
            LogService.add_log(
                "进货管理",
                "进货入库",
                f"进货入库: {detail_str}，共{total_qty}件"
            )

            return True, "进货成功"
        except Exception as e:
            session.rollback()
            return False, f"进货失败: {str(e)}"
        finally:
            session.close()

    @staticmethod
    def update_product(product_id, name, category, location, cost, price):
        """
        更新商品信息
        :param product_id: 商品编号
        :param name: 商品名称
        :param category: 类别
        :param location: 位置
        :param cost: 进价
        :param price: 售价
        :return: (success: bool, message: str)
        """
        session = SessionLocal()
        try:
            # 查找商品
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False, "商品不存在"

            # 更新信息
            product.name = name
            product.category = category
            product.location = location
            product.cost_price = cost
            product.sell_price = price

            session.commit()

            # v2.2: 添加日志记录
            LogService.add_log(
                "商品管理",
                "修改商品",
                f"修改商品: {name} (编号:{product_id}) 进价{cost} 售价{price}"
            )

            return True, "更新成功"
        except Exception as e:
            session.rollback()
            return False, f"更新失败: {str(e)}"
        finally:
            session.close()