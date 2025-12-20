# 文件名: ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QToolBar,
                             QStackedWidget, QLabel, QMessageBox)
from PyQt6.QtGui import QAction
from ui.inventory_page import InventoryPage
from ui.cashier_page import CashierPage
from ui.stats_page import StatsPage
from ui.hidden_page import HiddenPage
from services.backup_service import BackupService
class MainWindow(QMainWindow):
    def __init__(self,is_hidden_mode=False):
        super().__init__()
        self.is_hidden_mode = is_hidden_mode
        self.setWindowTitle("超市售货系统 v1.3")
        self.resize(1000, 600) # 默认大小

        # 1. 创建核心容器 (堆叠窗口，用来切换页面)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # 2. 初始化各个页面
        self.page_inventory = InventoryPage()
        self.page_cashier = CashierPage()
        self.page_stats = StatsPage()     # 后面开发

        # 3. 把页面加入堆叠容器
        self.stack.addWidget(self.page_inventory) # 索引 0
        self.stack.addWidget(self.page_cashier)# 索引1
        self.stack.addWidget(self.page_stats) # Index 2 
        # --- 核心修改：如果是隐藏模式，加载隐藏页面 ---
        if self.is_hidden_mode:
            self.page_hidden = HiddenPage()
            self.stack.addWidget(self.page_hidden) # Index 3
        # 4. 创建顶部工具栏 (导航栏)
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = QToolBar("导航栏")
        toolbar.setMovable(False) # 锁定工具栏不让拖动
        self.addToolBar(toolbar)

        # --- 添加动作按钮 ---
        # 动作 1: 收银台 (暂时占位)
        action_cashier = QAction("💰 收银台", self)
        # 点击切换到 Index 1 (CashierPage)
        action_cashier.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_cashier))
        toolbar.addAction(action_cashier)

        # 动作 2: 商品管理
        action_inventory = QAction("📦 商品管理", self)
        # 点击切换到 Index 0 (InventoryPage)
        action_inventory.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_inventory))
        toolbar.addAction(action_inventory)

        # 动作 3: 销售报表
        action_stats = QAction("📈 销售报表", self)
        # 点击切换到 Index 2
        action_stats.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_stats))
        toolbar.addAction(action_stats)
        if self.is_hidden_mode:
            action_hidden = QAction("🔧 系统维护", self)
            action_hidden.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_hidden))
            # 给个特殊的颜色或图标（这里简单用文字区分）
            toolbar.addAction(action_hidden)

        # 动作 4: 退出
        action_exit = QAction("❌ 退出系统", self)
        action_exit.triggered.connect(self.close)
        toolbar.addAction(action_exit)

    def closeEvent(self, event):
        """窗口关闭事件：执行自动备份"""
        try:
            # v1.3新增：退出时自动备份数据库
            success, message = BackupService.backup_db()
            if success:
                print(f"✅ {message}")
            else:
                print(f"⚠️ 备份失败: {message}")
        except Exception as e:
            print(f"⚠️ 备份过程出错: {e}")
        finally:
            # 无论备份是否成功，都允许关闭窗口
            event.accept()