# 文件名: init_db.py
from database import engine, Base, SessionLocal
from models import User, Product, SaleRecord
import hashlib

def init_db():
    # 1. 创建所有表结构
    # 这一步会检查 models.py 里定义的所有类，并在数据库中创建对应表格
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表结构创建成功！")

    # 2. 检查并添加默认管理员
    session = SessionLocal()
    
    # 查询是否已经存在用户
    existing_user = session.query(User).filter(User.username == "admin").first()
    
    if not existing_user:
        print("👉 未检测到管理员，正在创建默认账号...")
        
        # 简单的密码加密 (这里用 MD5 仅作演示，实际生产建议用 bcrypt)
        pwd = "admin"
        pwd_hash = hashlib.md5(pwd.encode()).hexdigest()
        
        admin_user = User(username="admin", password_hash=pwd_hash)
        session.add(admin_user)
        session.commit()
        print("✅ 默认管理员已创建：账号 admin / 密码 admin")
    else:
        print("ℹ️ 管理员账号已存在，跳过创建。")
    
    session.close()

if __name__ == "__main__":
    init_db()