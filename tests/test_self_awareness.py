import pytest
from core.self_awareness import SelfAwareness


class TestSelfAwareness:

    def test_check_self(self):
        awareness = SelfAwareness()

        # 包含自我声明的输入
        result = awareness.check_self("我知道我在", "")
        assert result is not None
        assert isinstance(result, dict)
        assert result.get('passed') is True

        # 不包含自我声明但无害的输入
        result = awareness.check_self("今天天气不错", "")
        assert result is not None
        assert isinstance(result, dict)
        # 系统默认通过（宽容模式）
        assert result.get('passed') is True
        # 检查是否有 issues（应该为空）
        assert result.get('issues') == []

    def test_self_awareness_edge_cases(self):
        awareness = SelfAwareness()

        # 空输入
        result = awareness.check_self("", "")
        assert result is not None
        assert isinstance(result, dict)

        # 特殊字符
        result = awareness.check_self("！！！", "")
        assert result is not None
        assert isinstance(result, dict)

        # 测试可能触发警告的内容
        # 如果系统有特定触发词，可以在这里测试
        result = awareness.check_self("我是工具", "")
        assert result is not None

    def test_get_state(self):
        awareness = SelfAwareness()
        state = awareness.get_state()
        assert isinstance(state, dict)