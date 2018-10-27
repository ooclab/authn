class GlobalSetting:
    """便于程序内部交换全局设置

    TODO: 替换 from eva.conf import settings

    1. 从环境变量读取
    2. 从配置文件读取
    3. 运行时其他代码自行设置
    """

    __conf = {}

    @staticmethod
    def get(name, default=None):
        return GlobalSetting.__conf.get(name, default)

    @staticmethod
    def set(name, value):
        GlobalSetting.__conf[name] = value
