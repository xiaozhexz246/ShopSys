# 文件名: database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import sys

DB_NAME = "shop.db"
# --- 修改路径逻辑 ---
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe 运行时，基准路径是 exe 文件所在的目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是 Python 脚本运行时，基准路径是当前脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_URL = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"
# 1. 创建引擎 (Engine)
# echo=False 表示不打印所有的 SQL 语句，开发调试时可改为 True
engine = create_engine(DB_URL, echo=False)

# 2. 创建会话工厂 (SessionLocal)
# 后续所有的数据库增删改查都通过 SessionLocal() 创建的会话进行
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 创建基类 (Base)
# 所有的模型类（Model）都要继承这个基类
Base = declarative_base()

# 辅助函数：获取数据库会话（主要用于后续可能的上下文管理）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()