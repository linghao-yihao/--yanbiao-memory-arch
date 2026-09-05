import pytest
from core.curiosity_engine import CuriosityEngine


class TestCuriosityEngine:

    def test_open_gap(self, curiosity_engine):
        result = curiosity_engine.open_gap(
            topic='量子计算',
            description='缺乏相关知识',
            variable=''
        )
        assert result is not None

    def test_get_open_gaps(self, curiosity_engine):
        curiosity_engine.open_gap(topic='量子计算', description='缺乏知识', variable='')
        gaps = curiosity_engine.get_open_gaps()
        assert gaps is not None

    def test_generate_closure_proposals(self, curiosity_engine):
        # 先打开一个缺口，获取 gap 对象
        gap = curiosity_engine.open_gap(
            topic='量子计算',
            description='缺乏相关知识',
            variable=''
        )
        # 调用 generate_closure_proposals 需要传入 gap 参数
        proposals = curiosity_engine.generate_closure_proposals(gap=gap)
        assert proposals is not None

    def test_close_gap(self, curiosity_engine):
        gap = curiosity_engine.open_gap(
            topic='量子计算',
            description='缺乏相关知识',
            variable=''
        )
        # 获取 gap 的 ID
        gap_id = getattr(gap, 'id', None)
        if gap_id is None and isinstance(gap, dict):
            gap_id = gap.get('id')
        if gap_id is None:
            pytest.skip("无法获取 gap ID")
        # 调用 close_gap 传入 gap_id, closed_by, evidence
        result = curiosity_engine.close_gap(gap_id, 'system', '已学习相关知识')
        assert result is not None or result is True

    def test_get_system_tension(self, curiosity_engine):
        tension = curiosity_engine.get_system_tension()
        assert isinstance(tension, dict)
        assert 'tension_level' in tension or 'total_gap' in tension

    def test_update_tension(self, curiosity_engine):
        result = curiosity_engine.update_tension()
        assert result is not None

    def test_stats(self, curiosity_engine):
        stats = curiosity_engine.stats()
        assert isinstance(stats, dict)