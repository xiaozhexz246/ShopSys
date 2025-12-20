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
        self.setFixedSize(300, 200) # 固定窗口大小

        # 布局管理器 (垂直布局)
        layout = QVBoxLayout()

        # 1. 标题
        title_label = QLabel("欢迎使用")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 2. 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        layout.addWidget(self.username_input)

        # 3. 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # 隐藏密码字符
        layout.addWidget(self.password_input)

        # 4. 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet("background-color: #0078d7; color: white; height: 30px;")
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