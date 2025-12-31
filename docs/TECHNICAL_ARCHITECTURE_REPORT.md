# ShopSys 技术架构报告

> **生成时间**: 2025-12-30
> **项目版本**: v1.4
> **报告目的**: 为架构师提供完整的项目上下文，以便规划下一阶段功能开发
> **数据库**: SQLite (shop.db)
> **UI框架**: PyQt6

---

## 目录

1. [项目目录结构](#1-项目目录结构)
2. [数据库模型 (Database Schema)](#2-数据库模型-database-schema)
3. [核心业务逻辑 (Service Layer)](#3-核心业务逻辑-service-layer)
4. [UI 架构 (User Interface)](#4-ui-架构-user-interface)
5. [依赖库](#5-依赖库)
6. [版本演进历史](#6-版本演进历史)

---

## 1. 项目目录结构

```
ShopSys/
├── main.py                    # 应用程序入口
├── init.py                    # 数据库初始化脚本
├── database.py                # 数据库配置和会话管理
├── models.py                  # SQLAlchemy ORM 模型定义
├── requirements.txt           # Python 依赖清单
├── shop.db                    # SQLite 数据库文件
├── logo.ico                   # 应用图标
│
├── services/                  # 业务逻辑层
│   ├── auth_service.py        # 用户认证服务
│   ├── product_service.py     # 商品管理服务
│   ├── sale_service.py        # 销售结算服务
│   ├── stats_service.py       # 数据统计和报表服务
│   └── backup_service.py      # 数据库备份服务
│
├── ui/                        # 用户界面层
│   ├── login_window.py        # 登录窗口
│   ├── main_window.py         # 主窗口 (导航框架)
│   ├── cashier_page.py        # 收银台页面
│   ├── inventory_page.py      # 商品管理页面
│   ├── stats_page.py          # 销售报表页面
│   ├── product_dialog.py      # 商品新增/编辑弹窗
│   └── hidden_page.py         # 隐藏维护页面 (root 模式)
│
├── backups/                   # 备份文件目录
│   ├── shop_YYYYMMDD_HHMMSS.db  # 数据库备份文件
│   └── sells/                 # Excel 导出目录
│       └── sales_record_*.xlsx
│
└── docs/                      # 文档目录
    └── TECHNICAL_ARCHITECTURE_REPORT.md  # 本报告
```

---

## 2. 数据库模型 (Database Schema)

### 2.1 技术栈
- **ORM**: SQLAlchemy 2.0+
- **数据库引擎**: SQLite
- **数据库文件**: `shop.db` (自动在可执行文件目录生成)

### 2.2 表结构详细说明

#### 2.2.1 User (用户表)
**表名**: `users`

| 字段名        | 类型      | 约束条件           | 说明               | 版本   |
|--------------|-----------|-------------------|-------------------|--------|
| id           | Integer   | PRIMARY KEY       | 用户 ID (自增)     | v1.0   |
| username     | String    | UNIQUE, NOT NULL  | 用户名 (唯一)      | v1.0   |
| password_hash| String    | NOT NULL          | MD5 加密的密码     | v1.0   |

**业务说明**:
- 默认管理员账号: `admin / admin` (由 `init.py` 自动创建)
- 硬编码特权账号: `root / 123456` (开启隐藏维护模式，不存储在数据库)

---

#### 2.2.2 Product (商品表)
**表名**: `products`

| 字段名      | 类型    | 约束条件           | 默认值     | 说明               | 版本   |
|------------|---------|-------------------|-----------|-------------------|--------|
| id         | String  | PRIMARY KEY       | -         | 商品编号 (条形码)   | v1.0   |
| name       | String  | NOT NULL          | -         | 商品名称           | v1.0   |
| cost_price | Float   | -                 | 0.0       | 进货价             | v1.0   |
| sell_price | Float   | -                 | 0.0       | 零售价             | v1.0   |
| stock      | Integer | -                 | 0         | 库存数量           | v1.0   |
| **category**   | **String**  | -             | **"未设置"** | **商品类别**       | **v1.2** |
| **location**   | **String**  | -             | **"未设置"** | **存放位置**       | **v1.2** |

**业务说明**:
- `id` 使用字符串类型以支持各种条形码格式
- v1.2 新增 `category` 和 `location` 字段，用于商品分类和库位管理
- 支持下拉选择预设值，也可自定义输入 (通过 QComboBox 实现)

**预设类别**: `["香烟", "酒水", "饮料", "零食", "日用品", "未设置"]`
**预设位置**: `["一楼", "二楼", "楼梯", "未设置"]`

---

#### 2.2.3 SaleRecord (销售记录表)
**表名**: `sale_records`

| 字段名        | 类型      | 约束条件                | 默认值       | 说明                   | 版本   |
|--------------|-----------|------------------------|-------------|------------------------|--------|
| id           | Integer   | PRIMARY KEY            | -           | 流水号 (自增)           | v1.0   |
| product_id   | String    | FOREIGN KEY -> products.id | -       | 关联商品编号           | v1.0   |
| quantity     | Integer   | NOT NULL               | -           | 销售数量               | v1.0   |
| total_amount | Float     | NOT NULL               | -           | 本单总金额 (实付)      | v1.0   |
| **profit**       | **Float**     | -                      | **0.0**     | **本单净利润 (快照)**  | **v1.3** |
| sale_time    | DateTime  | INDEX                  | now()       | 销售时间 (带索引)      | v1.0   |

**业务说明**:
- v1.3 新增 `profit` 字段，**固化每笔交易的利润快照**，避免后续修改进价导致历史数据失真
- 利润计算公式: `profit = (actual_price - cost_price) * quantity`
- `total_amount` 存储实付金额 (支持议价，可低于原价但不低于进价)
- 通过 `product` relationship 关联 Product 表，方便联表查询

---

## 3. 核心业务逻辑 (Service Layer)

### 3.1 AuthService (services/auth_service.py)

#### 类方法

```python
@staticmethod
def login(username: str, password: str) -> Tuple[bool, bool]:
    """
    验证登录
    返回: (登录成功标志, 是否管理员标志)
    """
```

**逻辑说明**:
- 优先检查硬编码特权账号 `root / 123456`，返回 `(True, True)`
- 再查询数据库中的 User 表，密码使用 MD5 加密比对
- 普通用户返回 `(True, False)`，失败返回 `(False, False)`

---

### 3.2 ProductService (services/product_service.py)

#### 类方法签名

```python
@staticmethod
def get_all_products() -> List[Product]:
    """获取所有商品列表"""

@staticmethod
def add_product(id: str, name: str, cost: float, price: float,
                stock: int, category: str = "未设置",
                location: str = "未设置") -> Tuple[bool, str]:
    """
    添加新商品
    返回: (成功标志, 消息)
    """

@staticmethod
def delete_product(product_id: str) -> Tuple[bool, str]:
    """删除指定编号的商品"""

@staticmethod
def get_product_by_id(product_id: str) -> Optional[Product]:
    """根据ID查找单个商品"""

@staticmethod
def search_products_by_name(keyword: str) -> List[Product]:
    """根据商品名称模糊搜索 (LIKE %keyword%)"""
```

---

### 3.3 SaleService (services/sale_service.py)

#### 核心方法: `checkout`

```python
@staticmethod
def checkout(cart_items: List[Dict]) -> Tuple[bool, str]:
    """
    结算功能
    :param cart_items: 格式 [{'id': '1001', 'qty': 2, 'price': 3.0, 'actual_price': 2.8}, ...]
    :return: (成功标志, 消息)
    """
```

**业务逻辑**:
1. **库存检查**: 遍历购物车，检查每个商品的库存是否充足
2. **库存扣减**: `product.stock -= qty` (原子操作)
3. **利润计算** (v1.3 核心变更):
   ```python
   record_profit = (actual_price - product.cost_price) * qty
   ```
   - 使用**实付金额 `actual_price`** (而非原价 `price`)
   - 将利润值**固化到 SaleRecord.profit 字段**，作为历史快照
4. **创建销售记录**:
   ```python
   record = SaleRecord(
       product_id=pid,
       quantity=qty,
       total_amount=qty * actual_price,  # 使用实付金额
       profit=record_profit,              # v1.3新增
       sale_time=datetime.now()
   )
   ```
5. **事务提交**: 使用 SQLAlchemy 事务保证原子性，失败自动回滚

**实付金额限制**:
- 收银台界面 `CashierPage` 使用 `QDoubleSpinBox` 限制实付金额范围: `[进价, 售价]`
- 防止亏本销售，允许议价但不能低于成本

---

### 3.4 StatsService (services/stats_service.py)

#### 核心方法签名

```python
@staticmethod
def get_sales_and_profit_trend(start_date, end_date) -> pd.DataFrame:
    """
    获取每日销售额和利润趋势
    返回: DataFrame(['date', 'revenue', 'profit'])
    """

@staticmethod
def get_category_stats(start_date, end_date) -> pd.DataFrame:
    """
    获取各商品类别的销售统计
    返回: DataFrame(['category', 'revenue'])
    """

@staticmethod
def get_top_products(start_date, end_date, limit=10) -> pd.DataFrame:
    """
    获取热销商品排行
    返回: DataFrame(['product_name', 'total_quantity', 'revenue'])
    """

@staticmethod
def get_total_stats(start_date, end_date) -> Dict[str, float]:
    """
    获取总营收和总利润
    返回: {'total_revenue': xxx, 'total_profit': xxx}
    """

@staticmethod
def get_raw_sales_records(start_date, end_date) -> pd.DataFrame:
    """
    获取原始销售记录 (用于明细查询和导出)
    返回: DataFrame(['流水号', '商品名称', '类别', '总金额', '数量', '利润', '时间', '商品编号'])
    """

@staticmethod
def export_to_excel(dataframe: pd.DataFrame) -> Tuple[bool, str]:
    """
    将 DataFrame 导出为 Excel 文件
    保存路径: backups/sells/sales_record_{timestamp}.xlsx
    """
```

**v1.3 性能优化**:
- 利润查询从联表计算改为**直接对 `SaleRecord.profit` 字段求和**
- 减少 JOIN 操作，提升大数据量下的查询性能

**导出功能** (v1.4):
- 自动创建 `backups/sells/` 目录
- 文件名格式: `sales_record_20251230_173000.xlsx`
- 使用 `openpyxl` 引擎导出

---

### 3.5 BackupService (services/backup_service.py)

#### 类方法签名

```python
@staticmethod
def backup_db() -> Tuple[bool, str]:
    """
    备份数据库文件
    返回: (成功标志, 消息)
    """

@staticmethod
def get_backup_list() -> List[Dict]:
    """
    获取所有备份文件列表 (按时间倒序)
    返回: [{'filename': str, 'path': str, 'time': datetime, 'size': int}]
    """
```

**业务逻辑**:
- 自动在 `backups/` 目录创建 `shop_YYYYMMDD_HHMMSS.db` 备份
- **自动清理机制**: 保留最近 7 天的备份，超期自动删除 (通过 `_cleanup_old_backups` 私有方法实现)
- **退出时自动备份**: `MainWindow.closeEvent` 中调用 `BackupService.backup_db()`

---

## 4. UI 架构 (User Interface)

### 4.1 UI 层级结构

```
LoginWindow (登录窗口)
   └─> MainWindow (主窗口框架)
         ├─> CashierPage (收银台)
         ├─> InventoryPage (商品管理)
         ├─> StatsPage (销售报表)
         └─> HiddenPage (隐藏维护模式, root 专属)
```

---

### 4.2 主要页面类

#### 4.2.1 LoginWindow (ui/login_window.py)
**尺寸**: 300x200 (固定)

**组件**:
- 用户名输入框 (`QLineEdit`)
- 密码输入框 (`QLineEdit`, EchoMode.Password)
- 登录按钮 (`QPushButton`)
- 回车快捷键绑定 (`returnPressed` 信号)

**逻辑**:
- 调用 `AuthService.login()` 验证
- 成功后创建 `MainWindow` 并传递 `is_hidden_mode` 标志

---

#### 4.2.2 MainWindow (ui/main_window.py)
**标题**: "超市售货系统 v1.3"
**尺寸**: 1000x600 (默认)

**核心组件**:
- `QStackedWidget`: 页面容器，用于切换不同功能页面
- `QToolBar`: 顶部导航栏

**导航按钮**:
1. 💰 收银台 → `CashierPage`
2. 📦 商品管理 → `InventoryPage`
3. 📈 销售报表 → `StatsPage`
4. 🔧 系统维护 → `HiddenPage` (仅 root 模式可见)
5. ❌ 退出系统 → 关闭窗口

**生命周期事件**:
- `closeEvent`: 退出时自动调用 `BackupService.backup_db()` 备份数据库

---

#### 4.2.3 CashierPage (ui/cashier_page.py) - 收银台
**布局**: 垂直布局，上下分区

##### 上半部分: 🔍 商品检索与快速添加 (v1.4)
- **搜索栏**: `QLineEdit` + "搜索"按钮，支持回车触发
- **搜索结果表格**: 4 列 (`QTableWidget`)
  ```
  | 编号 | 名称 | 库存 | 操作 |
  ```
- **操作列**: "➕ 添加"按钮，点击添加到购物车 (默认数量为 1)

##### 下半部分: 🛒 当前购物清单
- **扫码输入框**: `QLineEdit` (回车快速扫码添加)
- **购物车表格**: 6 列 (`QTableWidget`)
  ```
  | 编号 | 名称 | 单价 | 实付金额 | 数量 | 小计 |
  ```
  - **实付金额列**: `QDoubleSpinBox`，范围 `[进价, 售价]`，支持议价
  - **数量列**: 可编辑 (`DoubleClicked` 触发)，修改后自动重算小计
- **底部结算栏**:
  - 总金额显示: 红色粗体 20px 字体
  - "清空清单"按钮
  - "确认结算"按钮 (蓝色高亮)

**交互逻辑**:
1. **添加商品**:
   - 扫码枪输入 → 回车 → 自动查询并添加 (数量 +1)
   - 搜索结果点击"添加"按钮 → 添加到购物车
2. **修改数量**: 双击数量单元格，直接输入新值
3. **议价**: 修改"实付金额"列的 SpinBox 值
4. **结算**: 调用 `SaleService.checkout()`，成功后清空购物车并刷新搜索结果

**信号阻塞机制** (v1.4 重要优化):
- 使用 `blockSignals(True/False)` 防止 `update_cart_table()` 触发 `itemChanged` 信号导致死循环
- `update_actual_price_only()` 方法仅更新小计和总金额，不重绘整个表格

---

#### 4.2.4 InventoryPage (ui/inventory_page.py) - 商品管理
**布局**: 垂直布局

##### 顶部按钮区
- ➕ 新增商品 (绿色)
- 🗑️ 删除选中 (红色)
- 🔄 刷新列表
- 搜索框 (`QLineEdit`, 实时搜索)
- "显示进价"切换按钮 (默认隐藏进价，点击切换)

##### 商品表格
**显示列 (隐藏进价模式)**: 6 列
```
| 编号 | 名称 | 类别 | 位置 | 售价 | 库存 |
```

**显示列 (显示进价模式)**: 7 列
```
| 编号 | 名称 | 类别 | 位置 | 进价 | 售价 | 库存 |
```

**表格特性** (v1.4):
- 启用排序功能 (`setSortingEnabled(True)`)
- 数值列使用 `DisplayRole` 存储数值，支持数值排序 (而非字符串排序)
- 整行选中模式
- 不可编辑 (双击打开弹窗编辑，待开发)

**交互逻辑**:
- 点击"新增商品"弹出 `ProductDialog` 弹窗
- 选中行后点击"删除"二次确认后删除
- 搜索框实时过滤商品列表 (模糊匹配名称)

---

#### 4.2.5 ProductDialog (ui/product_dialog.py) - 商品弹窗
**类型**: `QDialog` (模态对话框)
**尺寸**: 350x350 (固定)

**表单字段**:
1. 商品编号 (`QLineEdit`)
2. 商品名称 (`QLineEdit`)
3. 商品类别 (`QComboBox`, 可编辑)
4. 存放位置 (`QComboBox`, 可编辑)
5. 进货价 (`QDoubleSpinBox`, 范围 0-100000)
6. 零售价 (`QDoubleSpinBox`, 范围 0-100000)
7. 库存量 (`QSpinBox`, 范围 0-99999)

**校验规则**:
- 编号和名称不能为空
- 确认后返回字典数据 (`get_data()` 方法)

---

#### 4.2.6 StatsPage (ui/stats_page.py) - 销售报表
**布局**: 水平布局 (左右分区, 比例 5:1)

##### 左侧: 图表展示区 (`QTabWidget`)
**Tab 0: 📜 销售明细** (v1.4)
- **导出按钮**: "📤 导出当前记录为 Excel" (绿色)
- **明细表格**: 8 列
  ```
  | 流水号 | 商品名称 | 类别 | 总金额 | 数量 | 利润 | 时间 | 商品编号 |
  ```
- 点击导出按钮调用 `StatsService.export_to_excel()`

**Tab 1: 📈 营收与利润趋势**
- 双线折线图 (Matplotlib)
- 蓝色实线: 销售额
- 绿色虚线: 净利润

**Tab 2: 🍰 类别销售占比**
- 环形图 (Pie Chart with width=0.5)
- 显示各类别销售额占比

**Tab 3: 🏆 热销商品排行**
- 水平条形图 (Top 10)
- 按销售数量降序排列

##### 右侧: 控制面板 (最大宽度 280px)
**1. 📅 查询时间范围**
- 开始日期 (`QDateEdit`, 默认 7 天前)
- 结束日期 (`QDateEdit`, 默认明天)
- 日历弹窗选择

**2. ⚡ 快捷选择**
- "今日"按钮
- "本周"按钮
- "本月"按钮

**3. 💰 核心指标**
- 总营收标签 (14px 粗体)
- 总利润标签 (14px 粗体, 蓝色)

**4. 🔄 生成报表按钮**
- 点击后禁用按钮并显示"⏳ 加载中..."
- 使用 `QThread` 异步加载数据 (`DataWorker` 类)

**异步加载机制**:
```python
class DataWorker(QThread):
    finished = pyqtSignal(dict)  # 发送加载完成的信号

    def run(self):
        # 后台查询所有数据
        # 查询完成后通过 finished 信号传递结果
```
- 避免 UI 冻结，提升用户体验

---

#### 4.2.7 HiddenPage (ui/hidden_page.py) - 隐藏维护模式
**触发条件**: 使用 `root / 123456` 登录

**功能按钮** (当前仅占位，待开发):
1. 🗑️ 深度数据清洗
2. ⚠️ 系统重置
3. 📜 查看系统日志

**样式**: 红色警示标题 + 居中按钮布局

---

## 5. 依赖库

### 5.1 requirements.txt

```txt
PyQt6==6.4.2              # GUI 框架
PyQt6-tools>=6.4.2        # Qt Designer 等开发工具
SQLAlchemy>=2.0.0         # ORM 框架
pandas>=2.1.0             # 数据分析和导出
matplotlib>=3.8.0         # 数据可视化
openpyxl>=3.1.0           # Excel 导出引擎
pyinstaller>=6.0.0        # 打包为独立 exe
```

### 5.2 核心库用途说明

| 库名          | 用途                                  | 关键模块                     |
|--------------|--------------------------------------|----------------------------|
| PyQt6        | 桌面应用 GUI 框架                     | QtWidgets, QtCore, QtGui   |
| SQLAlchemy   | 数据库 ORM (对象关系映射)             | create_engine, sessionmaker, declarative_base |
| pandas       | 数据处理和 DataFrame 导出             | read_sql, to_excel         |
| matplotlib   | 图表绘制 (折线图/饼图/条形图)          | pyplot, FigureCanvasQTAgg  |
| openpyxl     | Excel 文件读写 (pandas 的 backend)   | 自动调用                    |
| pyinstaller  | 打包为 Windows exe 可执行文件         | CLI 工具                    |

---

## 6. 版本演进历史

### v1.0 (基础版本)
- 实现基础 MVC 架构
- User/Product/SaleRecord 三表结构
- 登录 + 商品管理 + 收银结算
- 简单的日报表查询

### v1.2 (分类增强)
- **Product 表新增字段**:
  - `category` (商品类别)
  - `location` (存放位置)
- 商品弹窗支持下拉选择类别和位置
- 商品管理页面显示类别和位置列

### v1.3 (利润快照 + 自动备份)
- **SaleRecord 表新增字段**:
  - `profit` (本单净利润快照)
- 利润计算从联表改为直接求和 `SaleRecord.profit`
- 新增 `BackupService` 自动备份数据库
- 退出时自动备份 + 7 天自动清理
- 报表页面新增"总利润"指标卡

### v1.4 (当前版本)
- **收银台优化**:
  - 搜索结果直接添加到购物车，默认数量为 1
  - 购物车数量列可编辑 (双击修改)
  - 信号阻塞机制防止死循环
- **商品管理优化**:
  - 启用表格排序功能
  - 数值列正确存储为数值类型 (DisplayRole)
- **报表页面新增**:
  - "销售明细" Tab (第一个 Tab)
  - 支持导出 Excel 到 `backups/sells/` 目录

---

## 附录: 关键代码片段

### A1. 数据库路径自适应 (database.py:8-16)

```python
if getattr(sys, 'frozen', False):
    # 打包后的 exe 运行时，基准路径是 exe 所在目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Python 脚本运行时，基准路径是当前脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_URL = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"
```

### A2. 利润固化逻辑 (sale_service.py:34-42)

```python
# 计算本次交易的利润 (v1.3: 固化利润快照)
record_profit = (actual_price - product.cost_price) * qty

# 创建销售记录 (使用实付金额，并保存利润)
record = SaleRecord(
    product_id=pid,
    quantity=qty,
    total_amount=qty * actual_price,  # 使用实付金额
    profit=record_profit,              # v1.3新增
    sale_time=datetime.now()
)
```

### A3. 实付金额限制 (cashier_page.py:199-206)

```python
# 实付金额使用可编辑的SpinBox
actual_price_spin = QDoubleSpinBox()
actual_price_spin.setRange(item['cost_price'], item['price'])  # 范围：进价到售价
actual_price_spin.setDecimals(2)
actual_price_spin.setValue(item['actual_price'])
actual_price_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
# 当值改变时，只更新数据和总金额，不重新刷新整个表格
actual_price_spin.valueChanged.connect(lambda value, i=idx: self.update_actual_price_only(i, value))
```

### A4. 异步数据加载 (stats_page.py:20-49)

```python
class DataWorker(QThread):
    """后台数据加载线程"""
    finished = pyqtSignal(dict)

    def __init__(self, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        try:
            # 加载所有需要的数据
            trend_data = StatsService.get_sales_and_profit_trend(self.start_date, self.end_date)
            category_data = StatsService.get_category_stats(self.start_date, self.end_date)
            # ... 其他数据查询

            self.finished.emit({
                'trend': trend_data,
                'category': category_data,
                # ... 其他数据
            })
        except Exception as e:
            print(f"数据加载出错: {e}")
            self.finished.emit({})
```

---

## 报告总结

### 架构优势
1. **清晰的分层架构**: UI → Service → Model，职责分离
2. **事务安全**: SQLAlchemy 事务保证数据一致性
3. **数据固化**: 利润快照机制避免历史数据失真
4. **用户体验**: 异步加载、实时搜索、自动备份

### 潜在优化方向 (供架构师参考)
1. **权限系统**: 目前仅有 root/admin 二级权限，可扩展为多角色系统
2. **商品编辑**: 目前仅支持新增/删除，可添加编辑功能 (复用 ProductDialog)
3. **退货流程**: 当前无退货功能，需增加负数销售记录和库存回滚
4. **会员系统**: 可扩展会员积分、折扣等功能
5. **多仓库管理**: 当前仅支持单仓库，可扩展多仓库调拨
6. **日志系统**: HiddenPage 的日志功能待实现
7. **数据恢复**: BackupService 仅支持备份，可添加恢复功能
8. **打印功能**: 结算后打印小票

---

**报告完成**
📧 如有疑问，请联系技术负责人
🔗 项目仓库: [根据实际情况填写]
