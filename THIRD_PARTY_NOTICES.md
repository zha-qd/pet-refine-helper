# 第三方组件

Windows 便携包包含 Python 3.10、Tcl/Tk、PaddlePaddle、PaddleOCR、OpenCV、NumPy 及其依赖。
完整已安装版本见 `docs/runtime-packages.json`。

- Python 许可证保留于 `runtime/LICENSE.txt`。
- Python 包的许可证和元数据保留于 `runtime/Lib/site-packages/` 下的包目录及 `.dist-info` / `.egg-info` 目录。
- Tcl/Tk 许可证随 `runtime/tcl/` 保留。
- OCR 模型来自 PaddleOCR 官方分发，使用英语 PP-OCRv3 检测、英语 PP-OCRv4 识别和 mobile v2 分类模型；便携包中的 `models/PaddleOCR-LICENSE` 保留 PaddleOCR 项目的许可证。

各第三方组件遵循各自许可证。本项目的公开发布不改变这些条款。
项目自身尚未指定开源许可证；公开可下载不代表授予任意再分发或商业使用许可。
