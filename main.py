# 文件名: main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.login_window import LoginWindow
from init import init_db

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
    # 1. 初始化数据库
    init_db()
    
    # 2. 创建应用程序对象
    app = QApplication(sys.argv)
    
    # 设置应用图标
    icon_path = resource_path("logo.ico") 
    app.setWindowIcon(QIcon(icon_path))

    # ================= 关键添加：加载全局 QSS 样式表 =================
    # 使用 resource_path 确保打包后也能找到样式文件
    # 注意：确保你的目录结构是 assets/styles.qss
    qss_path = resource_path(os.path.join("assets", "styles.qss"))
    
    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                style_content = f.read()
                app.setStyleSheet(style_content) # 核心步骤：将样式应用到整个 App
                print(f"✅ 成功加载样式表: {qss_path}")
        except Exception as e:
            print(f"❌ 读取样式表失败: {e}")
    else:
        print(f"⚠️ 未找到样式表文件，请检查路径: {qss_path}")
    # ==============================================================

    # 3. 创建并显示登录窗口
    login_window = LoginWindow()
    login_window.show()

    # 4. 进入事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()