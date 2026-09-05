import os
import pytest
from orchestrator import YanbiaoCore


class TestIntegration:

    @pytest.fixture
    def orchestrator(self, temp_dir):
        storage_path = os.path.join(temp_dir, 'orchestrator')
        return YanbiaoCore(storage_path=storage_path)

    def test_orchestrator_creation(self, orchestrator):
        assert orchestrator is not None

    def test_process_message(self, orchestrator):
        if hasattr(orchestrator, 'process'):
            try:
                response = orchestrator.process(user_id='test_user', text='我今年25岁')
            except TypeError:
                try:
                    response = orchestrator.process(user_id='test_user', query='我今年25岁')
                except TypeError:
                    response = orchestrator.process('test_user', '我今年25岁')
            assert response is not None
        else:
            pytest.skip("YanbiaoCore 没有 process 方法")

    def test_multi_user_flow(self, orchestrator):
        if hasattr(orchestrator, 'process'):
            try:
                r1 = orchestrator.process(user_id='user_a', text='我喜欢吃苹果')
                r2 = orchestrator.process(user_id='user_b', text='我喜欢吃香蕉')
            except TypeError:
                try:
                    r1 = orchestrator.process(user_id='user_a', query='我喜欢吃苹果')
                    r2 = orchestrator.process(user_id='user_b', query='我喜欢吃香蕉')
                except TypeError:
                    r1 = orchestrator.process('user_a', '我喜欢吃苹果')
                    r2 = orchestrator.process('user_b', '我喜欢吃香蕉')
            assert r1 is not None
            assert r2 is not None
        else:
            pytest.skip("YanbiaoCore 没有 process 方法")

    def test_sandbox_mode(self, orchestrator):
        """测试沙盒模式：通过输入内容触发自动路由"""
        # 使用包含"假设"、"如果"等创造性表达来触发沙盒
        # 或者使用常理违反的内容
        response = orchestrator.process(
            user_input='假设明天会下雨，世界会怎样？',
            user_id='test_user'
        )
        # 检查结果是否进入了沙盒模式
        assert response is not None
        # 如果是 ProcessingResult 对象，检查 in_sandbox 属性
        if hasattr(response, 'in_sandbox'):
            assert response.in_sandbox is True
        elif isinstance(response, dict):
            assert response.get('in_sandbox') is True
        else:
            # 如果返回的是字符串，检查是否包含沙盒免责声明
            assert '沙盒推演' in str(response) or '架空现实' in str(response)