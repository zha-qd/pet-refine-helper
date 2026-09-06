# 更新记录 | Changelog

## 1.0.0

- 白色双栏界面，右侧大日志区域。
- 默认窗口标题为空，需要自行填写。
- 单洗、双洗、三洗；单个开始/停止按钮，F5 快捷键防重复触发。
- 单洗仅替换正增量；双洗/三洗按所选属性合计正值替换。
- 无红绿文字视为无变化；每轮输出属性和操作日志。
- 替换后连续读取两次总属性，与预期一致才记录成功。
- 单洗开始前及替换后检查满值并自动停止。
- 停止后输出已核验属性的累计正向提升。
- 便携包附运行环境、OCR 模型及启动错误日志入口。

### English

- Clean white two-column UI with a large log panel and an empty initial window title.
- Single/dual/triple-stat modes and one Start/Stop button, controlled by F5.
- Per-round change logs and zero-change reroll behavior.
- Two consecutive total-stat reads verify each replacement before counting gains.
- Single-stat cap detection before rolling and after replacement.
- Verified positive-gain summary, portable runtime, bundled OCR models and startup diagnostics.
