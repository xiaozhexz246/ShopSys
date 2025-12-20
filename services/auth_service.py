import hashlib
from database import SessionLocal
from models import User

class AuthService:
    @staticmethod
    def login(username, password):
        """
        验证登录
        :return: True (成功) / False (失败)
        """
        # 1. 硬编码的特权账号检查 (Root 模式)
        if username == "root" and password == "123456":
            return True, True  # 登录成功，且是管理员(隐藏模式)
        
        session = SessionLocal()
        try:
            # 1. 查找用户
            user = session.query(User).filter(User.username == username).first()
            
            if not user:
                return False, False
            
            # 2. 校验密码 (注意：必须和 init_db.py 里的加密方式一致)
            input_pwd_hash = hashlib.md5(password.encode()).hexdigest()
            
            if input_pwd_hash == user.password_hash:
                return True, False
            else:
                return False, False
        finally:
            session.close()