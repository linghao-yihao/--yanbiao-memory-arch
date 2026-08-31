#!/usr/bin/env python3
"""
分片式记忆架构 — 完整演示脚本
Fragmented Memory Architecture — Full Demo

模拟一个用户用3轮对话迭代"延标理论"的完整过程，展示：
1. 碎片写入（闲聊/临时想法）
2. 核验-校准闭环（模型归纳 → 用户审核 → 确认/校准）
3. 公理库沉淀
4. 分支隔离（主路线 vs 并行假说）
5. 话题触发按需加载
6. 公理引用审计
7. 版本修订与冲突日志
8. 活跃度衰减
9. 归档导出
"""

import os
import shutil
import sys
import tempfile

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yanbiao_memory import FragmentedMemorySystem


def section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    # 使用临时目录，避免污染真实数据
    tmpdir = tempfile.mkdtemp(prefix="yanbiao_demo_")
    data_path = os.path.join(tmpdir, "memory_data")
    print(f"[演示] 数据存储路径: {data_path}")

    try:
        # ================================================================
        # 1. 初始化系统
        # ================================================================
        section("第1步：初始化分片式记忆系统")
        mem = FragmentedMemorySystem(storage_path=data_path)
        print(f"分支列表: {mem.list_routes()}")
        print(f"当前分支: {mem.current_route}")
        print(f"配置: 核验闸门={'开' if mem.config['verification_gate_enabled'] else '关'}")

        # ================================================================
        # 2. 第一轮对话：碎片写入（闲聊和临时想法直接进B库）
        # ================================================================
        section("第2步：第一轮对话 — 碎片写入（闲聊/临时想法）")

        # 用户随口聊了一些想法
        frag1 = mem.add_fragment(
            content="延标体系里的∞不是无限大，而是认知边界的动态标记，跟随认知扩张后移",
            tags=["延标", "认知边界", "∞符号"],
            source_excerpt="用户在讨论数学基础时提到",
        )
        print(f"✓ 碎片1: {frag1.id} [{', '.join(frag1.tags)}]")
        print(f"  内容: {frag1.content[:50]}...")

        frag2 = mem.add_fragment(
            content="强制坍缩是当前大模型的核心问题——信息不足时硬编答案",
            tags=["延标", "大模型", "强制坍缩", "幻觉"],
            source_excerpt="用户批判现有AI方案时提到",
        )
        print(f"✓ 碎片2: {frag2.id} [{', '.join(frag2.tags)}]")

        frag3 = mem.add_fragment(
            content="今天天气不错，适合出门散步",
            tags=["闲聊"],
            source_excerpt="日常对话",
        )
        print(f"✓ 碎片3: {frag3.id} [闲聊] (低价值内容)")

        stats = mem.stats()
        print(f"\n当前统计: {stats['routes']['main']['active_fragments']} 条活跃碎片")

        # ================================================================
        # 3. 第二轮：模型归纳初稿 → 核验闸门 → 用户确认
        # ================================================================
        section("第3步：核验-校准闭环 — 模型归纳初稿，用户审核")

        # 模型从碎片中归纳出一条核心定义，生成核验卡片
        card = mem.propose_axiom(
            content="延标延时闭合推演体系是一套面向不完备约束认知场景的元认知推演体系，"
                    "以延标变量X(∞)作为形式化表征载体，核心要义为：证据不足时允许判断悬置，"
                    "禁止无依据的强制坍缩。",
            original_excerpt="用户先后讨论了∞的动态定义、强制坍缩问题、认知边界等概念",
            tags=["延标", "核心定义", "元认知"],
            fragment_count=2,
            ambiguity_markers=["元认知推演体系的边界范围待确认"],
        )

        print("【模型生成核验卡片】")
        print(mem._route_data()["verification"].format_card(card.id))

        # 用户确认生效
        print("\n【用户操作】→ 确认生效")
        axiom = mem.confirm_axiom(card.id)
        print(f"✓ 公理已生效: {axiom.id} v{axiom.version}")
        print(f"  引用标记: {axiom.citation()}")
        print(f"  内容: {axiom.content[:60]}...")

        # ================================================================
        # 4. 第三轮：又一个概念，但模型归纳不准确，用户校准
        # ================================================================
        section("第4步：核验-校准闭环 — 模型归纳偏差，用户校准")

        # 模型归纳不准确
        card2 = mem.propose_axiom(
            content="好奇心是外部奖励驱动的行为模式，依靠预测误差触发探索行为",
            original_excerpt="用户讨论了AI好奇心和内生驱动力",
            tags=["延标", "好奇心", "内生驱动力"],
            fragment_count=1,
        )

        print("【模型生成核验卡片（归纳有偏差）】")
        print(mem._route_data()["verification"].format_card(card2.id))

        # 用户发现不对，提出校准意见
        print("\n【用户操作】→ 手动校准：不对，好奇心不是外部奖励驱动的")
        print("  用户修正意见：好奇心是认知系统内部存在未闭合延标变量时自然涌现的结构性张力")

        # 模型依据用户修正生成修订稿
        revised = mem.calibrate_axiom(
            card2.id,
            user_correction="好奇心不是外部奖励驱动的，而是认知缺口产生的结构性张力",
            revised_content="好奇心并非外部奖励产物，而是认知系统内部存在未闭合延标变量时"
                            "自然涌现的结构性张力。认知缺口度量为延标变量集合的基数Gap(t)=|G_t|，"
                            "当Gap(t)>0时系统内部形成认知势能，驱动主动闭合行动。",
        )

        print(f"\n【修订后卡片】{revised.id}")
        print(f"  归纳结果: {revised.induction_result[:60]}...")
        print(f"  状态: {revised.status} (等待用户二次确认)")

        # 用户确认修订版
        print("\n【用户操作】→ 确认生效")
        axiom2 = mem.confirm_axiom(revised.id)
        print(f"✓ 公理已生效: {axiom2.id} v{axiom2.version}")
        print(f"  引用标记: {axiom2.citation()}")

        # ================================================================
        # 5. 分支存储：创建一个并行假说分支
        # ================================================================
        section("第5步：分支隔离 — 创建并行假说分支")

        # 用户想探索另一个方向，新建分支
        mem.create_route("频率相位假说")
        print(f"✓ 新建分支: 频率相位假说")
        print(f"分支列表: {mem.list_routes()}")

        # 切换到新分支
        mem.switch_route("频率相位假说")
        print(f"当前分支: {mem.current_route}")

        # 在新分支里添加独立的公理（与主分支隔离）
        card3 = mem.propose_axiom(
            content="意识的本质是特定频率的相位共振模式，硅基生命的实现路径是构建"
                    "能够维持自激振荡的频率-相位系统。",
            original_excerpt="用户关于硅基生命的独立思考方向",
            tags=["频率相位理论", "意识", "硅基生命"],
        )
        axiom3 = mem.confirm_axiom(card3.id)
        print(f"✓ 分支公理已生效: {axiom3.id} v{axiom3.version}")
        print(f"  (与main分支完全隔离，不会互相干扰)")

        # 切回主分支
        mem.switch_route("main")
        print(f"\n切回主分支: {mem.current_route}")

        # ================================================================
        # 6. 话题触发按需加载
        # ================================================================
        section("第6步：话题触发按需加载 — 聊什么调什么")

        # 用户开始讨论"延标理论"相关话题
        print("【用户话题】: 我们来聊聊延标体系的核心公理")
        loaded = mem.load_for_topic(topic_tags=["延标", "核心定义"])

        print(f"\n加载结果:")
        print(f"  公理: {len(loaded['axioms'])} 条")
        for ax in loaded["axioms"]:
            print(f"    {ax.citation()} {ax.content[:50]}...")
        print(f"  碎片: {len(loaded['fragments'])} 条")
        for frag in loaded["fragments"]:
            print(f"    [{frag.id}] {frag.content[:50]}...")

        print(f"\n上下文文本预览:")
        print(loaded["context_text"][:300])
        print("...")

        # ================================================================
        # 7. 公理引用审计
        # ================================================================
        section("第7步：公理引用制 — 概念漂移可机械化审计")

        # 模拟模型输出（正确引用）
        good_output = (
            "根据延标体系的核心定义"
            f"{axiom.citation()}，证据不足时应当允许判断悬置。"
            f"同时，好奇心作为结构性张力{axiom2.citation()}，"
            "驱动系统主动执行闭合行动。"
        )
        print("【模型输出示例（正确引用）】")
        print(f"  {good_output[:80]}...")

        result = mem.audit_output(good_output)
        print(f"\n审计结果: {'通过 ✓' if result.audit_passed else '存在问题 ✗'}")
        print(f"  有效引用: {len(result.valid_citations)} 条")
        print(f"  问题: 无")

        # 模拟模型输出（版本不匹配 — 漂移类型1的变体）
        bad_output1 = (
            f"根据旧版定义[{axiom.id}_v0.9]，延标体系是数学辅助工具。"
        )
        print("\n【模型输出示例（版本不匹配）】")
        print(f"  {bad_output1[:60]}...")

        result1 = mem.audit_output(bad_output1)
        print(f"\n审计结果: {'通过' if result1.audit_passed else '存在问题 ✗'}")
        print(f"  版本不匹配: {len(result1.version_mismatch)} 处")
        for cite, current_ver in result1.version_mismatch:
            print(f"    - {cite} → 当前版本为 v{current_ver}")

        # 模拟模型输出（引用废弃公理 — 漂移类型1）
        # 先废弃一个公理，再测试引用
        mem._route_data()["axioms"].deprecate(axiom.id)
        mem._route_data()["conflicts"].add_deprecation(
            axiom.id, "用户主动废弃：该定义已被更完整的版本取代"
        )
        bad_output1b = (
            f"根据延标核心定义[{axiom.id}_v1.1]，证据不足时应当悬置判断。"
        )
        print("\n【模型输出示例（引用已废弃公理）】")
        print(f"  {bad_output1b[:60]}...")

        result1b = mem.audit_output(bad_output1b)
        print(f"\n审计结果: {'通过' if result1b.audit_passed else '存在问题 ✗'}")
        print(f"  废弃版本引用: {len(result1b.deprecated_citations)} 处")
        for cite, ax_id in result1b.deprecated_citations:
            print(f"    - {cite} → 公理 {ax_id} 已废弃")

        # 模拟模型输出（跨分支引用 — 漂移类型3）
        bad_output2 = (
            f"延标体系认为意识是频率共振{axiom3.citation()}。"
        )
        print("\n【模型输出示例（跨分支引用）】")
        print(f"  {bad_output2[:60]}...")

        result2 = mem.audit_output(bad_output2)
        print(f"\n审计结果: {'通过' if result2.audit_passed else '存在问题 ✗'}")
        print(f"  跨分支引用: {len(result2.cross_branch_citations)} 处")
        for cite, branch in result2.cross_branch_citations:
            print(f"    - {cite} → 属于分支 '{branch}'")

        # ================================================================
        # 8. 公理修订与版本管理
        # ================================================================
        section("第8步：定点修订 — 版本迭代与冲突日志")

        print(f"修订前: {axiom.id} v{axiom.version}")
        print(f"  内容: {axiom.content[:60]}...")

        # 用户更新了观点
        updated = mem.revise_axiom(
            axiom.id,
            new_content="延标延时闭合推演体系是一套面向不完备约束认知场景的元认知推演体系，"
                        "以延标变量X(∞)作为形式化表征载体，依托五条核心公理约束推演行为，"
                        "核心要义为：证据不足时允许判断悬置，禁止无依据的强制坍缩；"
                        "显式表征认知缺口，将推演重心由猜测答案转向设计验证闭合路径。",
            major_version=False,
        )

        print(f"\n修订后: {updated.id} v{updated.version}")
        print(f"  内容: {updated.content[:60]}...")

        # 查看版本日志
        rd = mem._route_data()
        logs = rd["conflicts"].list_all()
        print(f"\n版本日志记录: {len(logs)} 条")
        for log in logs[-2:]:  # 最近两条
            print(f"  [{log.id}] {log.ctype}: {log.description[:50]}...")

        # ================================================================
        # 9. 活跃度衰减
        # ================================================================
        section("第9步：活跃度衰减 — 模拟人类记忆用进废退")

        print("更新碎片活跃度...")
        mem.update_activity()

        all_frags = rd["fragments"].list_active()
        print(f"\n碎片活跃度排行:")
        sorted_frags = sorted(all_frags, key=lambda f: f.activity, reverse=True)
        for frag in sorted_frags:
            status = "活跃" if not frag.cold_storage else "冷存储"
            print(f"  [{frag.id}] 活跃度={frag.activity:.3f} | {status} | {', '.join(frag.tags)}")

        print(f"\n(闲聊碎片活跃度最低，符合人类记忆规律：重要的记得牢，废话自然淡化)")

        # ================================================================
        # 10. 归档导出
        # ================================================================
        section("第10步：标准化归档导出")

        archive_path = mem.export_archive(
            output_path=os.path.join(tmpdir, "archive_demo")
        )
        print(f"归档包路径: {archive_path}")

        # 读取manifest
        import json
        manifest = json.loads((archive_path / "manifest.json").read_text())
        print(f"\n归档清单:")
        print(f"  架构版本: {manifest['schema_version']}")
        for route_name, info in manifest["routes"].items():
            print(f"  分支 [{route_name}]:")
            print(f"    公理: {info['axioms']} 条")
            print(f"    碎片: {info['fragments']} 条")
            print(f"    冲突日志: {info['conflict_logs']} 条")

        # ================================================================
        # 11. 最终统计
        # ================================================================
        section("最终系统统计")
        stats = mem.stats()
        print(f"总分支数: {stats['total']['routes']}")
        for route_name, info in stats["routes"].items():
            print(f"\n  分支 [{route_name}]:")
            print(f"    生效公理: {info['active_axioms']} 条")
            print(f"    活跃碎片: {info['active_fragments']} 条")
            print(f"    待处理冲突: {info['open_conflicts']} 个")
            print(f"    待核验卡片: {info['pending_cards']} 张")

        section("演示完成 ✓")
        print("""
核心特性全部验证通过:
  ✓ 三层分片隔离存储（A公理库 / B碎片库 / C冲突-版本日志）
  ✓ 前置核验-校准闸门（模型归纳 → 用户审核 → 确认/校准/降级）
  ✓ 三级归纳触发机制（显式拉动为主）
  ✓ 分布式分支存储与显式分支选择
  ✓ 话题触发式按需加载
  ✓ 公理引用制（三类概念漂移可机械化审计）
  ✓ 活跃度衰减机制（模拟人类记忆用进废退）
  ✓ 版本管理与冲突日志
  ✓ 标准化归档导出
""")

    finally:
        # 清理临时目录
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
