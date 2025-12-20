# 文件名: main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.login_window import LoginWindow
from init import init_db # 确保引入初始化函数
# 暂时注释掉，等后面写了 MainWindow 再启用
# from ui.main_window import MainWindow 
def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境 """
    try:
        # PyInstaller 创建临时文件夹，路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 正常 Python 运行环境
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
def main():
    init_db()
    # 1. 创建应用程序对象
    app = QApplication(sys.argv)
    icon_path = resource_path("logo.ico") 
    app.setWindowIcon(QIcon(icon_path))
    # 2. 创建并显示登录窗口
    login_window = LoginWindow()
    login_window.show()

    # 3. 进入事件循环 (让窗口一直显示，直到手动关闭)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()