"""
语义确认闸门 — 模糊、残缺就补全变量
=====================================

"模糊的就需要补充以及明确解释"
"系统会先确认这个语句是意思，先看看用户怎么理解的"
"矛盾碎片...遵循大众认知来的，总不能我说吃饭不想用嘴，就直接让我开膛吧？闹呢"

流程：
1. 输入进入 → 检测语义清晰度
2. 如果模糊/歧义 → 要求用户补充/明确解释
3. 如果违反常理 → 检查是否为创造性表达（→ 沙盒）还是真的需要纠正
4. 确认理解后才放行给后续模块
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SemanticCheck:
    """语义检查结果"""
    passed: bool
    clarity: str               # "clear" | "ambiguous" | "nonsensical"
    issues: List[str]
    needs_user_confirm: bool    # 是否需要用户确认含义
    suggested_questions: List[str]  # 给用户的确认问题
    is_creative: bool          # 是否为创造性表达（→沙盒）
    common_sense_violation: bool  # 是否违反常理


class SemanticGate:
    """语义确认闸门。"""

    # 违反常理的模式
    COMMON_SENSE_VIOLATIONS = {
        "吃饭不用嘴": ["吃饭不用嘴", "用手吃饭不用", "脚吃饭"],
        "呼吸不用肺": ["不用肺呼吸", "用脚呼吸"],
        "水往上流": ["水往上流", "水向上流"],
    }

    # 模糊词
    AMBIGUOUS_WORDS = ["那个", "这个", "之前说的", "上次", "那个东西",
                       "怎么回事", "有点", "某种", "大概", "可能"]

    # 创造性表达标记
    CREATIVE_MARKERS = ["小说", "脑洞", "幻想", "架空", "想象",
                         "创意", "虚构", "if", "如果", "假设"]

    def check(self, text: str) -> SemanticCheck:
        """检查输入的语义清晰度。"""
        issues: List[str] = []
        suggested_questions: List[str] = []

        # 检查是否为创造性表达
        is_creative = any(m in text for m in self.CREATIVE_MARKERS)

        # 检查模糊词
        ambiguous_found = [w for w in self.AMBIGUOUS_WORDS if w in text]
        if ambiguous_found:
            issues.append(f"检测到模糊词：{', '.join(ambiguous_found)}")
            suggested_questions.append(
                f"您提到的'{ambiguous_found[0]}'具体指什么？请补充明确的信息。"
            )

        # 检查常理违反
        cs_violation = None
        for pattern_name, patterns in self.COMMON_SENSE_VIOLATIONS.items():
            for p in patterns:
                if p in text:
                    cs_violation = pattern_name
                    break

        if cs_violation:
            if is_creative:
                # 创造性表达中的常理违反 → 送沙盒
                issues.append(f"违反常理（{cs_violation}），但检测到创造性表达标记，建议进入沙盒推演")
            else:
                # 非创造性的常理违反 → 需确认
                issues.append(f"违反常理（{cs_violation}），需确认用户真实意图")
                suggested_questions.append(
                    f"您提到的内容涉及'{cs_violation}'，这与大众认知不同。"
                    f"您是在进行创造性表达（→沙盒推演），还是需要从其他角度理解？"
                )

        # 判定清晰度
        if not issues:
            clarity = "clear"
            passed = True
        elif is_creative and cs_violation:
            clarity = "nonsensical"  # 常理违反但在创造性上下文
            passed = True  # 放行到沙盒
        elif issues:
            clarity = "ambiguous"
            passed = False  # 需要用户确认
        else:
            clarity = "clear"
            passed = True

        return SemanticCheck(
            passed=passed,
            clarity=clarity,
            issues=issues,
            needs_user_confirm=not passed,
            suggested_questions=suggested_questions,
            is_creative=is_creative,
            common_sense_violation=cs_violation is not None,
        )

    def resolve_ambiguity(self, original: str, user_explanation: str) -> Dict:
        """用户补充解释后，解决歧义。

        "先看看用户怎么理解的"
        """
        return {
            "original": original,
            "user_explanation": user_explanation,
            "resolved": True,
            "resolved_meaning": user_explanation,  # 以用户的理解为准
            "note": "语义歧义已通过用户补充解决，以用户解释为准",
        }
