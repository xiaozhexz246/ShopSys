# 超市售货系统 v1.9 修正清单 (Refined)

**目标**: 实现无边框的扁平化按钮样式，并使用底层事件拦截解决扫码枪自动提交问题。

---

## 🎨 Phase 1: 按钮样式微调 (Flat Style)
不要纯文字，而是要“去掉边框”的现代按钮。

- [ ] **修改 `assets/styles.qss`**
    * **定义 `.table-btn` 样式类** (替代之前的 link-btn):
        ```css
        QPushButton[class="table-btn"] {
            border: none;                  /* 关键：去掉边框 */
            background-color: transparent; /* 平时透明 */
            border-radius: 4px;            /* 鼠标放上去时有圆角 */
            padding: 4px 8px;              /* 给文字留点呼吸空间 */
            color: #606266;                /* 默认深灰字体 */
        }
        QPushButton[class="table-btn"]:hover {
            background-color: #ecf5ff;     /* 悬停时显示淡蓝色背景 */
            color: #409eff;                /* 文字变蓝 */
        }
        QPushButton[class="table-btn"]:pressed {
            background-color: #d9ecff;     /* 按下时背景变深 */
        }
        ```
    * *特殊处理*: 对于“删除”按钮，可以定义一个红色系的 Hover。

- [ ] **更新 Python 代码 (`ui/inventory_page.py` 等)**
    * 在创建表格按钮时：
        * `btn.setProperty("class", "table-btn")`。
        * **移除** `setFlat(True)` (因为我们用 QSS 控制了，不需要原生 Flat 属性干扰)。
        * 保持 `setFixedSize` 或让其自适应，但要确保有 Padding。

---

## 🛡️ Phase 2: 扫码枪底层拦截 (Event Override)
不再相信信号连接，直接在底层截断回车键。

- [ ] **修改 `ui/product_dialog.py` 和 `ui/batch_dialog.py`**
    * **核心逻辑**: 重写窗口的 `keyPressEvent`。
    * **代码实现 (请完整复制)**:
      ```python
      # 在 Dialog 类中添加这个方法
      def keyPressEvent(self, event):
          # 1. 检测是否是回车键 (支持大键盘 Enter 和小键盘 Return)
          if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
              # 2. 检查焦点是否在“商品编号”输入框
              if self.id_input.hasFocus(): # 假设输入框叫 id_input
                  # 3. 核心：只转移焦点，不提交
                  print("检测到扫码枪回车，拦截提交，跳转焦点") # debug用
                  self.name_input.setFocus() # 跳转到下一个框
                  event.accept() # 标记事件已处理
                  return # 强制结束，不再传递给父类(QDialog)
          
          # 4. 其他情况（如在确认按钮上按回车），交给父类处理（即正常提交）
          super().keyPressEvent(event)
      ```
    * *注意*: 这种写法会彻底屏蔽掉编号框回车触发 `accept()` 的可能性。