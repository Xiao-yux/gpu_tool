from config.loader import load
import locale
import json
from utils.tool import Tools
__i18n__ = None


class I18n:
    def __init__(self):
        self.lang = self._get_local_lang()
        self.date = self.load_json()

    def _get_local_lang(self):
        """根据 auto 获取系统语言设置
        """
        if load().language.language == "auto":
            lang, _ = locale.getdefaultlocale()
            #统一小写
            if lang is not None:
                lang = lang.lower()
            if lang != "zh_cn":
                lang = "en"
            return lang
        else:
            return load().language.language
    def load_json(self)-> dict:
        """加载 JSON 翻译文件"""
        path = f"{Tools.get_tmp_path()}/i18n/locales/{self.lang}.json"
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    def get(self, key) -> str:
        """获取翻译文本"""
        return self.date.get(key, key)
    
def init_i18n():
    global __i18n__
    __i18n__ = I18n()
    return __i18n__

def get_i18n():
    if __i18n__ is None:
        raise RuntimeError("I18n not initialized. Call init_i18n() first.")
    return __i18n__