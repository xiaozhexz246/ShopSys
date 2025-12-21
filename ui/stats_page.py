# 文件名: ui/stats_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QDateEdit, QFrame, QTabWidget, QGroupBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import QDate, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from services.stats_service import StatsService

# --- Matplotlib 相关导入 ---
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# 设置字体以支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class DataWorker(QThread):
    """后台数据加载线程"""
    finished = pyqtSignal(dict)  # 发送加载完成的信号

    def __init__(self, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        """在后台线程中执行数据查询"""
        try:
            # 加载所有需要的数据
            trend_data = StatsService.get_sales_and_profit_trend(self.start_date, self.end_date)
            category_data = StatsService.get_category_stats(self.start_date, self.end_date)
            top_products_data = StatsService.get_top_products(self.start_date, self.end_date, limit=10)
            total_stats = StatsService.get_total_stats(self.start_date, self.end_date)
            raw_sales_data = StatsService.get_raw_sales_records(self.start_date, self.end_date)

            # 发送结果
            self.finished.emit({
                'trend': trend_data,
                'category': category_data,
                'top_products': top_products_data,
                'total_stats': total_stats,
                'raw_sales': raw_sales_data
            })
        except Exception as e:
            print(f"数据加载出错: {e}")
            self.finished.emit({})

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.current_raw_data = None  # 保存当前的原始销售数据用于导出
        self.init_ui()

    def init_ui(self):
        # 主布局：水平布局
        main_layout = QHBoxLayout()

        # === 左侧：图表展示区 ===
        left_panel = self.create_chart_panel()
        main_layout.addWidget(left_panel, 5)  # Stretch Factor = 5

        # === 右侧：控制面板区 ===
        right_panel = self.create_control_panel()
        right_panel.setMaximumWidth(280)  # 限制最大宽度
        main_layout.addWidget(right_panel, 1)  # Stretch Factor = 1

        self.setLayout(main_layout)

    def create_chart_panel(self):
        """创建左侧图表展示区"""
        # 使用 QTabWidget 容纳多张图表
        self.tab_widget = QTabWidget()

        # Tab 0: 销售明细 (v1.4新增)
        self.details_tab = self.create_details_tab()
        self.tab_widget.insertTab(0, self.details_tab, "📜 销售明细")

        # Tab 1: 营收与利润趋势
        self.trend_canvas = FigureCanvas(Figure(figsize=(8, 5), dpi=100))
        self.tab_widget.addTab(self.trend_canvas, "📈 营收与利润趋势")

        # Tab 2: 类别占比
        self.category_canvas = FigureCanvas(Figure(figsize=(8, 5), dpi=100))
        self.tab_widget.addTab(self.category_canvas, "🍰 类别销售占比")

        # Tab 3: 热销排行
        self.top_canvas = FigureCanvas(Figure(figsize=(8, 5), dpi=100))
        self.tab_widget.addTab(self.top_canvas, "🏆 热销商品排行")

        return self.tab_widget

    def create_details_tab(self):
        """创建销售明细 Tab (v1.4)"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 顶部：导出按钮
        btn_export = QPushButton("📤 导出当前记录为 Excel")
        btn_export.clicked.connect(self.export_to_excel)
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(btn_export)

        # 主体：销售明细表格
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(8)
        self.details_table.setHorizontalHeaderLabels([
            '流水号', '商品名称', '类别', '总金额', '数量', '利润', '时间', '商品编号'
        ])

        # 设置表格属性
        self.details_table.horizontalHeader().setStretchLastSection(True)
        self.details_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.details_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.details_table)
        widget.setLayout(layout)
        return widget

    def create_control_panel(self):
        """创建右侧控制面板区"""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()

        # --- 1. 日期范围选择器 ---
        date_group = QGroupBox("📅 查询时间范围")
        date_layout = QVBoxLayout()

        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addDays(-7))
        date_layout.addWidget(QLabel("开始日期:"))
        date_layout.addWidget(self.date_start)

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate().addDays(1))
        date_layout.addWidget(QLabel("结束日期:"))
        date_layout.addWidget(self.date_end)

        date_group.setLayout(date_layout)
        layout.addWidget(date_group)

        # --- 2. 快捷按钮组 ---
        shortcut_group = QGroupBox("⚡ 快捷选择")
        shortcut_layout = QVBoxLayout()

        btn_today = QPushButton("今日")
        btn_today.clicked.connect(lambda: self.set_date_range(0))
        shortcut_layout.addWidget(btn_today)

        btn_week = QPushButton("本周")
        btn_week.clicked.connect(lambda: self.set_date_range(7))
        shortcut_layout.addWidget(btn_week)

        btn_month = QPushButton("本月")
        btn_month.clicked.connect(lambda: self.set_date_range(30))
        shortcut_layout.addWidget(btn_month)

        shortcut_group.setLayout(shortcut_layout)
        layout.addWidget(shortcut_group)

        # --- 3. 核心指标卡 (KPI Cards) ---
        kpi_group = QGroupBox("💰 核心指标")
        kpi_layout = QVBoxLayout()

        self.label_revenue = QLabel("总营收: ¥0.00")
        self.label_revenue.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        kpi_layout.addWidget(self.label_revenue)

        self.label_profit = QLabel("总利润: ¥0.00")
        self.label_profit.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_profit.setStyleSheet("color: #0078d7;")
        kpi_layout.addWidget(self.label_profit)

        kpi_group.setLayout(kpi_layout)
        layout.addWidget(kpi_group)

        # --- 4. 功能按钮 ---
        self.btn_refresh = QPushButton("🔄 生成报表")
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.btn_refresh)

        layout.addStretch()  # 底部弹性空间
        panel.setLayout(layout)
        return panel

    def set_date_range(self, days):
        """设置日期范围快捷方法"""
        if days == 0:  # 今日
            self.date_start.setDate(QDate.currentDate())
            self.date_end.setDate(QDate.currentDate().addDays(1))
        else:  # 过去N天
            self.date_start.setDate(QDate.currentDate().addDays(-days))
            self.date_end.setDate(QDate.currentDate().addDays(1))

    def load_data(self):
        """异步加载数据"""
        # 禁用按钮，防止重复点击
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setText("⏳ 加载中...")

        # 获取日期
        start = self.date_start.date().toPyDate()
        end = self.date_end.date().toPyDate()

        # 创建后台线程
        self.worker = DataWorker(start, end)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.start()

    def on_data_loaded(self, data):
        """数据加载完成后的回调"""
        # 恢复按钮状态
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText("🔄 生成报表")

        if not data:
            return

        # 更新核心指标
        total_stats = data.get('total_stats', {})
        self.label_revenue.setText(f"总营收: ¥{total_stats.get('total_revenue', 0):.2f}")
        self.label_profit.setText(f"总利润: ¥{total_stats.get('total_profit', 0):.2f}")

        # 绘制各个图表
        self.plot_trend_chart(data.get('trend'))
        self.plot_category_chart(data.get('category'))
        self.plot_top_products_chart(data.get('top_products'))

        # 更新销售明细表格 (v1.4)
        self.update_details_table(data.get('raw_sales'))

    def plot_trend_chart(self, df):
        """绘制营收与利润趋势图"""
        figure = self.trend_canvas.figure
        figure.clear()
        ax = figure.add_subplot(111)

        if not df.empty and 'date' in df.columns:
            # 绘制双线图
            x = df['date']
            revenue = df['revenue']
            profit = df['profit']

            ax.plot(x, revenue, marker='o', linewidth=2, label='销售额', color='#0078d7')
            ax.plot(x, profit, marker='s', linewidth=2, linestyle='--', label='净利润', color='#28a745')

            ax.set_title("营收与利润趋势", fontsize=14, fontweight='bold')
            ax.set_ylabel("金额 (元)", fontsize=12)
            ax.set_xlabel("日期", fontsize=12)
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)

            figure.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, '该时间段无销售记录',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='gray')

        self.trend_canvas.draw()

    def plot_category_chart(self, df):
        """绘制类别销售占比环形图"""
        figure = self.category_canvas.figure
        figure.clear()
        ax = figure.add_subplot(111)

        if not df.empty and 'category' in df.columns:
            # 绘制环形图
            labels = df['category']
            sizes = df['revenue']

            # 设置颜色
            colors = plt.cm.Set3(range(len(labels)))

            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                colors=colors, startangle=90,
                                                wedgeprops=dict(width=0.5))  # width=0.5 制作环形图

            # 美化文字
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            ax.set_title("商品类别销售占比", fontsize=14, fontweight='bold')
        else:
            ax.text(0.5, 0.5, '该时间段无类别数据',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='gray')

        self.category_canvas.draw()

    def plot_top_products_chart(self, df):
        """绘制热销商品排行水平条形图"""
        figure = self.top_canvas.figure
        figure.clear()
        ax = figure.add_subplot(111)

        if not df.empty and 'product_name' in df.columns:
            # 绘制水平条形图
            products = df['product_name']
            quantities = df['total_quantity']

            # 反转顺序，让第一名在最上方
            products = products[::-1]
            quantities = quantities[::-1]

            bars = ax.barh(products, quantities, color='#ff6b6b', height=0.6)
            ax.set_xlabel("销售数量", fontsize=12)
            ax.set_title("热销商品 TOP 10", fontsize=14, fontweight='bold')

            # 在条形上显示数值
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        ha='left', va='center', fontweight='bold')

            ax.grid(axis='x', alpha=0.3)
        else:
            ax.text(0.5, 0.5, '该时间段无销售数据',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='gray')

        self.top_canvas.draw()

    def update_details_table(self, df):
        """更新销售明细表格 (v1.4)"""
        # 保存数据用于导出
        self.current_raw_data = df

        # 清空表格
        self.details_table.setRowCount(0)

        if df is None or df.empty:
            return

        # 填充表格
        self.details_table.setRowCount(len(df))

        for row_idx, row_data in df.iterrows():
            # 按照列顺序填充：流水号, 商品名称, 类别, 总金额, 数量, 利润, 时间, 商品编号
            col_mapping = ['流水号', '商品名称', '类别', '总金额', '数量', '利润', '时间', '商品编号']

            for col_idx, col_name in enumerate(col_mapping):
                value = row_data.get(col_name, '')

                # 格式化显示
                if col_name in ['总金额', '利润']:
                    item = QTableWidgetItem(f"¥{value:.2f}")
                elif col_name == '时间':
                    item = QTableWidgetItem(str(value))
                else:
                    item = QTableWidgetItem(str(value))

                self.details_table.setItem(row_idx, col_idx, item)

        # 自动调整列宽
        self.details_table.resizeColumnsToContents()

    def export_to_excel(self):
        """导出当前销售明细为 Excel (v1.4)"""
        if self.current_raw_data is None or self.current_raw_data.empty:
            QMessageBox.warning(self, "提示", "当前无数据可导出，请先查询数据！")
            return

        # 调用 StatsService 导出
        success, result = StatsService.export_to_excel(self.current_raw_data)

        if success:
            QMessageBox.information(self, "导出成功", f"销售记录已导出至:\n{result}")
        else:
            QMessageBox.critical(self, "导出失败", result)
