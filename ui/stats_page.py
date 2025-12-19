# 文件名: ui/stats_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QMessageBox)
from PyQt6.QtCore import QDate
from services.stats_service import StatsService

# --- Matplotlib 相关导入 ---
import matplotlib
matplotlib.use('QtAgg') # 声明使用 Qt 后端
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# 设置字体以支持中文显示 (Windows一般用 SimHei, Mac可能需要改用 Arial Unicode MS)
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- 1. 顶部筛选区 ---
        filter_layout = QHBoxLayout()
        
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addDays(-7)) # 默认查过去7天
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate().addDays(1)) # 默认查到明天
        
        btn_query = QPushButton("📊 生成报表")
        btn_query.clicked.connect(self.plot_chart)

        filter_layout.addWidget(QLabel("开始日期:"))
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("结束日期:"))
        filter_layout.addWidget(self.date_end)
        filter_layout.addWidget(btn_query)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)

        # --- 2. 图表显示区 ---
        # 创建 Matplotlib 的 Figure 对象
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure) # 把 Figure 放进 Canvas
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def plot_chart(self):
        """查询数据并画图"""
        # 获取日期 (转为 Python datetime 格式的字符串)
        start = self.date_start.date().toPyDate()
        end = self.date_end.date().toPyDate()

        # 调用 Service
        df = StatsService.get_daily_sales(start, end)

        # 清空旧图表
        self.figure.clear()

        # 创建子图 (subplot)
        ax = self.figure.add_subplot(111)

        if not df.empty and 'date' in df.columns and 'total' in df.columns:
            # 绘制柱状图
            bars = ax.bar(df['date'], df['total'], color='#0078d7', width=0.5)
            
            # 设置标题和标签
            ax.set_title(f"销售趋势 ({start} 至 {end})")
            ax.set_ylabel("销售额 (元)")
            ax.set_xlabel("日期")
            
            # 在柱子上方显示具体数值
            ax.bar_label(bars, fmt='%.0f')
            
            # 自动调整日期标签倾斜度，防止重叠
            self.figure.autofmt_xdate()
        else:
            # 如果没数据，显示提示文本
            ax.text(0.5, 0.5, '该时间段无销售记录', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='gray')

        # 刷新画布，显示新图
        self.canvas.draw()