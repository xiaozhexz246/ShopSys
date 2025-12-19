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
        session = SessionLocal()
        try:
            # 1. 查找用户
            user = session.query(User).filter(User.username == username).first()
            
            if not user:
                return False
            
            # 2. 校验密码 (注意：必须和 init_db.py 里的加密方式一致)
            input_pwd_hash = hashlib.md5(password.encode()).hexdigest()
            
            if input_pwd_hash == user.password_hash:
                return True
            else:
                return False
        finally:
            session.close()