# 文件名: models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
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
    category = Column(String, default="未设置")  # 商品类别
    location = Column(String, default="未设置")  # 存放位置

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
    profit = Column(Float, default=0.0) # 固化记录单笔交易的净利润 (v1.3新增)
    sale_time = Column(DateTime, default=datetime.now, index=True) # 自动记录当前时间，添加索引优化查询

    # 建立与 Product 的关联，方便查询时直接获取商品详情
    product = relationship("Product")

# --- 进货记录表 ---
class PurchaseRecord(Base):
    __tablename__ = "purchase_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)  # 进货数量
    cost_price = Column(Float, nullable=False)  # 当时的进价
    purchase_time = Column(DateTime, default=datetime.now, index=True)  # 进货时间

    # 关联到商品表
    product = relationship("Product")

# --- 易过期批次表 ---
class PerishableBatch(Base):
    __tablename__ = "perishable_batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    production_date = Column(Date, nullable=False)  # 生产日期
    shelf_life = Column(Integer, nullable=False)  # 保质期天数
    expiration_date = Column(Date, nullable=False)  # 过期日期
    quantity = Column(Integer, nullable=False)  # 该批次数量
    created_at = Column(DateTime, default=datetime.now, index=True)  # 记录创建时间

    # 关联到商品表
    product = relationship("Product")

# --- 操作日志表 (v2.2新增) ---
class OperationLog(Base):
    __tablename__ = 'operation_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)   # 操作人 (如: admin)
    module = Column(String, nullable=False)     # 模块 (如: 易过期管理)
    action = Column(String, nullable=False)     # 动作 (如: 修改批次)
    content = Column(String)                    # 详情 (如: 批次#5 数量 10 -> 8)
    log_time = Column(DateTime, default=datetime.now, index=True) # 时间