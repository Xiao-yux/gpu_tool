import json
import os
from typing import Any, Dict, List, Union, Optional
from pathlib import Path

class JsonDB:
    def __init__(self, file_path: str, auto_save: bool = False):
        self.file_path = os.path.abspath(file_path)
        self.ensure_file(self.file_path)
        self.auto_save = auto_save
        self._data: Dict[str, Any] = {}
        self._load()

    # ---------- 内部工具 ----------
    def _load(self) -> None:
        if os.path.getsize(self.file_path) == 0:  # 文件空
            self._data = {}
            return
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    PathLike = Union[str, bytes, os.PathLike]

    @staticmethod
    def ensure_file(path: Union[str, os.PathLike[str]], 
                    *,
                    mkdir: bool = True,
                    content: Optional[str] = None,
                    encoding: str = "utf-8",
                    mode: str = "w",  # "w" / "a" / "x"  或 None（只创建空文件）
                    permissions: Optional[int] = None
                    ) -> tuple[bool, str]:
        """
        创建文件并写入内容（可选）。
        返回 (success, message)
        """
        try:
            # 1. 统一转成 Path 对象，并展开 ~ 和环境变量
            p = Path(path).expanduser().expanduser().resolve()

            # 2. 若目录不存在，按需创建
            if mkdir:
                parent = p.parent
                if not parent.exists():
                    parent.mkdir(parents=True, exist_ok=True)

            # 3. 若仅想创建空文件且已存在，直接返回
            if mode is None and p.exists():
                return True, f"文件已存在: {p}"

            # 4. 写入/追加内容
            if mode in {"w", "a", "x"}:
                with p.open(mode, encoding=encoding) as f:
                    if content is not None:
                        f.write(content)
            elif mode is None:
                # 只创建空文件
                p.touch(exist_ok=True)
            else:
                return False, f"不支持的 mode: {mode}"

            # 5. 设置权限（可选）
            if permissions is not None:
                os.chmod(p, permissions)

            return True, f"文件已创建: {p}"

        except Exception as e:
            return False, f"创建文件失败: {e}"

    def _maybe_save(self) -> None:
        if self.auto_save:
            self.save()

    # ---------- 对外 API ----------
    def add(self, key: str, value: Any) -> None:
        """
        多次 add 同一 key，自动升级为数组并追加：
        第 1 次: add('user','alice')   -> {'user': 'alice'}
        第 2 次: add('user','bob')     -> {'user': ['alice', 'bob']}
        第 3 次: add('user','c')       -> {'user': ['alice', 'bob', 'c']}
        """
        if key not in self._data:
            # 第一次：直接存
            self._data[key] = value
        else:
            exist = self._data[key]
            if isinstance(exist, list):
                # 已经是数组，直接追加
                exist.append(value)
            else:
                # 升级成数组
                self._data[key] = [exist, value]
        self._maybe_save()
    def get(self,key):
        try:
            return self._data[key]
        except KeyError:
            return None

    def edit(self, key: str, value: Any) -> None:
        """整体覆盖，不做数组升级"""
        self._data[key] = value
        self._maybe_save()

    # 让对象像 dict 一样使用
    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._maybe_save()

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        return f"JsonDB({self._data})"