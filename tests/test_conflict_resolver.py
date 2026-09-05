import os
import pytest
from core.conflict_resolver import ConflictResolver


class TestConflictResolver:

    @pytest.fixture
    def conflict_resolver(self, temp_dir):
        storage_path = os.path.join(temp_dir, 'conflicts')
        return ConflictResolver(storage_path)

    def test_conflict_resolver_creation(self, conflict_resolver):
        assert conflict_resolver is not None

    def test_resolve_conflict(self, conflict_resolver):
        # 注册一个矛盾
        conflict = conflict_resolver.register_conflict(
            topic="是否要带伞",
            path_a="带伞，因为天气预报说会下雨",
            path_b="不带伞，因为目前是晴天",
            conditions_a=["天气预报准确率 > 80%"],
            conditions_b=["当前无雨"]
        )
        assert conflict is not None
        assert conflict.status == "open"

        # 解决矛盾
        resolved = conflict_resolver.resolve(conflict.id, "选择带伞")
        assert resolved is not None
        assert resolved.status == "resolved"
        assert resolved.resolution == "选择带伞"

    def test_conflict_history(self, conflict_resolver):
        """测试：矛盾历史"""
        # 先产生一个矛盾
        conflict = conflict_resolver.register_conflict(
            topic="测试主题",
            path_a="路径A",
            path_b="路径B"
        )
        # 调用 get_history
        history = conflict_resolver.get_history(limit=10)
        assert history is not None
        assert isinstance(history, list)
        assert len(history) >= 1
        # 验证返回的记录包含基本信息
        first = history[0]
        assert "id" in first
        assert "topic" in first
        assert "status" in first

    def test_conflict_resolve_not_found(self, conflict_resolver):
        """测试：解决不存在的冲突"""
        result = conflict_resolver.resolve("NOT_EXIST", "用户决策")
        assert result is None  # 或返回错误信息

    def test_conflict_formatting(self, conflict_resolver):
        """测试：冲突格式化输出"""
        conflict = conflict_resolver.register_conflict(
            topic="测试主题",
            path_a="路径A",
            path_b="路径B",
            conditions_a=["条件1", "条件2"],
            conditions_b=["条件3"]
        )
        formatted = conflict_resolver.format_paths(conflict)
        assert "路径A" in formatted
        assert "路径B" in formatted
        assert "条件1" in formatted
        assert "条件2" in formatted
        assert "条件3" in formatted
        assert "不做价值评判" in formatted

    def test_conflict_stats(self, conflict_resolver):
        """测试：矛盾统计"""
        conflict_resolver.register_conflict("主题1", "A", "B")
        stats = conflict_resolver.stats()
        assert stats['total'] == 1
        assert stats['open'] == 1
        assert stats['resolved'] == 0