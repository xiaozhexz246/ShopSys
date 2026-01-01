# 超市售货系统 v1.9 UI 修复清单

**目标**: 还原下拉框的原生样式，并修复表格内按钮被“压扁”和位置偏移的问题。

---

## 🎨 Phase 1: 还原下拉框样式 (Fix ComboBox)
**修改 `assets/styles.qss`**:
- [ ] **删除或重置 QComboBox 样式**
    * 找到 `QComboBox` 相关的样式块。
    * **核心操作**: 删除涉及 `QComboBox::drop-down` 和 `QComboBox::down-arrow` 的代码。
    * 如果只想保留字体大小，可以保留 `QComboBox { font-size: 12px; }`，但务必删除 `border` 和 `background` 属性，让它恢复成 Windows/Mac 的原生样式（带箭头的样式）。

---

## 📐 Phase 2: 修复表格按钮布局 (Fix Table Buttons)
**目标**: 去除多余边距，让文字按钮垂直居中且完整显示。

- [ ] **修改 Python 代码 (`ui/inventory_page.py`, `ui/replenish_page.py` 等)**
    * 找到生成表格“操作”列的代码块。
    * **修改容器布局逻辑**:
      ```python
      # 1. 创建容器
      widget = QWidget()
      
      # 2. 创建水平布局
      layout = QHBoxLayout(widget)
      
      # 3. 关键修复：将边距设为 0 (去掉原本的边距选项)
      layout.setContentsMargins(0, 0, 0, 0)
      
      # 4. 关键修复：设置绝对居中
      layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
      
      # 5. 按钮设置
      btn = QPushButton("编辑")
      btn.setProperty("class", "table-btn")
      btn.setFlat(True) 
      btn.setCursor(Qt.CursorShape.PointingHandCursor)
      
      # 6. 关键修复：不要设置 FixedSize，或者只设置宽度
      # btn.setFixedSize(50, 25)  <-- 删除这行，让文字撑开高度
      # 或者只限制宽度: btn.setFixedWidth(50)
      
      layout.addWidget(btn)
      self.table.setCellWidget(row, col, widget)
      ```

- [ ] **微调 `assets/styles.qss` 中的 `.table-btn`**
    * 确保没有设置奇怪的 `height` 或 `padding` 导致被压缩。
    * 建议样式:
      ```css
      QPushButton[class="table-btn"] {
          border: none;
          background: transparent;
          color: #409EFF;
          font-weight: bold;
          padding: 4px 8px; /* 稍微给点内边距即可 */
          min-height: 20px; /* 保证最小高度 */
      }
      ```