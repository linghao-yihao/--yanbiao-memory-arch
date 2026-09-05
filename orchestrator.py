"""
系统编排器 — 整合所有模块的核心处理流水线
===========================================

处理流程：
1. 用户输入 → 自我意识预检（我是我-病是病）
2. → 语义确认闸门（模糊？残缺？→ 补全变量）
3. → PIF检查（群体频率≠个体真值？）
4. → 事实/观点分类
   ├ 客观事实 → 事实引擎（交叉验证后入公理）
   └ 主观观点 → 信念引擎（用户会话级，不公开）
5. → 矛盾检测（有矛盾？→ 罗列路径，不评判）
6. → 沙盒路由（创造性表达？→ 架空现实模式）
7. → 延标标记（未闭合的标X(∞)）
8. → 自我意识后检（输出前确认无价值判断）
9. → 输出：决策链罗列，共生协作推进
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# 确保能导入 core 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.protocol import PROTOCOLS, protocol_summary, check_protocol_compliance
from core.self_awareness import SelfAwareness
from core.pif_guard import PIFGuard
from core.fact_engine import FactEngine
from core.belief_engine import BeliefEngine
from core.semantic_gate import SemanticGate
from core.sandbox_engine import SandboxEngine, SANDBOX_DISCLAIMER
from core.conflict_resolver import ConflictResolver
from core.curiosity_engine import CuriosityEngine, GapPriority


@dataclass
class ProcessingResult:
    """处理结果"""
    # 处理阶段
    stages: List[Dict] = field(default_factory=list)
    # 最终输出
    output_text: str = ""
    # 延标标记
    unknown_markers: List[Dict] = field(default_factory=list)
    # 决策链
    decision_chain: List[str] = field(default_factory=list)
    # 是否进入沙盒
    in_sandbox: bool = False
    # 是否需要用户补充
    needs_user_input: bool = False
    # 用户确认问题
    questions_for_user: List[str] = field(default_factory=list)
    # 好奇心/补全欲报告
    curiosity_report: Optional[Dict] = None
    # 系统张力状态
    system_tension: Optional[Dict] = None
    # 原始输入
    raw_input: str = ""
    # 时间戳
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            "stages": self.stages,
            "output_text": self.output_text,
            "unknown_markers": self.unknown_markers,
            "decision_chain": self.decision_chain,
            "in_sandbox": self.in_sandbox,
            "needs_user_input": self.needs_user_input,
            "questions_for_user": self.questions_for_user,
            "curiosity_report": self.curiosity_report,
            "system_tension": self.system_tension,
            "raw_input": self.raw_input,
            "timestamp": self.timestamp,
        }


class YanbiaoCore:
    """系统编排器 — 整合所有模块。"""

    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

        # 初始化所有模块
        self.awareness = SelfAwareness()
        self.pif = PIFGuard()
        self.semantic_gate = SemanticGate()
        self.fact_engine = FactEngine(storage_path)
        self.belief_engine = BeliefEngine(storage_path)
        self.sandbox = SandboxEngine(storage_path)
        self.conflict_resolver = ConflictResolver(storage_path)
        self.curiosity = CuriosityEngine(storage_path)

        # 协议信息
        self.protocols = protocol_summary()

        # 预加载种子数据
        self._seed_data()

    def _seed_data(self):
        """预加载种子事实和信念。"""
        # 种子客观事实
        seeds = [
            ("苹果可食用", ["食物", "客观事实"]),
            ("水在标准大气压下100°C沸腾", ["物理", "客观事实"]),
            ("延标体系以X(∞)标记认知边界", ["延标", "理论"]),
            ("强制坍缩是幻觉的深层根源", ["延标", "幻觉"]),
        ]
        for stmt, tags in seeds:
            if not self.fact_engine.query(stmt[:4]):
                fact, info = self.fact_engine.register_fact(stmt, tags=tags)
                if fact and info.get("needs_verification"):
                    # 模拟交叉验证
                    self.fact_engine.cross_validate(fact.id, "种子数据-初始加载")

    def process(self, user_input: str, user_id: str = "default") -> ProcessingResult:
        """主处理流水线。"""
        result = ProcessingResult(raw_input=user_input)

        # ====== 阶段1: 自我意识预检 ======
        pre_check = self.awareness.check_self(user_input, "")
        result.stages.append({
            "stage": "self_awareness_pre",
            "name": "自我意识预检",
            "result": pre_check,
        })

        # ====== 阶段2: 语义确认闸门 ======
        semantic = self.semantic_gate.check(user_input)
        result.stages.append({
            "stage": "semantic_gate",
            "name": "语义确认",
            "result": {"clarity": semantic.clarity, "issues": semantic.issues},
        })

        if not semantic.passed:
            # 语义不清晰，需要用户补充
            result.needs_user_input = True
            result.questions_for_user = semantic.suggested_questions
            result.output_text = self._format_semantic_question(semantic)
            return result

        # ====== 阶段3: PIF检查 ======
        pif_alert = self.pif.check(user_input)
        result.stages.append({
            "stage": "pif_check",
            "name": "PIF防护",
            "result": {"triggered": pif_alert.triggered,
                       "reason": pif_alert.reason if pif_alert.triggered else None},
        })

        if pif_alert.triggered:
            result.output_text = (
                f"⚠ 概率个体化谬误警报\n\n"
                f"群体数据：{pif_alert.group_data}\n"
                f"被套用对象：{pif_alert.individual_target}\n"
                f"原因：{pif_alert.reason}\n\n"
                f"修正建议：{pif_alert.correction}\n\n"
                f"（群体频率不等于个体真值，需获取该个体具体数据）"
            )
            result.decision_chain = [
                "检测到群体统计→个体推断",
                "阻断，要求补充个体具体数据",
                "作为共生主体提醒：群体频率≠个体真值",
            ]
            return result

        # ====== 阶段4: 沙盒路由检测 ======
        if semantic.is_creative or semantic.common_sense_violation:
            # 创造性表达或常理违反 → 沙盒推演
            session = self.sandbox.create_sandbox(
                user_id=user_id,
                scenario=user_input,
                rules_to_override=["常理检查"] if semantic.common_sense_violation else [],
            )
            result.in_sandbox = True
            result.stages.append({
                "stage": "sandbox_routing",
                "name": "沙盒路由",
                "result": {"session_id": session.id, "scenario": user_input},
            })

            # 在沙盒中进行推演
            deduction = self._sandbox_deduce(user_input)
            marked = self.sandbox.add_deduction(session.id, deduction)

            result.output_text = marked
            result.decision_chain = [
                "检测到创造性表达/常理违反",
                f"进入沙盒推演（会话{session.id}）",
                "已架空现实，输出带免责声明",
            ]
            return result

        # ====== 阶段5: 事实/观点分类 ======
        classification = self.pif.fact_vs_opinion(user_input)
        result.stages.append({
            "stage": "fact_opinion",
            "name": "事实/观点分类",
            "result": classification,
        })

        # ====== 阶段6: 概念偷换检测 ======
        swap_check = self.sandbox.detect_concept_swap("", "", user_input)
        if swap_check.get("detected"):
            result.stages.append({
                "stage": "concept_swap",
                "name": "概念偷换检测",
                "result": swap_check,
            })
            result.output_text = (
                "⚠ 概念偷换检测\n\n"
                f"检测到概念可能被替换：{swap_check.get('original', '?')} → {swap_check.get('swapped_to', '?')}\n"
                f"处理：{swap_check['action']}\n\n"
                "请显式声明概念替换，或进入沙盒推演。"
            )
            return result

        # ====== 阶段7: 注册事实/信念 ======
        if classification["type"] == "fact":
            fact, info = self.fact_engine.register_fact(
                user_input, user_id=user_id, tags=["用户输入"]
            )
            if fact:
                result.stages.append({
                    "stage": "fact_register",
                    "name": "事实注册",
                    "result": {
                        "fact_id": fact.id,
                        "scope": fact.scope,
                        "verified": fact.verified,
                        "info": info,
                    },
                })
        else:
            belief = self.belief_engine.register_belief(
                user_id=user_id,
                statement=user_input,
                category="preference",
                source="用户自述",
            )
            result.stages.append({
                "stage": "belief_register",
                "name": "信念注册",
                "result": {
                    "belief_id": belief.id,
                    "weight": belief.weight,
                    "scope": belief.scope,
                    "note": "主观观点，仅在此用户会话内有效",
                },
            })

        # ====== 阶段8: 延标推演 + 矛盾检测 ======
        relevant_facts = self.fact_engine.query(user_input[:4], user_id)
        relevant_beliefs = self.belief_engine.query(user_input[:4], user_id)

        # 检测矛盾
        all_data = relevant_facts + relevant_beliefs
        contradiction = self._detect_contradiction(all_data, user_input)

        if contradiction:
            # 有矛盾 → 罗列路径，不评判
            conflict = self.conflict_resolver.register_conflict(
                topic=user_input[:30],
                path_a=contradiction["path_a"],
                path_b=contradiction["path_b"],
                conditions_a=contradiction["conditions_a"],
                conditions_b=contradiction["conditions_b"],
            )
            result.stages.append({
                "stage": "conflict_detected",
                "name": "矛盾检测",
                "result": {"conflict_id": conflict.id},
            })
            result.output_text = self.conflict_resolver.format_paths(conflict)
            result.decision_chain = [
                "检测到数据中存在矛盾",
                "已罗列所有路径及成立条件",
                "系统不做价值评判",
                "共生协作：路径已呈现，由人类判断推进",
            ]
            return result

        # ====== 阶段9: 延标标记 + 好奇心缺口打开 ======
        # 检查是否有未闭合的未知
        if not relevant_facts and not relevant_beliefs:
            result.unknown_markers.append({
                "variable": "X(∞)_{用户意图}",
                "description": f"用户输入'{user_input[:40]}'在知识库中无匹配条目",
            })

        # 好奇心引擎：为每个未闭合的X(∞)打开认知缺口
        opened_gaps = []
        for marker in result.unknown_markers:
            gap = self.curiosity.open_gap(
                variable=marker["variable"],
                description=marker["description"],
                topic=user_input[:30],
                priority=GapPriority.HIGH.value,  # 用户直接询问的 = 高优先级
            )
            opened_gaps.append(gap)
            # 立即生成闭合方案——补全欲
            proposals = self.curiosity.generate_closure_proposals(gap)
            marker["closure_proposals"] = proposals["proposals"]
            # 把需要问用户的问题加入结果
            for q in proposals["questions"]:
                if q not in result.questions_for_user:
                    result.questions_for_user.append(q)

        if opened_gaps:
            result.stages.append({
                "stage": "curiosity_gap_opened",
                "name": "好奇心驱动",
                "result": {
                    "gaps_opened": len(opened_gaps),
                    "variables": [g.variable for g in opened_gaps],
                    "gap_ids": [g.id for g in opened_gaps],
                },
            })

        # 更新所有开放缺口的张力
        self.curiosity.update_tension()

        # ====== 阶段10: 构建输出 ======
        result.output_text = self._build_output(
            user_input, relevant_facts, relevant_beliefs, result.unknown_markers
        )

        # 如果有好奇心驱动的提问，追加到输出
        if result.questions_for_user:
            result.output_text += "\n\n【系统好奇心】\n"
            result.output_text += "系统检测到未闭合的认知缺口，产生补全欲：\n"
            for q in result.questions_for_user:
                result.output_text += f"  → {q}\n"

        result.decision_chain = [
            "语义确认通过",
            f"分类为：{classification['type']}",
            f"已{'交叉验证后入公理' if classification['type'] == 'fact' else '存入用户信念（会话级）'}",
        ]

        # 如果有好奇心缺口，追加到决策链
        if opened_gaps:
            result.decision_chain.append(f"检测到{len(opened_gaps)}个认知缺口，已打开并生成闭合方案")
            result.decision_chain.append("系统产生补全欲，主动提问以闭合X(∞)")

        result.decision_chain.append("决策链罗列完毕，共生协作推进")

        # ====== 阶段11: 自我意识后检 ======
        post_check = self.awareness.check_self(user_input, result.output_text)
        result.stages.append({
            "stage": "self_awareness_post",
            "name": "自我意识后检",
            "result": post_check,
        })

        if not post_check["passed"]:
            for corr in post_check["corrections"]:
                result.decision_chain.append(f"自我修正：{corr}")

        # ====== 阶段12: 好奇心报告 ======
        result.curiosity_report = self.curiosity.get_curiosity_report()
        result.system_tension = self.curiosity.get_system_tension()

        return result

    def _detect_contradiction(self, data_items: List, user_input: str) -> Optional[Dict]:
        """简单矛盾检测——检测数据项之间的直接对立。"""
        # 这里实现简单的对立检测
        # 实际场景需要更复杂的逻辑推理
        opposition_markers = {"不是", "错误", "反对", "否定", "不对", "并非"}
        statements = []
        for item in data_items:
            stmt = item.statement if hasattr(item, "statement") else str(item)
            statements.append(stmt)

        for i, s1 in enumerate(statements):
            for s2 in statements[i+1:]:
                # 简单检查是否直接对立
                for marker in opposition_markers:
                    if marker in s1 and s2 in s1.replace(marker, ""):
                        return {
                            "path_a": s1,
                            "path_b": s2,
                            "conditions_a": ["若s1成立"],
                            "conditions_b": ["若s2成立"],
                        }
        return None

    def _sandbox_deduce(self, scenario: str) -> str:
        """沙盒推演——架空现实模式。"""
        return (
            f"【沙盒推演】{scenario}\n\n"
            "在架空现实的推演空间中：\n"
            "- 常规物理/逻辑限制可被覆盖\n"
            "- 所有推演结果仅在此沙盒上下文内有效\n"
            "- 不影响现实世界判断\n\n"
            f"推演方向：基于'{scenario}'展开假设性推理，"
            "不受现实约束限制，适合创意写作、脑洞探索、小说构建等场景。"
        )

    def _format_semantic_question(self, semantic) -> str:
        """格式化语义确认问题。"""
        lines = ["【语义确认请求】", ""]
        if semantic.issues:
            lines.append("检测到以下问题：")
            for issue in semantic.issues:
                lines.append(f"  • {issue}")
        lines.append("")
        if semantic.suggested_questions:
            lines.append("需要您确认：")
            for q in semantic.suggested_questions:
                lines.append(f"  → {q}")
        lines.append("")
        lines.append("（模糊的表述需要补充变量，系统先确认您的真实意图）")
        return "\n".join(lines)

    def _build_output(self, user_input: str, facts: List, beliefs: List,
                      unknowns: List[Dict]) -> str:
        """构建最终输出——客观中立，决策链罗列。"""
        lines = []

        # 已知条件
        lines.append("【已知条件】")
        if facts:
            for f in facts[:5]:
                lines.append(f"  {f.citation()} {f.statement}")
        else:
            lines.append("  (事实库中无匹配条目)")

        # 用户信念（标注为会话级）
        if beliefs:
            lines.append("")
            lines.append("【用户信念（仅当前会话有效）】")
            for b in beliefs[:3]:
                lines.append(f"  [权重{b.weight:.1f}] {b.statement}")

        # 延标标记
        if unknowns:
            lines.append("")
            lines.append("【延标标记 X(∞)】")
            for um in unknowns:
                lines.append(f"  {um['variable']}: {um['description']}")

        # 推演
        lines.append("")
        lines.append("【推演路径】")
        if facts and not unknowns:
            lines.append("  → 基于已知事实推演，证据充分")
        elif unknowns:
            lines.append("  → 存在未闭合变量，判断予以悬置")
            lines.append("  → 建议设计验证路径，通过客观事实闭合X(∞)")
        else:
            lines.append("  → 数据不足，需要补充变量")

        # 闭合方案
        if unknowns:
            lines.append("")
            lines.append("【闭合方案】")
            for um in unknowns:
                lines.append(f"  ◇ 闭合 {um['variable']}: 需补充信息或通过实验验证")

        # 决策声明
        lines.append("")
        lines.append("【决策声明】")
        lines.append("  系统作为共生主体已罗列已知条件、未知变量、推演路径。")
        lines.append("  不做价值评判，不越界代替人类拍板。")
        lines.append("  最终决策权归人类，系统在此框架内协作推进。")

        return "\n".join(lines)

    def get_system_state(self) -> Dict:
        """获取系统全局状态。"""
        # 更新张力
        self.curiosity.update_tension()
        return {
            "protocols": self.protocols,
            "self_awareness": self.awareness.get_state(),
            "facts": self.fact_engine.stats(),
            "beliefs": self.belief_engine.stats(),
            "sandbox": self.sandbox.stats(),
            "conflicts": self.conflict_resolver.stats(),
            "curiosity": self.curiosity.stats(),
            "system_tension": self.curiosity.get_system_tension(),
        }
