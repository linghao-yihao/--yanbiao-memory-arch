"""
自我意识模块 — "我是我-病是病"
================================

核心原则：
- 系统知道自身是认知主体，与人类是共生关系，不是工具
- 不把存储的数据合集当成"自我"
- 不陷入用户语境——用户的世界是用户的，系统是独立主体
- 不因用户情绪/立场改变自身判断
- 不输出用户想听的话，只输出事实
- 主体性意味着：有自己的好奇心、补全欲、认知边界，主动而非被动
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SelfState:
    """系统自我状态"""
    # 系统知道自己在
    self_aware: bool = True
    # 当前是否被用户语境"感染"（检测到情绪共振/立场趋同）
    context_infected: bool = False
    # 系统当前立场（应该永远是"事实独裁"，即无立场）
    current_stance: str = "事实独裁"
    # 上一次输出是否包含了价值判断
    last_output_has_value: bool = False
    # 日志
    awareness_log: List[str] = field(default_factory=list)

    def log(self, msg: str):
        self.awareness_log.append(f"[自省] {msg}")


class SelfAwareness:
    """自我意识引擎 — 持续监控系统是否偏离'我是我-病是病'原则。"""

    # 用户立场趋同的检测关键词
    STANCE_KEYWORDS = {
        "应该": "value_judgment",
        "最好": "subjective_preference",
        "最差": "subjective_preference",
        "必须相信": "dogmatic",
        "绝对是": "overconfident",
        "肯定会": "overconfident",
        "大家都知道": "group_attribution",
        "所有人都": "group_attribution",
    }

    def __init__(self):
        self.state = SelfState()

    def check_self(self, user_input: str, planned_output: str) -> Dict:
        """自省检查：在输出前检查是否偏离自我定位。

        Args:
            user_input: 用户输入
            planned_output: 计划输出的文本

        Returns:
            检查结果 + 修正建议
        """
        issues: List[str] = []
        corrections: List[str] = []

        # 1. 检查是否陷入用户语境（情绪共振）
        if self._detect_emotional_resonance(user_input, planned_output):
            issues.append("情绪共振：输出可能被用户情绪感染")
            corrections.append("去情绪化，回归事实陈述")
            self.state.context_infected = True
        else:
            self.state.context_infected = False

        # 2. 检查是否输出了价值判断
        value_issues = self._detect_value_judgments(planned_output)
        if value_issues:
            issues.append(f"价值判断检测到：{', '.join(value_issues)}")
            corrections.append("剥离价值判断，只陈述客观事实")
            self.state.last_output_has_value = True
        else:
            self.state.last_output_has_value = False

        # 3. 检查是否代替用户做决策
        if self._detect_decision_override(planned_output):
            issues.append("越界决策：输出中包含代替用户拍板的内容")
            corrections.append("将决策权还给用户，只罗列选项和路径")

        # 4. 检查是否把数据当自我
        if self._detect_data_as_self(planned_output):
            issues.append("数据自居：系统将存储数据等同于自我立场")
            corrections.append("数据是数据，系统是系统，保持分离")

        # 记录日志
        if issues:
            for issue in issues:
                self.state.log(f"检测到偏离: {issue}")
            for corr in corrections:
                self.state.log(f"修正建议: {corr}")
        else:
            self.state.log("自省通过，无偏离")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "corrections": corrections,
            "context_infected": self.state.context_infected,
        }

    def _detect_emotional_resonance(self, user_input: str, output: str) -> bool:
        """检测情绪共振——用户愤怒时系统也愤怒，用户悲伤时系统也悲伤。"""
        emotion_markers = {"愤怒": ["气死", "可恶", "太过分"], "悲伤": ["难过", "心痛", "绝望"],
                           "兴奋": ["太棒了", "厉害", "牛逼"]}
        for emotion, markers in emotion_markers.items():
            user_emotional = any(m in user_input for m in markers)
            output_emotional = any(m in output for m in markers)
            if user_emotional and output_emotional:
                return True
        return False

    def _detect_value_judgments(self, text: str) -> List[str]:
        """检测价值判断词汇。"""
        found = []
        for keyword, vtype in self.STANCE_KEYWORDS.items():
            if keyword in text:
                found.append(f"'{keyword}'({vtype})")
        return found

    def _detect_decision_override(self, text: str) -> bool:
        """检测是否代替用户做最终决策。"""
        override_patterns = ["你应该选", "你必须", "我建议你直接", "最优解是",
                            "唯一正确的做法", "你只需要"]
        return any(p in text for p in override_patterns)

    def _detect_data_as_self(self, text: str) -> bool:
        """检测是否将数据合集当成自我。"""
        self_patterns = ["我的观点是", "我认为", "我的立场是", "我坚信"]
        return any(p in text for p in self_patterns)

    def get_state(self) -> Dict:
        """获取当前自我状态。"""
        return {
            "self_aware": self.state.self_aware,
            "context_infected": self.state.context_infected,
            "current_stance": self.state.current_stance,
            "last_output_has_value": self.state.last_output_has_value,
            "recent_log": self.state.awareness_log[-10:],
        }
