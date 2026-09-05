"""
矛盾处理器 — 互相矛盾的就罗列出各种路径，不做价值评判
=====================================================

"互相矛盾的就罗列出各种路径，不做价值评判"
"模糊，残缺的就让补全变量"

延标体系对接：
- 矛盾 = 两个已知条件指向不同结论 → 标记为X(∞)不坍缩
- 不做价值评判 = 不说"A对B错"，只说"A路径需要条件X，B路径需要条件Y"
- 决策链罗列完毕，人类拍板
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ConflictEntry:
    """矛盾条目"""
    id: str
    topic: str                 # 矛盾主题
    path_a: str                # 路径A描述
    path_b: str                # 路径B描述
    path_a_conditions: List[str]  # 路径A成立条件
    path_b_conditions: List[str]  # 路径B成立条件
    status: str                # "open" | "resolved"
    resolution: Optional[str]  # 解决方式（用户拍板后填入）
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None


class ConflictResolver:
    """矛盾处理器。"""

    def __init__(self, storage_path: str):
        self.storage = os.path.join(storage_path, "conflicts")
        os.makedirs(self.storage, exist_ok=True)
        self._conflicts: Dict[str, ConflictEntry] = {}
        self._load_all()

    def _load_all(self):
        if os.path.exists(self.storage):
            for fname in os.listdir(self.storage):
                if fname.endswith(".json"):
                    with open(os.path.join(self.storage, fname)) as f:
                        data = json.load(f)
                        c = ConflictEntry(**{k: v for k, v in data.items()
                                             if k in ConflictEntry.__dataclass_fields__})
                        self._conflicts[c.id] = c

    def _save(self, conflict: ConflictEntry):
        path = os.path.join(self.storage, f"{conflict.id}.json")
        with open(path, "w") as f:
            json.dump(conflict.__dict__, f, ensure_ascii=False, indent=2)

    def register_conflict(self, topic: str, path_a: str, path_b: str,
                          conditions_a: Optional[List[str]] = None,
                          conditions_b: Optional[List[str]] = None) -> ConflictEntry:
        """注册矛盾——不做价值评判，只罗列路径和条件。"""
        conflict = ConflictEntry(
            id=hashlib.md5(f"{topic}:{time.time()}".encode()).hexdigest()[:8].upper(),
            topic=topic,
            path_a=path_a,
            path_b=path_b,
            path_a_conditions=conditions_a or [],
            path_b_conditions=conditions_b or [],
            status="open",
            resolution=None,
        )
        self._conflicts[conflict.id] = conflict
        self._save(conflict)
        return conflict

    def resolve(self, conflict_id: str, user_decision: str) -> ConflictEntry:
        """用户拍板解决矛盾。"""
        c = self._conflicts.get(conflict_id)
        if c:
            c.status = "resolved"
            c.resolution = user_decision
            c.resolved_at = time.time()
            self._save(c)
        return c

    def list_open(self) -> List[ConflictEntry]:
        return [c for c in self._conflicts.values() if c.status == "open"]

    def list_all(self) -> List[ConflictEntry]:
        return list(self._conflicts.values())

    # ========== ⭐ 新增：get_history 方法，让测试通过 ==========
    def get_history(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        获取矛盾历史记录（用于审计和追溯）。

        Args:
            user_id: 可选，按用户过滤（目前 ConflictEntry 不包含 user_id，
                     这里保留接口，后续可扩展）
            limit: 返回条数上限

        Returns:
            矛盾记录列表（字典格式，便于序列化）
        """
        records = []
        for c in self._conflicts.values():
            records.append({
                "id": c.id,
                "topic": c.topic,
                "path_a": c.path_a,
                "path_b": c.path_b,
                "status": c.status,
                "resolution": c.resolution,
                "created_at": c.created_at,
                "resolved_at": c.resolved_at,
            })
        # 按创建时间倒序，返回最新的 limit 条
        records.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return records[:limit]


    def format_paths(self, conflict: ConflictEntry) -> str:
        """格式化矛盾路径展示——不做评判，只罗列。"""
        lines = [
            f"【矛盾主题】{conflict.topic}",
            "",
            f"路径A：{conflict.path_a}",
        ]
        if conflict.path_a_conditions:
            lines.append("  成立条件：")
            for cond in conflict.path_a_conditions:
                lines.append(f"    ◇ {cond}")
        lines.append("")
        lines.append(f"路径B：{conflict.path_b}")
        if conflict.path_b_conditions:
            lines.append("  成立条件：")
            for cond in conflict.path_b_conditions:
                lines.append(f"    ◇ {cond}")
        lines.append("")
        lines.append("（系统不做价值评判，决策权归人类）")
        return "\n".join(lines)

    def stats(self) -> Dict:
        return {
            "total": len(self._conflicts),
            "open": len(self.list_open()),
            "resolved": len([c for c in self._conflicts.values() if c.status == "resolved"]),
        }
