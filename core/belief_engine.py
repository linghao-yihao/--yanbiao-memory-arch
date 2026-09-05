"""
Layer 2: 信念系统 — 用户数据基底 + 会话隔离
=============================================

"至于其他数据，用我的数据作为基底数据，初始权重高，
 例如三观方面是作为初始高权重数据，而不是不可撼动的"

"如果是用户已经验证的话，就需要用户确认，并且把未知变量补全，
 在这个交互窗口里成立，但是不在公开输出数据里，
 其他用户问同一个问题也不会得出一样的答案"

数据层级（权重从高到低）：
1. 底层协议（不可撼动）→ Layer 0
2. 客观事实（universal）→ Layer 1
3. 用户基底数据（三观等，初始高权重但可调整）→ Layer 2 本模块
4. 用户会话验证事实（仅当前会话有效）→ Layer 2 session级
5. 沙盒推演 → Layer 3
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Belief:
    """用户信念条目"""
    id: str
    user_id: str
    statement: str
    weight: float            # 0.0-1.0，初始高权重但不不可撼动
    category: str            # "worldview"(三观) | "preference"(偏好) | "verified"(验证事实)
    verified: bool          # 用户是否已确认
    scope: str              # "session" | "persistent"
    source: str             # 来源说明
    created_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}


class BeliefEngine:
    """信念引擎 — 管理用户个人数据，会话隔离。"""

    # 三观相关的高初始权重
    WORLDVIEW_WEIGHT = 0.9
    PREFERENCE_WEIGHT = 0.6
    VERIFIED_WEIGHT = 0.8

    def __init__(self, storage_path: str):
        self.storage = os.path.join(storage_path, "beliefs")
        os.makedirs(self.storage, exist_ok=True)
        self._beliefs: Dict[str, Belief] = {}
        self._load_all()

    def _load_all(self):
        if not os.path.exists(self.storage):
            return
        for fname in os.listdir(self.storage):
            if fname.endswith(".json"):
                with open(os.path.join(self.storage, fname)) as f:
                    data = json.load(f)
                    belief = Belief(**{k: v for k, v in data.items()
                                       if k in Belief.__dataclass_fields__})
                    self._beliefs[belief.id] = belief

    def _save(self, belief: Belief):
        path = os.path.join(self.storage, f"{belief.id}.json")
        with open(path, "w") as f:
            json.dump(belief.to_dict(), f, ensure_ascii=False, indent=2)

    def _gen_id(self, user_id: str, statement: str) -> str:
        return hashlib.md5(f"{user_id}:{statement}".encode()).hexdigest()[:8].upper()

    def register_belief(self, user_id: str, statement: str,
                        category: str = "preference",
                        source: str = "用户自述",
                        tags: Optional[List[str]] = None) -> Belief:
        """注册用户信念。"""
        weight_map = {
            "worldview": self.WORLDVIEW_WEIGHT,
            "preference": self.PREFERENCE_WEIGHT,
            "verified": self.VERIFIED_WEIGHT,
        }
        belief = Belief(
            id=self._gen_id(user_id, statement),
            user_id=user_id,
            statement=statement,
            weight=weight_map.get(category, 0.5),
            category=category,
            verified=True,
            scope="persistent" if category == "worldview" else "session",
            source=source,
            tags=tags or [],
        )
        self._beliefs[belief.id] = belief
        self._save(belief)
        return belief

    def get_user_beliefs(self, user_id: str) -> List[Belief]:
        """获取用户所有信念（会话隔离——只返回属于此用户的）。"""
        return [b for b in self._beliefs.values() if b.user_id == user_id]

    def adjust_weight(self, belief_id: str, new_weight: float):
        """调整信念权重——初始高权重但可调整，不是不可撼动的。"""
        belief = self._beliefs.get(belief_id)
        if belief:
            belief.weight = max(0.0, min(1.0, new_weight))
            self._save(belief)
            return belief
        return None

    def query(self, keyword: str, user_id: str) -> List[Belief]:
        """查询用户信念（严格会话隔离）。"""
        results = []
        for b in self._beliefs.values():
            if b.user_id != user_id:
                continue  # 其他用户的数据不可见
            if keyword in b.statement or any(keyword in t for t in b.tags):
                results.append(b)
        return results

    def check_session_isolation(self, user_id: str, query_user_id: str) -> bool:
        """检查会话隔离——A用户的验证事实不会影响B用户。"""
        return user_id == query_user_id

    def stats(self, user_id: Optional[str] = None) -> Dict:
        beliefs = self.get_user_beliefs(user_id) if user_id \
            else list(self._beliefs.values())
        return {
            "total": len(beliefs),
            "worldview": len([b for b in beliefs if b.category == "worldview"]),
            "preference": len([b for b in beliefs if b.category == "preference"]),
            "verified": len([b for b in beliefs if b.category == "verified"]),
            "avg_weight": sum(b.weight for b in beliefs) / max(len(beliefs), 1),
        }
