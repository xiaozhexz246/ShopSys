# 文件名: ui/login_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from services.auth_service import AuthService

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("超市系统 - 登录")
        self.setFixedSize(360, 450) # v2.0: 稍微调大窗口以适应新间距

        # 布局管理器 (垂直布局)
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 50, 40, 50)  # 设置外边距
        layout.setSpacing(0)  # v2.0: 改为0，手动控制每个元素间距

        # 1. 标题
        title_label = QLabel("欢迎使用")
        title_label.setObjectName("login_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(40)  # v2.0: 标题下方间距增加到40px

        # 2. 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setObjectName("login_input")
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFixedHeight(45)
        self.username_input.returnPressed.connect(self.handle_login)  # 回车登录
        layout.addWidget(self.username_input)
        layout.addSpacing(15)  # v2.0: 输入框之间增加15px间距

        # 3. 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setObjectName("login_input")
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setFixedHeight(45)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # 隐藏密码字符
        self.password_input.returnPressed.connect(self.handle_login)  # 回车登录
        layout.addWidget(self.password_input)
        layout.addSpacing(30)  # v2.0: 登录按钮上方增加30px间距

        # 4. 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setObjectName("login_btn")
        self.login_btn.setFixedHeight(50)
        self.login_btn.clicked.connect(self.handle_login) # 绑定点击事件
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def handle_login(self):
        """处理点击登录后的逻辑"""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "提示", "用户名和密码不能为空！")
            return

        # 接收两个返回值
        success, is_admin = AuthService.login(username, password)
        # 调用 Service 层进行验证
        if success:
            # 登录成功
            # 注意：这里暂时只弹窗，下一阶段我们会在这里跳转到主界面
            QMessageBox.information(self, "成功", "登录验证通过！准备进入主界面...")
            from ui.main_window import MainWindow  # 延迟导入
            self.main_window = MainWindow(is_hidden_mode=is_admin)
            self.main_window.show()
            self.close() # 关闭登录窗口
        else:
            QMessageBox.critical(self, "错误", "用户名或密码错误！")