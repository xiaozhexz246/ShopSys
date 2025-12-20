# ui/hidden_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class HiddenPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("🔧 系统高级维护模式")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: red; margin: 20px;")
        layout.addWidget(title)

        # 功能按钮区域
        btn_clean = QPushButton("🗑️ 深度数据清洗")
        btn_clean.clicked.connect(lambda: QMessageBox.information(self, "提示", "数据清洗功能开发中..."))
        
        btn_reset = QPushButton("⚠️ 系统重置")
        btn_reset.clicked.connect(lambda: QMessageBox.warning(self, "警告", "系统重置功能暂未开放！"))

        btn_logs = QPushButton("📜 查看系统日志")
        btn_logs.clicked.connect(lambda: QMessageBox.information(self, "提示", "日志系统连接中..."))

        # 简单的样式美化
        for btn in [btn_clean, btn_reset, btn_logs]:
            btn.setFixedSize(200, 50)
            btn.setStyleSheet("font-size: 16px;")
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        self.setLayout(layout)