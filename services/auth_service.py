import hashlib
from database import SessionLocal
from models import User

class AuthService:
    # v2.2: 全局单例变量，记录当前登录用户
    current_user = None
    @staticmethod
    def login(username, password):
        """
        验证登录
        :return: True (成功) / False (失败)
        """
        # 1. 硬编码的特权账号检查 (Root 模式)
        if username == "root" and password == "123456":
            AuthService.current_user = username  # v2.2: 记录当前用户
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
                AuthService.current_user = username  # v2.2: 记录当前用户
                return True, False
            else:
                return False, False
        finally:
            session.close()

    @staticmethod
    def logout():
        """
        v2.2: 退出登录，清除当前用户
        """
        AuthService.current_user = None