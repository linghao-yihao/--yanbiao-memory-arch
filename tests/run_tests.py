#!/usr/bin/env python
"""
延标核心系统测试运行器

使用方法:
    python tests/run_tests.py          # 运行所有测试
    python tests/run_tests.py -v       # 详细输出
    python tests/run_tests.py -k test_user_isolation  # 运行特定测试

运行前确保:
    1. pytest 已安装: pip install pytest pytest-cov
    2. 项目根目录在 PYTHONPATH 中
"""

import sys
import os
import argparse
import time

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_tests(verbose=False, keyword=None, coverage=False):
    """运行测试"""
    import pytest

    # 构建 pytest 参数
    args = ['-xvs'] if verbose else ['-v']
    args.append('--tb=short')  # 简短回溯

    if keyword:
        args.extend(['-k', keyword])

    if coverage:
        args.extend([
            '--cov=core',
            '--cov-report=term',
            '--cov-report=html:htmlcov'
        ])

    # 指定测试目录
    test_dir = os.path.join(os.path.dirname(__file__))
    args.append(test_dir)

    print("\n" + "=" * 60)
    print("  延标核心系统 — 测试套件")
    print("  测试目录: {}".format(test_dir))
    print("=" * 60 + "\n")

    start_time = time.time()

    # 运行 pytest
    exit_code = pytest.main(args)

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("  测试完成")
    print("  耗时: {:.2f} 秒".format(elapsed))
    if coverage:
        print("  覆盖率报告: htmlcov/index.html")
    print("  退出码: {}".format(exit_code))
    print("=" * 60 + "\n")

    return exit_code


def main():
    parser = argparse.ArgumentParser(description='运行延标核心系统测试')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('-k', '--keyword', type=str, help='只运行匹配关键词的测试')
    parser.add_argument('--cov', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--list', action='store_true', help='列出所有测试')

    args = parser.parse_args()

    if args.list:
        # 列出所有测试
        import pytest
        test_dir = os.path.join(os.path.dirname(__file__))
        pytest.main(['--collect-only', test_dir])
        return 0

    return run_tests(
        verbose=args.verbose,
        keyword=args.keyword,
        coverage=args.cov
    )


if __name__ == '__main__':
    sys.exit(main())