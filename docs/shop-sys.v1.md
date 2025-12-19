# 超市售货系统架构文档 (v1.0)

**版本**: 1.0.0
**日期**: 2025-12-20
**维护者**: xiaozhexz
**架构模式**: C/S 单机桌面应用 (MVC 分层模式)

---

## 1. 总体架构设计

本系统采用 Python + PyQt6 开发，旨在为中小型超市提供轻量级、无需服务器部署的单机管理方案。系统核心遵循 **MVC (Model-View-Controller)** 的变种分层设计，将界面展示、业务逻辑与数据存储严格解耦。

### 1.1 技术栈 (Tech Stack)
| 层级 | 技术选型 | 版本要求 | 用途 |
| :--- | :--- | :--- | :--- |
| **表现层 (UI)** | PyQt6 | 6.4.2+ | 图形界面绘制、事件响应 |
| **业务层 (Service)** | Python 3.10+ | - | 核心逻辑处理 (登录、交易、库存计算) |
| **数据层 (DAO)** | SQLAlchemy | 2.0+ | ORM 映射，处理数据库交互 |
| **存储层 (DB)** | SQLite | - | 本地单文件数据库，无需安装服务 |
| **分析层** | Pandas / Matplotlib | - | 销售数据清洗与可视化图表绘制 |
| **部署** | PyInstaller | 6.0+ | 打包为独立 EXE 可执行文件 |

### 1.2 目录结构
```text
SupermarketSystem/
├── main.py                 # [入口] 程序启动点，负责初始化环境
├── database.py             # [配置] 数据库连接引擎，智能处理开发/打包路径
├── init_db.py              # [工具] 数据库表结构初始化脚本
├── models.py               # [模型] SQLAlchemy 数据表对象定义
├── requirements.txt        # [依赖] 项目依赖库列表
├── shop.db                 # [数据] SQLite 数据库文件 (运行时生成)
├── docs/                  # [文档] 项目文档
│   ├── shop-sys.v1.md      # 销售系统v1.0架构文档
├── services/               # [业务逻辑层] 纯 Python 逻辑，无 UI 代码
│   ├── auth_service.py     # 登录验证
│   ├── product_service.py  # 商品增删改查
│   ├── sale_service.py     # 交易结算与事务处理
│   └── stats_service.py    # 数据分析与报表生成
└── ui/                     # [表现层] PyQt6 界面代码
    ├── login_window.py     # 登录窗口
    ├── main_window.py      # 主程序框架 (导航栏 + 堆叠窗口)
    ├── inventory_page.py   # 商品管理页
    ├── product_dialog.py   # 商品录入弹窗
    ├── cashier_page.py     # 收银台页
    └── stats_page.py       # 统计报表页
```
## 2. 数据库设计 (Database Schema)

采用 SQLite 关系型数据库，包含三张核心表。

### 2.1 用户表 (`users`)

用于管理员登录验证。
| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key | 自增 ID |
| `username` | String | Unique, Not Null | 用户名 (默认: admin) |
| `password_hash` | String | Not Null | MD5 加密后的密码字符串 |

### 2.2 商品表 (`products`)

存储所有库存商品信息。
| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | String | Primary Key | **商品条码** (手动输入或扫描) |
| `name` | String | Not Null | 商品名称 |
| `cost_price` | Float | Default 0.0 | 进货价 (成本) |
| `sell_price` | Float | Default 0.0 | 零售价 |
| `stock` | Integer | Default 0 | 当前库存数量 |

### 2.3 销售记录表 (`sale_records`)

记录每一笔成功的交易流水。
| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key | 自增流水号 |
| `product_id` | String | ForeignKey | 关联商品表 ID |
| `quantity` | Integer | Not Null | 售出数量 |
| `total_amount` | Float | Not Null | 本单总额 (当时售价 * 数量) |
| `sale_time` | DateTime | Default Now | 交易完成时间 |

---

## 3. 核心业务逻辑流

### 3.1 结算流程 (Checkout Transaction)

为保证数据一致性，销售过程使用了数据库**事务 (Transaction)**。

1. **输入**: 接收购物车列表 `[{id, qty, price}, ...]`。
2. **开启事务**: `Session.begin()`
3. **循环检查**: 遍历每个商品 -> 检查 ID 是否存在 -> 检查 `stock >= qty`。
* *异常*: 任意商品检查失败，触发 `Rollback`，提示错误，不做任何修改。


4. **扣减库存**: `product.stock -= qty`。
5. **记录流水**: 插入数据到 `sale_records` 表。
6. **提交事务**: `Session.commit()`，所有更改生效。

### 3.2 数据路径修正 (Path Patching)

为了支持打包成 EXE 后仍能正确读写数据库，`database.py` 中实现了路径嗅探逻辑：

* **开发模式**: 使用 `__file__` 所在目录。
* **冻结模式 (Frozen)**: 使用 `sys.executable` (EXE文件) 所在目录。

---

## 4. 后续优化路线图 (Roadmap v2.0)

基于 v1.0 的架构，后续可进行的升级方向：

* [ ] **硬件对接**: 监听 USB 扫码枪事件（目前是模拟输入）。
* [ ] **数据导出**: 增加将销售报表导出为 Excel (`.xlsx`) 的功能 (需 `openpyxl`)。
* [ ] **小票打印**: 调用系统打印机接口，打印收银小票。
* [ ] **会员系统**: 新增 `Member` 表，支持积分与折扣计算。
* [ ] **云端同步**: (高级) 将 SQLite 替换为远程 MySQL，支持多台收银机联网。
