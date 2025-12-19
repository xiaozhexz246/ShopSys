# 文件名: main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from init import init_db # 确保引入初始化函数
# 暂时注释掉，等后面写了 MainWindow 再启用
# from ui.main_window import MainWindow 

def main():
    init_db()
    # 1. 创建应用程序对象
    app = QApplication(sys.argv)

    # 2. 创建并显示登录窗口
    login_window = LoginWindow()
    login_window.show()

    # 3. 进入事件循环 (让窗口一直显示，直到手动关闭)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()