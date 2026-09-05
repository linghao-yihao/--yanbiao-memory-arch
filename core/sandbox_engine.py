"""
Layer 3: 沙盒引擎 — 架空现实推演
===================================

"改那些不符合常理的，都是在沙盒推演那里的"
"改一个定义就把旧的定义压缩了，用户再提出来的时候再解压"
"偷换概念那一类攻击...沙盒、定义归档、语义确认能挡掉"
"想要爽快可以啊，沙盒推演呗，直接架空现实好了"
"文末加上：为沙盒推演，已架空现实，不可现实使用"
"利好那些写小说的，开脑洞的，天马行空之类的"

功能：
1. 定义压缩/解压 — 修改定义时，旧定义不删除，压缩归档
2. 架空现实模式 — 允许违反常理的推演，但标记免责声明
3. 偷换概念防护 — 概念替换必须显式声明
4. 创意推演 — 为小说/脑洞/天马行空提供推演空间
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


SANDBOX_DISCLAIMER = "为沙盒推演，已架空现实，不可现实使用"


@dataclass
class ArchivedDefinition:
    """压缩归档的旧定义"""
    id: str
    term: str                # 被修改的概念
    original_definition: str  # 原定义
    new_definition: str       # 新定义
    compressed_at: float     # 压缩时间
    reason: str             # 修改原因
    restored: bool = False   # 是否已解压恢复


@dataclass
class SandboxSession:
    """沙盒推演会话"""
    id: str
    user_id: str
    scenario: str            # 推演场景描述
    rules_overridden: List[str]  # 被覆盖的规则
    deductions: List[str]    # 推演结果
    created_at: float = field(default_factory=time.time)
    disclaimer_added: bool = True


class SandboxEngine:
    """沙盒引擎。"""

    def __init__(self, storage_path: str):
        self.storage = os.path.join(storage_path, "sandbox")
        os.makedirs(self.storage, exist_ok=True)
        os.makedirs(os.path.join(self.storage, "archives"), exist_ok=True)
        os.makedirs(os.path.join(self.storage, "sessions"), exist_ok=True)
        self._archives: Dict[str, ArchivedDefinition] = {}
        self._sessions: Dict[str, SandboxSession] = {}
        self._load_all()

    # def _load_all(self):
    #     arch_dir = os.path.join(self.storage, "archives")
    #     if os.path.exists(arch_dir):
    #         for fname in os.listdir(arch_dir):
    #             if fname.endswith(".json"):
    #                 with open(os.path.join(arch_dir, fname)) as f:
    #                     data = json.load(f)
    #                     a = ArchivedDefinition(**{k: v for k, v in data.items()
    #                                               if k in ArchivedDefinition.__dataclass_fields__})
    #                     self._archives[a.id] = a
    #     sess_dir = os.path.join(self.storage, "sessions")
    #     if os.path.exists(sess_dir):
    #         for fname in os.listdir(sess_dir):
    #             if fname.endswith(".json"):
    #                 with open(os.path.join(sess_dir, fname)) as f:
    #                     data = json.load(f)
    #                     s = SandboxSession(**{k: v for k, v in data.items()
    #                                            if k in SandboxSession.__dataclass_fields__})
    #                     self._sessions[s.id] = s

    # def _save_archive(self, arch: ArchivedDefinition):
    #     path = os.path.join(self.storage, "archives", f"{arch.id}.json")
    #     with open(path, "w") as f:
    #         json.dump(arch.__dict__, f, ensure_ascii=False, indent=2)

    # def _save_session(self, sess: SandboxSession):
    #     path = os.path.join(self.storage, "sessions", f"{sess.id}.json")
    #     with open(path, "w") as f:
    #         json.dump(sess.__dict__, f, ensure_ascii=False, indent=2)

    def _load_all(self):
        arch_dir = os.path.join(self.storage, "archives")
        if os.path.exists(arch_dir):
            for fname in os.listdir(arch_dir):
                if fname.endswith(".json"):
                    with open(os.path.join(arch_dir, fname), encoding='utf-8') as f:  # ✅
                        data = json.load(f)
                        a = ArchivedDefinition(**{k: v for k, v in data.items()
                                                if k in ArchivedDefinition.__dataclass_fields__})
                        self._archives[a.id] = a
        sess_dir = os.path.join(self.storage, "sessions")
        if os.path.exists(sess_dir):
            for fname in os.listdir(sess_dir):
                if fname.endswith(".json"):
                    with open(os.path.join(sess_dir, fname), encoding='utf-8') as f:  # ✅
                        data = json.load(f)
                        s = SandboxSession(**{k: v for k, v in data.items()
                                            if k in SandboxSession.__dataclass_fields__})
                        self._sessions[s.id] = s

    def _save_archive(self, arch: ArchivedDefinition):
        path = os.path.join(self.storage, "archives", f"{arch.id}.json")
        # ✅ 指定 encoding='utf-8'
        with open(path, "w", encoding='utf-8') as f:
            json.dump(arch.__dict__, f, ensure_ascii=False, indent=2)

    def _save_session(self, sess: SandboxSession):
        path = os.path.join(self.storage, "sessions", f"{sess.id}.json")
        # ✅ 指定 encoding='utf-8'
        with open(path, "w", encoding='utf-8') as f:
            json.dump(sess.__dict__, f, ensure_ascii=False, indent=2)


    def compress_definition(self, term: str, original_def: str,
                            new_def: str, reason: str = "") -> ArchivedDefinition:
        """压缩旧定义——改一个定义就把旧的定义压缩了。

        旧定义不删除，归档保存。用户再次提出时可以解压恢复。
        """
        arch = ArchivedDefinition(
            id=hashlib.md5(f"{term}:{time.time()}".encode()).hexdigest()[:8].upper(),
            term=term,
            original_definition=original_def,
            new_definition=new_def,
            compressed_at=time.time(),
            reason=reason,
        )
        self._archives[arch.id] = arch
        self._save_archive(arch)
        return arch

    def decompress_definition(self, term: str) -> Optional[ArchivedDefinition]:
        """解压旧定义——用户再次提出时恢复。

        "用户再提出来的时候再解压"
        """
        for arch in self._archives.values():
            if arch.term == term and not arch.restored:
                arch.restored = True
                self._save_archive(arch)
                return arch
        return None

    def detect_concept_swap(self, original_term: str, new_term: str,
                            context: str) -> Dict:
        """偷换概念检测。

        "偷换概念那一类攻击...沙盒、定义归档、语义确认能挡掉"

        检测推理链中是否有概念被偷偷替换。
        """
        # 如果概念不同且没有显式声明替换
        if original_term != new_term:
            has_explicit_swap = any(m in context for m in [
                "重新定义", "概念替换", "换一个说法", "在此上下文中",
                "这里指的是",
            ])
            if not has_explicit_swap:
                return {
                    "detected": True,
                    "original": original_term,
                    "swapped_to": new_term,
                    "severity": "high",
                    "action": "阻断：检测到概念可能被偷换。需显式声明概念替换，或进入沙盒推演。",
                }
        return {"detected": False}

    def create_sandbox(self, user_id: str, scenario: str,
                       rules_to_override: Optional[List[str]] = None) -> SandboxSession:
        """创建沙盒推演会话——架空现实。"""
        sess = SandboxSession(
            id=hashlib.md5(f"{user_id}:{scenario}:{time.time()}".encode()).hexdigest()[:8].upper(),
            user_id=user_id,
            scenario=scenario,
            rules_overridden=rules_to_override or [],
            deductions=[],
        )
        self._sessions[sess.id] = sess
        self._save_session(sess)
        return sess

    def add_deduction(self, session_id: str, deduction: str) -> str:
        """在沙盒中添加推演结果。"""
        sess = self._sessions.get(session_id)
        if not sess:
            return "沙盒会话不存在"

        # 每条推演结果自动加上免责声明
        marked = f"{deduction}\n⚠ {SANDBOX_DISCLAIMER}"
        sess.deductions.append(marked)
        self._save_session(sess)
        return marked

    def get_session(self, session_id: str) -> Optional[SandboxSession]:
        return self._sessions.get(session_id)

    def list_sessions(self, user_id: Optional[str] = None) -> List[SandboxSession]:
        if user_id:
            return [s for s in self._sessions.values() if s.user_id == user_id]
        return list(self._sessions.values())

    def list_archives(self) -> List[ArchivedDefinition]:
        return list(self._archives.values())

    def stats(self) -> Dict:
        return {
            "total_sessions": len(self._sessions),
            "total_archives": len(self._archives),
            "active_sandboxes": len([s for s in self._sessions.values() if s.deductions]),
        }
