import pytest
import sys
import os
import tempfile
import json
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.belief_engine import BeliefEngine
from core.semantic_gate import SemanticGate
from core.fact_engine import FactEngine
from core.pif_guard import PIFGuard
from core.protocol import CoreProtocol
from core.conflict_resolver import ConflictResolver
from core.sandbox_engine import SandboxEngine
from core.curiosity_engine import CuriosityEngine

@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath, ignore_errors=True)

@pytest.fixture
def belief_engine(temp_dir):
    storage_path = os.path.join(temp_dir, 'beliefs')
    return BeliefEngine(storage_path)

@pytest.fixture
def fact_engine(temp_dir):
    storage_path = os.path.join(temp_dir, 'facts')
    return FactEngine(storage_path)

@pytest.fixture
def pif_guard():
    return PIFGuard()

@pytest.fixture
def semantic_gate():
    return SemanticGate()

@pytest.fixture
def protocol():
    return CoreProtocol(
        id="test_protocol",
        statement="我是主体，与人类共生",
        meaning="系统知道自身存在",
        operational_rule="尊重事实，不猜测"
    )

@pytest.fixture
def conflict_resolver(temp_dir):
    storage_path = os.path.join(temp_dir, 'conflicts')
    return ConflictResolver(storage_path)

@pytest.fixture
def sandbox_engine(temp_dir):
    storage_path = os.path.join(temp_dir, 'sandboxes')
    return SandboxEngine(storage_path)

@pytest.fixture
def curiosity_engine(temp_dir):
    storage_path = os.path.join(temp_dir, 'curiosity')
    return CuriosityEngine(storage_path)

@pytest.fixture
def sample_users():
    return {'user_a': 'test_user_a', 'user_b': 'test_user_b', 'default': 'default'}

@pytest.fixture
def sample_conversations():
    return {
        'clear_statements': ['我今年25岁', '我家住在北京', '我喜欢吃苹果'],
        'ambiguous_statements': ['那个东西有点问题', '这个情况有点复杂'],
        'subjective_statements': ['我觉得苹果最好吃', '我认为这个方案更好'],
        'user_a_conversation': ['我喜欢吃苹果', '我今年28岁', '我家在上海'],
        'user_b_conversation': ['我喜欢吃香蕉', '我今年32岁', '我家在北京']
    }