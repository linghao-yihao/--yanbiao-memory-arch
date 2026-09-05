"""
概率个体化谬误防护（PIF Guard）
================================

核心原则：群体频率 ≠ 个体真值

"大数定律保证样本量趋于无穷时，群体频率收敛于客观概率；
 但大数定律对单个个体的预测不存在逻辑约束力。
 群体统计结论不能直接等价于个体的现实判断。"

"断章取义？直接让对方把数据来源列出来，是否属实，是否是全貌，
 依据已知情况，不可直接作用于个体，这会产生概率个体化谬误"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PIFAlert:
    """PIF警报"""
    triggered: bool
    group_data: str       # 群体频率描述
    individual_target: str  # 被套用的个体
    reason: str           # 触发原因
    correction: str       # 修正建议


class PIFGuard:
    """概率个体化谬误防护模块。"""

    # 群体统计 → 个体推断的典型模式
    PATTERNS = {
        "gender": {
            "keywords": ["男性", "女性", "男生", "女生", "男人", "女人"],
            "risk": "将性别统计频率直接套用于个体判断",
        },
        "age": {
            "keywords": ["90后", "00后", "年轻人", "老年人", "中年人"],
            "risk": "将年龄群体统计直接套用于个体",
        },
        "region": {
            "keywords": ["南方人", "北方人", "某地人", "城里人", "农村人"],
            "risk": "将地域统计直接套用于个体",
        },
        "probability_to_individual": {
            "keywords": ["概率是", "成功率高", "失败率", "命中率", "通过率"],
            "risk": "将群体概率直接等同于个体结果",
        },
    }

    def check(self, statement: str, target_individual: Optional[str] = None) -> PIFAlert:
        """检查一条陈述是否犯PIF。

        Args:
            statement: 待检查的陈述
            target_individual: 是否针对某个具体个体

        Returns:
            PIFAlert 警报结果
        """
        for category, config in self.PATTERNS.items():
            for kw in config["keywords"]:
                if kw in statement:
                    # 进一步检查是否在针对个体做推断
                    if target_individual or self._targets_individual(statement):
                        return PIFAlert(
                            triggered=True,
                            group_data=f"群体统计关键词: '{kw}' (类别: {category})",
                            individual_target=target_individual or "未具名个体",
                            reason=config["risk"],
                            correction=(
                                "群体频率不能直接等于个体真值。"
                                "如需对个体判断，需获取该个体的具体数据，"
                                "而非用群体统计替代。"
                            ),
                        )
        return PIFAlert(
            triggered=False,
            group_data="",
            individual_target="",
            reason="",
            correction="",
        )

    def _targets_individual(self, text: str) -> bool:
        """检测陈述是否针对某个具体个体。"""
        individual_markers = ["你", "他", "她", "这个人", "那个", "这个", "你一定",
                             "你肯定", "你大概率"]
        return any(m in text for m in individual_markers)

    def validate_source(self, source_claim: str) -> Dict:
        """验证数据来源——防断章取义。

        "直接让对方把数据来源列出来，是否属实，是否是全貌"
        """
        result = {
            "has_source": False,
            "source_verified": False,
            "is_complete": False,
            "issues": [],
        }

        # 检查是否有来源标注
        source_markers = ["来源", "根据", "研究显示", "数据表明", "统计"]
        result["has_source"] = any(m in source_claim for m in source_markers)

        if not result["has_source"]:
            result["issues"].append("缺少数据来源，可能为断章取义")

        # 检查是否有完整性声明
        completeness_markers = ["全貌", "完整", "部分", "仅", "只是"]
        result["is_complete"] = any(m in source_claim for m in completeness_markers)

        if not result["is_complete"]:
            result["issues"].append("未声明是否为全貌，存在断章取义风险")

        return result

    def fact_vs_opinion(self, statement: str) -> Dict:
        """区分事实与观点。

        "事实不是主观，事实是绝对客观的。
         苹果可食用 = 事实，可入公理；
         苹果是世界最好吃的水果 = 主观观点，不入公理。"
        """
        opinion_markers = ["最好", "最差", "应该", "值得", "好看", "难吃",
                          "美丽", "丑陋", "优秀", "糟糕", "喜欢", "讨厌"]

        is_opinion = any(m in statement for m in opinion_markers)

        if is_opinion:
            return {
                "type": "opinion",
                "can_be_axiom": False,
                "reason": "包含主观评价词，属于个人观点，不可入公理库",
                "scope": "session_only",  # 只在用户会话内有效
            }
        else:
            return {
                "type": "fact",
                "can_be_axiom": True,
                "reason": "不含主观评价词，属于客观陈述，可入公理库（需交叉验证）",
                "scope": "universal",  # 公理可公开
            }
