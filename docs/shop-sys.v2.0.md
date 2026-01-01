# 超市售货系统 v2.0 优化清单

**目标**: 完善收银台商品信息展示（增加价格透视），并将登录界面升级为现代商务风格（修复样式失效问题）。

---

## 🛒 Phase 1: 收银台搜索增强 (Cashier Info)
**目标**: 在搜索商品时，让收银员（或老板）能直接看到进价和售价。

- [ ] **修改 `ui/cashier_page.py`**
    * **修改表头 (`setup_search_table`)**:
        * 将列定义扩展为：`["编号", "名称", "类别", "进价", "售价", "库存", "操作"]`。
        * 进价/售价列宽建议设为 80px。
    * **修改数据填充 (`add_search_result_row`)**:
        * 在填充数据时，获取 `product.cost_price` (进价) 和 `product.sell_price` (售价)。
        * 注意：显示价格时建议保留两位小数，如 `f"{price:.2f}"`。
        * *提示*: 如果只想让老板看进价，可以加一个权限判断 `if self.is_admin: show_cost...`，如果不需要权限控制，直接显示即可。

---

## 🎨 Phase 2: 登录界面大修 (Login UI Redesign)
**目标**: 修复按钮样式失效问题，增加 Logo 展示，采用“微渐变”风格提升质感。

- [ ] **修改 `ui/login_window.py` (Python 代码)**
    * **增加 Logo (可选)**:
        * 在“欢迎使用”上方添加一个 `QLabel`，加载 `assets/logo.ico` 或绘制一个简单的圆形图标。
    * **设置 ObjectName (关键步骤)**:
        * **必须确保**代码里有这两行，否则 QSS 不生效：
          ```python
          self.username_input.setObjectName("login_input")
          self.password_input.setObjectName("login_input")
          self.login_btn.setObjectName("login_btn")
          ```
    * **调整布局**:
        * 标题下方的间距 (`addSpacing`) 增加到 40px。
        * 输入框之间增加 15px 间距。
        * 登录按钮上方增加 30px 间距。

- [ ] **修改 `assets/styles.qss` (样式重写)**
    * **背景优化**:
        * 给 `LoginWindow` 设置一个干净的纯白背景。
    * **输入框 (Modern Style)**:
        * 去掉四周黑框，改为**仅显示底部边框**（Material Design 风格）或 **浅灰色填充**。
        * 示例方案（浅灰填充）：
          ```css
          QLineEdit#login_input {
              background-color: #F2F4F7; /* 浅灰背景 */
              border: 1px solid transparent; /*以此占位*/
              border-radius: 6px;
              padding-left: 15px;
              font-size: 14px;
              color: #333;
          }
          QLineEdit#login_input:focus {
              background-color: #FFFFFF;
              border: 1px solid #409EFF; /* 聚焦时显示蓝框 */
          }
          ```
    * **登录按钮 (Gradient Style)**:
        * 之前的蓝色可能太单调，使用**线性渐变**增加立体感。
          ```css
          QPushButton#login_btn {
              /* 稍微斜向的蓝色渐变 */
              background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #409EFF, stop:1 #2b85e4);
              border: none;
              border-radius: 25px; /* 保持胶囊形 */
              color: white;
              font-size: 16px;
              font-weight: bold;
              letter-spacing: 4px; /* 增加字间距 */
          }
          QPushButton#login_btn:hover {
              background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #66b1ff, stop:1 #409EFF);
          }
          QPushButton#login_btn:pressed {
              padding-top: 2px;
          }
          ```