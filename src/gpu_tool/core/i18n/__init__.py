# 国际化(i18n)管理器
import os
import sys

class I18n:
    """国际化管理器，用于加载不同语言的翻译"""

    def __init__(self, language='auto'):
        """
        初始化国际化管理器

        Args:
            language: 语言设置，可选值为 'auto', 'en', 'zh-cn'
                     'auto' 会根据系统环境变量自动判断
        """
        self.language = self._determine_language(language)
        self._load_translations()

    def _determine_language(self, language):
        """
        确定最终使用的语言

        Args:
            language: 用户指定的语言设置

        Returns:
            最终使用的语言代码 ('en' 或 'zh-cn')
        """
        if language == 'auto':
            # 尝试从环境变量获取语言设置
            lang_env = os.environ.get('LANG', '').lower()
            if 'zh' in lang_env or 'cn' in lang_env:
                return 'zh-cn'
            else:
                return 'en'
        elif language in ['en', 'zh-cn']:
            return language
        else:
            # 默认使用英文
            return 'en'

    def _load_translations(self):
        """加载指定语言的翻译文件"""
        try:
            if self.language == 'zh-cn':
                from core.i18n import zh_cn
                module = zh_cn
            else:
                from core.i18n import en
                module = en
            
            # 获取模块中所有不以_开头的变量
            self.translations = {k: v for k, v in vars(module).items() if not k.startswith('_')}
        except ImportError as e:
            print(f"Failed to load translation file: {e}")
            # 如果加载失败，使用空字典
            self.translations = {}

    def get(self, key, default=None):
        """
        获取指定键的翻译文本

        Args:
            key: 翻译键
            default: 如果找不到翻译，返回的默认值

        Returns:
            翻译后的文本
        """
        return self.translations.get(key, default or key)

    def __getitem__(self, key):
        """支持字典式访问"""
        return self.get(key)

    def __getattr__(self, name):
        """支持属性式访问"""
        return self.get(name)


# 创建全局i18n实例
_i18n_instance = None

def init_i18n(language='auto'):
    """
    初始化全局i18n实例

    Args:
        language: 语言设置

    Returns:
        I18n实例
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(language)
    return _i18n_instance

def get_i18n():
    """
    获取全局i18n实例

    Returns:
        I18n实例
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance
