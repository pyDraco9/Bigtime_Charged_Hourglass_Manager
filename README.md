# Bigtime_Charged_Hourglass_Manager

由于openloot官网无法直接显示沙漏充能时间, 充能管理非常困难.

工具用于批量显示沙漏的充能时间, 并支持打钩批量转移, 方便出售.

使用方法: 请访问在任意有鉴权的接口(如: https://openloot.com/collection )时按F12获取 `cookie`, `X-Device-Id` 和 `X-Session-Id`.

如果不会可以谷歌搜索 "chrome如何获取cookie", 其他两个参数也在同一个页面可以找到.

将这些值写入.env文件后(用文本编辑器编辑)运行 `main.py`

(由于不明白为什么打包exe一直报错, 似乎是pySide6和PyInstaller之间有什么问题, 所以暂时不提供打包的exe)

预览图:

![20240402194636](https://github.com/pyDraco9/Bigtime_Charged_Hourglass_Manager/assets/11333467/1e09ab6e-b708-4181-9ead-84948f5ce74c)
