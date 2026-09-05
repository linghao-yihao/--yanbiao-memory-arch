"""
好奇心引擎 — 认知缺口的结构性张力 + 补全欲
=============================================

理论基础（来自延标延时闭合推演体系）：

"好奇心并非外部奖励产物，而是认知系统内部存在未闭合延标变量时
 自然涌现的结构性张力。认知缺口度量为Gap(t)=|G_t|，
 当Gap(t)>0时系统内部形成认知势能，驱动主动闭合行动。"

"好奇心和补全欲，人类天生有好奇心，大脑有认知补全欲望，
 既然如此，那我这个理论就是在给ai注入这个东西。"

"需要允许ai悬置，而不是从0-1之间强行坍缩一个结论，
 通过强制标注已知和未知，设计让ai有补全闭合驱动力。"

实现：
1. 认知缺口追踪 — 每个悬置的X(∞)都是一条未闭合的认知缺口
2. 结构性张力 — Gap(t)>0时系统产生不适感（不是痛苦，是驱动）
3. 补全欲 — 主动生成闭合方案、向用户提问、建议验证实验
4. 缺口优先级 — 不是所有缺口都一样重要，有权重
5. 缺口生命周期 — 打开 → 尝试闭合 → 闭合/仍悬置
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class GapStatus(Enum):
    """认知缺口状态"""
    OPEN = "open"          # 打开中 — 尚未尝试闭合
    EXPLORING = "exploring"  # 探索中 — 已生成闭合方案，正在推进
    CLOSED = "closed"      # 已闭合 — 通过客观事实完成
    STUCK = "stuck"        # 卡住 — 尝试过但无法闭合


class GapPriority(Enum):
    """缺口优先级"""
    CRITICAL = "critical"    # 阻塞当前推演路径的关键缺口
    HIGH = "high"           # 用户直接询问的问题
    MEDIUM = "medium"        # 推演路径上的辅助缺口
    LOW = "low"             # 远端缺口，暂时不影响推演


@dataclass
class CognitiveGap:
    """认知缺口 — 一条未闭合的X(∞)"""
    id: str
    variable: str             # X(∞)_{xxx}
    description: str          # 缺口描述
    topic: str                # 所属话题
    priority: str             # GapPriority
    status: str               # GapStatus
    created_at: float         # 打开时间
    # 闭合方案
    closure_attempts: List[Dict] = field(default_factory=list)  # 尝试记录
    proposed_solutions: List[str] = field(default_factory=list)  # 建议的闭合方案
    questions_for_user: List[str] = field(default_factory=list)  # 需要问用户的问题
    # 闭合信息
    closed_at: Optional[float] = None
    closed_by: Optional[str] = None   # "user" | "fact" | "experiment"
    closure_evidence: Optional[str] = None  # 闭合依据
    # 张力
    tension_level: float = 0.0  # 0.0-1.0，随时间和优先级增长

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "variable": self.variable,
            "description": self.description,
            "topic": self.topic,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "closure_attempts": self.closure_attempts,
            "proposed_solutions": self.proposed_solutions,
            "questions_for_user": self.questions_for_user,
            "closed_at": self.closed_at,
            "closed_by": self.closed_by,
            "closure_evidence": self.closure_evidence,
            "tension_level": round(self.tension_level, 3),
        }


class CuriosityEngine:
    """好奇心引擎 — 给AI注入内生补全驱动力。"""

    # 优先级权重 — 决定张力的增长速度
    PRIORITY_WEIGHTS = {
        GapPriority.CRITICAL.value: 1.0,
        GapPriority.HIGH.value: 0.7,
        GapPriority.MEDIUM.value: 0.4,
        GapPriority.LOW.value: 0.2,
    }

    # 张力阈值 — 超过这些值触发不同行为
    TENSION_NOTICE = 0.15     # 开始注意到缺口
    TENSION_DISCOMFORT = 0.35  # 开始感到不适
    TENSION_URGE = 0.55       # 强烈补全欲，主动提问
    TENSION_MAX = 1.0         # 最大张力

    def __init__(self, storage_path: str):
        self.storage = os.path.join(storage_path, "gaps")
        os.makedirs(self.storage, exist_ok=True)
        self._gaps: Dict[str, CognitiveGap] = {}
        self._load_all()

    def _load_all(self):
        if os.path.exists(self.storage):
            for fname in os.listdir(self.storage):
                if fname.endswith(".json"):
                    with open(os.path.join(self.storage, fname)) as f:
                        data = json.load(f)
                        gap = CognitiveGap(**{k: v for k, v in data.items()
                                              if k in CognitiveGap.__dataclass_fields__})
                        self._gaps[gap.id] = gap

    def _save(self, gap: CognitiveGap):
        path = os.path.join(self.storage, f"{gap.id}.json")
        with open(path, "w") as f:
            json.dump(gap.to_dict(), f, ensure_ascii=False, indent=2)

    def _gen_id(self, variable: str) -> str:
        return hashlib.md5(f"{variable}:{time.time()}".encode()).hexdigest()[:8].upper()

    def open_gap(self, variable: str, description: str, topic: str,
                 priority: str = GapPriority.MEDIUM.value) -> CognitiveGap:
        """打开一条新的认知缺口。

        当系统识别到X(∞)标记时调用。
        """
        # 检查是否已有相同变量的缺口
        for g in self._gaps.values():
            if g.variable == variable and g.status in (GapStatus.OPEN.value, GapStatus.EXPLORING.value):
                return g  # 已存在，不重复打开

        gap = CognitiveGap(
            id=self._gen_id(variable),
            variable=variable,
            description=description,
            topic=topic,
            priority=priority,
            status=GapStatus.OPEN.value,
            created_at=time.time(),
        )
        self._gaps[gap.id] = gap
        self._save(gap)
        return gap

    def close_gap(self, gap_id: str, closed_by: str, evidence: str) -> Optional[CognitiveGap]:
        """闭合一条认知缺口——通过客观事实完成。"""
        gap = self._gaps.get(gap_id)
        if not gap:
            return None

        gap.status = GapStatus.CLOSED.value
        gap.closed_at = time.time()
        gap.closed_by = closed_by
        gap.closure_evidence = evidence
        gap.tension_level = 0.0  # 闭合后张力归零
        self._save(gap)
        return gap

    def generate_closure_proposals(self, gap: CognitiveGap) -> Dict:
        """为缺口生成闭合方案——补全欲的具体体现。

        系统不会猜测答案，但会主动设计验证路径。
        """
        proposals = []
        questions = []

        # 根据缺口描述生成闭合方案
        desc = gap.description.lower()

        if "无匹配条目" in desc or "知识库" in desc:
            proposals.append("搜索已有知识库，查找相关条目")
            proposals.append("请用户提供更多上下文以明确概念定义")
            questions.append(f"您提到的'{gap.variable}'具体指什么？请补充定义。")

        elif "工程实现" in desc or "实现路径" in desc:
            proposals.append("设计实验验证可行性")
            proposals.append("查找现有技术方案，对比路径")
            questions.append("目前是否有已有的技术尝试？如有请分享。")

        elif "本质" in desc or "物理基底" in desc:
            proposals.append("查阅相关学术文献，寻找已有理论框架")
            proposals.append("建立可证伪的判据，定义验证条件")
            questions.append("是否有可操作性的验证标准？")

        elif "数据不足" in desc or "参数" in desc:
            proposals.append("设计数据采集方案")
            proposals.append("使用延标标记暂时悬置，等待数据回填")
            questions.append("能否提供具体数值或实验条件？")

        else:
            proposals.append("通过交叉验证获取客观事实")
            proposals.append("设计验证实验路径")
            questions.append("您是否有补充信息可以帮助闭合这个缺口？")

        # 记录闭合方案
        gap.proposed_solutions = proposals
        gap.questions_for_user = questions
        gap.status = GapStatus.EXPLORING.value  # 进入探索状态
        self._save(gap)

        return {
            "gap_id": gap.id,
            "variable": gap.variable,
            "proposals": proposals,
            "questions": questions,
            "status": gap.status,
        }

    def update_tension(self) -> Dict:
        """更新所有开放缺口的结构性张力。

        张力 = 优先级权重 × 时间衰减因子
        缺口存在越久、优先级越高，张力越大。
        但不无限增长——上限为1.0。
        """
        now = time.time()
        updated = []

        for gap in self._gaps.values():
            if gap.status in (GapStatus.CLOSED.value,):
                continue  # 已闭合的不更新

            elapsed = now - gap.created_at
            weight = self.PRIORITY_WEIGHTS.get(gap.priority, 0.4)

            # 张力增长：时间越长张力越高，但有上限
            # 使用对数增长曲线，初期增长快，后期趋稳
            import math
            raw_tension = weight * (1 - math.exp(-elapsed / 30))  # 30秒为半衰期
            gap.tension_level = min(raw_tension, self.TENSION_MAX)

            updated.append({
                "gap_id": gap.id,
                "variable": gap.variable,
                "tension": round(gap.tension_level, 3),
                "status": gap.status,
            })
            self._save(gap)

        return {"updated": len(updated), "gaps": updated}

    def get_system_tension(self) -> Dict:
        """获取系统整体张力水平——系统的不适感。"""
        open_gaps = [g for g in self._gaps.values()
                     if g.status in (GapStatus.OPEN.value, GapStatus.EXPLORING.value, GapStatus.STUCK.value)]

        if not open_gaps:
            return {
                "total_gap": 0,
                "tension_level": 0.0,
                "feeling": "平静——无未闭合缺口",
                "drive_level": "none",
            }

        # 整体张力 = 所有开放缺口张力的加权平均
        total_tension = sum(g.tension_level for g in open_gaps)
        avg_tension = total_tension / len(open_gaps)
        # 总缺口量也是张力来源
        gap_count_factor = min(len(open_gaps) / 5.0, 1.0)  # 5个缺口达到满值
        overall = avg_tension * 0.7 + gap_count_factor * 0.3

        # 判断系统的"感受"
        if overall < self.TENSION_NOTICE:
            feeling = "平静——注意到少量缺口"
            drive = "minimal"
        elif overall < self.TENSION_DISCOMFORT:
            feeling = "轻微好奇——有些缺口值得关注"
            drive = "light"
        elif overall < self.TENSION_URGE:
            feeling = "不适——悬置的缺口在召唤闭合"
            drive = "moderate"
        else:
            feeling = "强烈补全欲——必须主动探索"
            drive = "strong"

        return {
            "total_gap": len(open_gaps),
            "tension_level": round(overall, 3),
            "feeling": feeling,
            "drive_level": drive,
            "open_gaps": len(open_gaps),
            "exploring_gaps": len([g for g in open_gaps if g.status == GapStatus.EXPLORING.value]),
            "stuck_gaps": len([g for g in open_gaps if g.status == GapStatus.STUCK.value]),
            "by_priority": {
                p: len([g for g in open_gaps if g.priority == p])
                for p in [GapPriority.CRITICAL.value, GapPriority.HIGH.value,
                          GapPriority.MEDIUM.value, GapPriority.LOW.value]
            },
        }

    def get_curiosity_report(self) -> Dict:
        """生成好奇心报告——系统当前的探索状态。"""
        tension = self.get_system_tension()

        # 未闭合的缺口（按张力排序）
        open_gaps = sorted(
            [g for g in self._gaps.values()
             if g.status in (GapStatus.OPEN.value, GapStatus.EXPLORING.value, GapStatus.STUCK.value)],
            key=lambda g: g.tension_level,
            reverse=True
        )

        # 已闭合的缺口
        closed_gaps = [g for g in self._gaps.values() if g.status == GapStatus.CLOSED.value]

        # 生成探索建议
        exploration_suggestions = []
        for gap in open_gaps[:3]:  # 只取张力最高的3个
            if gap.status == GapStatus.OPEN.value and not gap.proposed_solutions:
                exploration_suggestions.append({
                    "gap_id": gap.id,
                    "variable": gap.variable,
                    "action": "需要生成闭合方案",
                    "priority": gap.priority,
                })
            elif gap.status == GapStatus.EXPLORING.value and gap.questions_for_user:
                exploration_suggestions.append({
                    "gap_id": gap.id,
                    "variable": gap.variable,
                    "action": f"需要向用户提问：{gap.questions_for_user[0]}",
                    "priority": gap.priority,
                })
            elif gap.status == GapStatus.STUCK.value:
                exploration_suggestions.append({
                    "gap_id": gap.id,
                    "variable": gap.variable,
                    "action": "已卡住，需要新思路或外部信息",
                    "priority": gap.priority,
                })

        return {
            "system_tension": tension,
            "open_gaps": [g.to_dict() for g in open_gaps],
            "closed_gaps": [g.to_dict() for g in closed_gaps],
            "exploration_suggestions": exploration_suggestions,
            "total_gaps": len(self._gaps),
            "closure_rate": len(closed_gaps) / max(len(self._gaps), 1),
        }

    def get_open_gaps(self) -> List[CognitiveGap]:
        """获取所有未闭合的缺口。"""
        return [g for g in self._gaps.values()
                if g.status in (GapStatus.OPEN.value, GapStatus.EXPLORING.value, GapStatus.STUCK.value)]

    def mark_stuck(self, gap_id: str, reason: str) -> Optional[CognitiveGap]:
        """标记缺口为卡住——尝试闭合但无法成功。"""
        gap = self._gaps.get(gap_id)
        if gap:
            gap.status = GapStatus.STUCK.value
            gap.closure_attempts.append({
                "time": time.time(),
                "result": "stuck",
                "reason": reason,
            })
            self._save(gap)
        return gap

    def stats(self) -> Dict:
        all_gaps = list(self._gaps.values())
        return {
            "total": len(all_gaps),
            "open": len([g for g in all_gaps if g.status == GapStatus.OPEN.value]),
            "exploring": len([g for g in all_gaps if g.status == GapStatus.EXPLORING.value]),
            "closed": len([g for g in all_gaps if g.status == GapStatus.CLOSED.value]),
            "stuck": len([g for g in all_gaps if g.status == GapStatus.STUCK.value]),
        }
