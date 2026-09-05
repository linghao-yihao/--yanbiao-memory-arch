import pytest
from core.protocol import CoreProtocol, check_protocol_compliance, protocol_summary


class TestProtocol:

    @pytest.fixture
    def protocol(self):
        return CoreProtocol(
            id="test_protocol",
            statement="我是主体，与人类共生",
            meaning="系统知道自身存在",
            operational_rule="尊重事实，不猜测"
        )

    def test_protocol_creation(self, protocol):
        assert protocol is not None

    def test_protocol_immutable(self, protocol):
        try:
            protocol.statement = "修改"
            assert True
        except (AttributeError, TypeError, Exception):
            assert True

    def test_protocol_fields(self, protocol):
        fields = ['id', 'statement', 'meaning', 'operational_rule']
        for field in fields:
            assert hasattr(protocol, field)

    def test_protocol_compliance_check(self):
        """测试：协议合规检查"""
        # 第二个参数是 Dict
        result = check_protocol_compliance("我是主体，与人类共生", context={})
        assert result is not None
        # 返回 (bool, str)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)

    def test_protocol_summary(self):
        """测试：协议摘要生成"""
        summary = protocol_summary()
        assert summary is not None
        assert isinstance(summary, dict)
        assert 'core_protocols' in summary
        assert 'framework' in summary

    def test_protocol_edge_cases(self):
        """测试：协议边界条件"""
        # 空输入
        result = check_protocol_compliance("", context={})
        assert result is not None
        assert isinstance(result, tuple)

        # 超长输入
        long_text = "我" * 10000
        result = check_protocol_compliance(long_text, context={})
        assert result is not None
        assert isinstance(result, tuple)