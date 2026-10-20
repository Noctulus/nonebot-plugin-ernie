"""测试公共初始化。

NoneBot 的插件加载依赖已初始化的 driver，因此在收集测试前完成初始化，
并只加载一次插件，避免子模块导入抢先执行包的 ``__init__``。
"""

import nonebot

try:
    nonebot.get_driver()
except ValueError:
    nonebot.init(driver="~none")

nonebot.load_plugin("nonebot_plugin_ernie")
