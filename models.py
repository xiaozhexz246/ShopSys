# 文件名: models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# --- 管理员表 ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False) # 用户名唯一
    password_hash = Column(String, nullable=False)         # 存储加密后的密码

# --- 商品表 ---
class Product(Base):
    __tablename__ = "products"

    # 商品编号 (条形码)，设为主键，必须是字符串类型
    id = Column(String, primary_key=True, index=True) 
    name = Column(String, nullable=False)
    cost_price = Column(Float, default=0.0)  # 进价
    sell_price = Column(Float, default=0.0)  # 售价
    stock = Column(Integer, default=0)       # 库存

    # 关联关系：一个商品可能有多个销售记录
    # sales = relationship("SaleRecord", back_populates="product")

# --- 销售记录表 ---
class SaleRecord(Base):
    __tablename__ = "sale_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # 外键：关联到 Product 表的 id
    product_id = Column(String, ForeignKey("products.id"))
    
    quantity = Column(Integer, nullable=False) # 卖出数量
    total_amount = Column(Float, nullable=False) # 本单总金额 (单价 * 数量)
    sale_time = Column(DateTime, default=datetime.now) # 自动记录当前时间

    # 建立与 Product 的关联，方便查询时直接获取商品详情
    product = relationship("Product")