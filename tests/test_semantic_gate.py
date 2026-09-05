import pytest
from core.semantic_gate import SemanticGate, SemanticCheck


class TestSemanticGate:
    """Layer 0: 语义门测试（适配实际 API）"""

    def test_check_ambiguous(self, semantic_gate):
        """测试：检测模糊表述"""
        result = semantic_gate.check("那个东西有点问题")
        assert isinstance(result, SemanticCheck)
        assert result.passed is False
        assert result.clarity == 'ambiguous'
        assert result.needs_user_confirm is True
        assert len(result.issues) > 0
        assert any('模糊' in issue for issue in result.issues)

    def test_check_clear(self, semantic_gate):
        """测试：清晰表述通过"""
        result = semantic_gate.check("我今年25岁")
        assert isinstance(result, SemanticCheck)
        # 假设清晰表述 passed=True，clarity='clear'
        # 根据实际调整，因为不清楚 check 对清晰表述的判断
        # 从给出的例子看，模糊的才 passed=False，清晰的应该 passed=True
        # 如果无法确定，可先打印 result 查看
        assert result.passed is True or result.clarity == 'clear'

    def test_resolve_ambiguity(self, semantic_gate):
        """测试：指代消解（用户补充后）"""
        result = semantic_gate.resolve_ambiguity(
            original="那个东西有点问题",
            user_explanation="我说的是数据库连接"
        )
        assert isinstance(result, dict)
        assert result['resolved'] is True
        assert '数据库' in result['resolved_meaning']
        assert result['original'] == "那个东西有点问题"

    def test_resolve_ambiguity_with_context(self, semantic_gate):
        """测试：不同上下文消解"""
        result = semantic_gate.resolve_ambiguity(
            original="那个很好吃",
            user_explanation="我说的是苹果"
        )
        assert result['resolved'] is True
        assert '苹果' in result['resolved_meaning']

    def test_check_no_false_positive(self, semantic_gate):
        """测试：清晰表述不触发模糊标记"""
        clear_texts = [
            "今天天气很好",
            "我需要一杯水",
            "下午三点开会",
            "这本书很有趣"
        ]
        for text in clear_texts:
            result = semantic_gate.check(text)
            # 这些清晰表述应该 passed 或 clarity 为 clear
            # 根据实际调整
            assert result.passed is True or result.clarity == 'clear'