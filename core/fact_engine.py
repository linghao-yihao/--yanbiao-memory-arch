"""
Layer 1: 事实引擎 — 客观事实公理系统
=====================================

"事实不是ai摸索出来的，得交叉验证"
"事实不是主观，事实是绝对客观的"
"苹果，可食用 → 可入公理；苹果是世界最好吃的水果 → 主观，不入公理"

事实层级：
- 客观事实（universal）：可验证、可公开、跨用户共享
  例："苹果可食用"、"水在标准大气压下100°C沸腾"
- 用户验证事实（session）：仅在此用户会话内成立，不公开
  例：用户说自己零基础学编程 → 此会话内成立，其他用户问不会得出一样答案
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .pif_guard import PIFGuard


@dataclass
class Fact:
    """事实条目"""
    id: str
    statement: str           # 事实陈述
    category: str            # "objective" | "user_verified"
    scope: str               # "universal" | "session"
    verified: bool           # 是否已交叉验证
    sources: List[str]       # 来源列表（防断章取义）
    user_id: Optional[str]    # 仅session类型有效
    created_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    def citation(self) -> str:
        return f"[FACT-{self.id[:8]}_{self.scope}]"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "statement": self.statement,
            "category": self.category,
            "scope": self.scope,
            "verified": self.verified,
            "sources": self.sources,
            "user_id": self.user_id,
            "citation": self.citation(),
            "tags": self.tags,
        }


class FactEngine:
    """事实引擎 — 管理客观事实的存储、验证、检索。"""

    def __init__(self, storage_path: str):
        self.storage = os.path.join(storage_path, "facts")
        os.makedirs(self.storage, exist_ok=True)
        os.makedirs(os.path.join(self.storage, "universal"), exist_ok=True)
        os.makedirs(os.path.join(self.storage, "session"), exist_ok=True)
        self.pif = PIFGuard()
        self._facts: Dict[str, Fact] = {}
        self._load_all()

    def _load_all(self):
        """加载所有事实"""
        for scope in ["universal", "session"]:
            path = os.path.join(self.storage, scope)
            for fname in os.listdir(path):
                if fname.endswith(".json"):
                    with open(os.path.join(path, fname)) as f:
                        data = json.load(f)
                        fact = Fact(**{k: v for k, v in data.items()
                                       if k in Fact.__dataclass_fields__})
                        self._facts[fact.id] = fact

    def _save(self, fact: Fact):
        scope_dir = os.path.join(self.storage, fact.scope)
        os.makedirs(scope_dir, exist_ok=True)
        path = os.path.join(scope_dir, f"{fact.id}.json")
        with open(path, "w") as f:
            json.dump(fact.to_dict(), f, ensure_ascii=False, indent=2)

    def _gen_id(self, statement: str) -> str:
        return hashlib.md5(statement.encode()).hexdigest()[:8].upper()

    def register_fact(self, statement: str, user_id: Optional[str] = None,
                      sources: Optional[List[str]] = None,
                      tags: Optional[List[str]] = None) -> Tuple[Fact, Dict]:
        """注册一条事实。

        自动判断是客观事实还是用户验证事实，
        自动检查PIF，自动分类事实/观点。
        """
        # PIF检查
        pif_alert = self.pif.check(statement, target_individual=user_id)
        if pif_alert.triggered:
            return None, {
                "rejected": True,
                "reason": "PIF: 群体频率不能直接套用于个体",
                "alert": pif_alert.__dict__,
            }

        # 事实/观点分类
        classification = self.pif.fact_vs_opinion(statement)

        if classification["type"] == "opinion":
            # 主观观点 → 用户会话级，不公开
            fact = Fact(
                id=self._gen_id(statement + (user_id or "")),
                statement=statement,
                category="user_verified",
                scope="session",
                verified=True,  # 用户已确认
                sources=sources or ["用户自述"],
                user_id=user_id,
                tags=tags or [],
            )
            self._facts[fact.id] = fact
            self._save(fact)
            return fact, {
                "rejected": False,
                "classification": classification,
                "note": "主观观点，仅在用户会话内有效，不公开输出",
            }

        # 客观事实 → 需交叉验证
        fact = Fact(
            id=self._gen_id(statement),
            statement=statement,
            category="objective",
            scope="universal" if not user_id else "universal",  # 客观事实总是universal
            verified=False,  # 待交叉验证
            sources=sources or [],
            user_id=None,  # 客观事实不属于任何用户
            tags=tags or [],
        )
        self._facts[fact.id] = fact
        self._save(fact)
        return fact, {
            "rejected": False,
            "classification": classification,
            "note": "客观事实，需交叉验证后可公开",
            "needs_verification": True,
        }

    def cross_validate(self, fact_id: str, source: str) -> Dict:
        """交叉验证——添加来源，当来源数>=2时标记为已验证。"""
        fact = self._facts.get(fact_id)
        if not fact:
            return {"error": "事实不存在"}

        if source not in fact.sources:
            fact.sources.append(source)

        if len(fact.sources) >= 2:
            fact.verified = True

        self._save(fact)
        return {
            "fact_id": fact.id,
            "sources": fact.sources,
            "verified": fact.verified,
            "source_count": len(fact.sources),
        }

    def query(self, keyword: str, user_id: Optional[str] = None) -> List[Fact]:
        """查询相关事实。

        - universal事实：所有人可见
        - session事实：仅对应用户可见
        """
        results = []
        for fact in self._facts.values():
            if keyword in fact.statement or any(keyword in t for t in fact.tags):
                if fact.scope == "universal":
                    if fact.verified:  # 只有已验证的universal事实才返回
                        results.append(fact)
                elif fact.scope == "session" and fact.user_id == user_id:
                    results.append(fact)
        return results

    def get_all(self, user_id: Optional[str] = None) -> List[Fact]:
        """获取所有事实（按scope过滤）"""
        results = []
        for fact in self._facts.values():
            if fact.scope == "universal" and fact.verified:
                results.append(fact)
            elif fact.scope == "session" and fact.user_id == user_id:
                results.append(fact)
        return results

    def stats(self) -> Dict:
        universal = [f for f in self._facts.values() if f.scope == "universal"]
        session = [f for f in self._facts.values() if f.scope == "session"]
        return {
            "universal_total": len(universal),
            "universal_verified": len([f for f in universal if f.verified]),
            "session_total": len(session),
            "total": len(self._facts),
        }
