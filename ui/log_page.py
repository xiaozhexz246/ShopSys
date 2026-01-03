# 文件名: ui/log_page.py
# v2.2: 系统日志查询界面
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QLabel, QGroupBox, QAbstractItemView,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from services.log_service import LogService
from datetime import datetime

class LogPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_logs()  # 初始加载日志

    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout()

        # 创建日志查询区域
        self.init_log_area(main_layout)

        self.setLayout(main_layout)

    def init_log_area(self, parent_layout):
        """初始化日志查询区域"""
        group_box = QGroupBox("系统操作日志")
        layout = QVBoxLayout()

        # 顶部搜索栏
        search_layout = QHBoxLayout()

        # 搜索框
        search_label = QLabel("搜索:")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索 (操作人/模块/动作/内容)")
        self.search_input.setFixedWidth(300)
        self.search_input.returnPressed.connect(self.search_logs)  # 回车触发搜索
        search_layout.addWidget(self.search_input)

        # 搜索按钮
        btn_search = QPushButton("🔍 搜索")
        btn_search.setProperty("class", "primary")
        btn_search.setFixedSize(100, 32)
        btn_search.clicked.connect(self.search_logs)
        search_layout.addWidget(btn_search)

        # 刷新按钮
        btn_refresh = QPushButton("🔄 刷新")
        btn_refresh.setFixedSize(100, 32)
        btn_refresh.clicked.connect(self.load_logs)
        search_layout.addWidget(btn_refresh)

        # 导出按钮 (v2.2新增)
        btn_export = QPushButton("📊 导出Excel")
        btn_export.setProperty("class", "success")
        btn_export.setFixedSize(120, 32)
        btn_export.clicked.connect(self.export_logs)
        search_layout.addWidget(btn_export)

        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 日志表格
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["时间", "操作人", "模块", "动作", "详细内容"])

        # 设置列宽
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.log_table.setColumnWidth(0, 160)  # 时间列固定160px

        # 设置行高
        self.log_table.verticalHeader().setDefaultSectionSize(45)

        # 设置表格为只读
        self.log_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        layout.addWidget(self.log_table)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def load_logs(self, keyword=None):
        """
        加载日志数据
        :param keyword: 搜索关键词 (可选)
        """
        # 清空搜索框
        if keyword is None:
            self.search_input.clear()

        # 获取日志数据
        logs = LogService.get_logs(keyword=keyword, limit=100)

        # 清空表格
        self.log_table.setRowCount(0)

        # 填充数据
        for log in logs:
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)

            # 格式化时间
            time_str = log.log_time.strftime("%Y-%m-%d %H:%M:%S")

            # 填充各列
            self.log_table.setItem(row, 0, QTableWidgetItem(time_str))
            self.log_table.setItem(row, 1, QTableWidgetItem(log.username))
            self.log_table.setItem(row, 2, QTableWidgetItem(log.module))
            self.log_table.setItem(row, 3, QTableWidgetItem(log.action))
            self.log_table.setItem(row, 4, QTableWidgetItem(log.content or ""))

            # 设置居中对齐 (除了详细内容列)
            for col in range(4):
                item = self.log_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def search_logs(self):
        """执行搜索"""
        keyword = self.search_input.text().strip()
        if keyword:
            self.load_logs(keyword=keyword)
        else:
            self.load_logs()

    def export_logs(self):
        """
        导出日志到 Excel 文件
        v2.2新增功能
        """
        # 1. 弹出文件保存对话框
        default_filename = f"系统日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出日志到Excel",
            default_filename,
            "Excel文件 (*.xlsx);;所有文件 (*.*)"
        )

        # 如果用户取消保存
        if not file_path:
            return

        # 2. 获取当前搜索关键词 (如果有的话)
        keyword = self.search_input.text().strip() or None

        # 3. 调用服务层导出方法
        success, message = LogService.export_logs_to_excel(file_path, keyword=keyword)

        # 4. 显示结果提示
        if success:
            QMessageBox.information(self, "导出成功", f"✅ {message}\n\n文件保存至:\n{file_path}")
        else:
            QMessageBox.warning(self, "导出失败", f"❌ {message}")
