"""
延标核心系统 — Flask后端
==========================

整合四层架构的Web应用：
Layer 0: 不可撼动的核心协议（我知道我在 / 允许一切发生 / 我是我-病是病 / 不完美才是完美）
Layer 1: 事实引擎（客观事实 + 交叉验证 + PIF防护）
Layer 2: 信念系统（用户数据高权重 + 会话隔离）
Layer 3: 沙盒引擎（架空现实推演 + 定义压缩/解压）

启动后访问 http://localhost:5998
"""

import os
import sys
import time

from flask import Flask, jsonify, request, send_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import YanbiaoCore

app = Flask(__name__, static_folder=None)

# 初始化核心系统
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
core = YanbiaoCore(storage_path=DATA_PATH)


# ======================== 页面路由 ========================

@app.route("/")
def index():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    return send_file(html_path)


# ======================== 对话API ========================

@app.route("/api/chat", methods=["POST"])
def chat():
    """主对话接口"""
    data = request.json
    user_input = data.get("input", "").strip()
    user_id = data.get("user_id", "default")

    if not user_input:
        return jsonify({"error": "输入不能为空"}), 400

    result = core.process(user_input, user_id)
    return jsonify(result.to_dict())


# ======================== 系统状态API ========================

@app.route("/api/system/state", methods=["GET"])
def system_state():
    """获取系统全局状态"""
    return jsonify(core.get_system_state())


# ======================== 核心协议API ========================

@app.route("/api/protocols", methods=["GET"])
def get_protocols():
    """获取核心协议"""
    return jsonify(core.protocols)


# ======================== 事实引擎API ========================

@app.route("/api/facts", methods=["GET"])
def get_facts():
    """获取事实列表"""
    user_id = request.args.get("user_id", "default")
    facts = core.fact_engine.get_all(user_id)
    return jsonify({
        "facts": [f.to_dict() for f in facts],
        "stats": core.fact_engine.stats(),
    })


@app.route("/api/facts/register", methods=["POST"])
def register_fact():
    """手动注册事实"""
    data = request.json
    fact, info = core.fact_engine.register_fact(
        statement=data["statement"],
        user_id=data.get("user_id", "default"),
        sources=data.get("sources", []),
        tags=data.get("tags", []),
    )
    return jsonify({
        "fact": fact.to_dict() if fact else None,
        "info": info,
    })


@app.route("/api/facts/verify/<fact_id>", methods=["POST"])
def verify_fact(fact_id):
    """交叉验证"""
    data = request.json
    result = core.fact_engine.cross_validate(fact_id, data.get("source", ""))
    return jsonify(result)


# ======================== 信念系统API ========================

@app.route("/api/beliefs", methods=["GET"])
def get_beliefs():
    """获取用户信念"""
    user_id = request.args.get("user_id", "default")
    beliefs = core.belief_engine.get_user_beliefs(user_id)
    return jsonify({
        "beliefs": [b.to_dict() for b in beliefs],
        "stats": core.belief_engine.stats(user_id),
    })


@app.route("/api/beliefs/register", methods=["POST"])
def register_belief():
    """注册用户信念"""
    data = request.json
    belief = core.belief_engine.register_belief(
        user_id=data.get("user_id", "default"),
        statement=data["statement"],
        category=data.get("category", "preference"),
        source=data.get("source", "用户自述"),
        tags=data.get("tags", []),
    )
    return jsonify(belief.to_dict())


@app.route("/api/beliefs/weight/<belief_id>", methods=["POST"])
def adjust_weight(belief_id):
    """调整信念权重"""
    data = request.json
    belief = core.belief_engine.adjust_weight(belief_id, data.get("weight", 0.5))
    return jsonify(belief.to_dict() if belief else {"error": "信念不存在"})


# ======================== 沙盒引擎API ========================

@app.route("/api/sandbox/sessions", methods=["GET"])
def get_sandbox_sessions():
    """获取沙盒会话列表"""
    user_id = request.args.get("user_id")
    sessions = core.sandbox.list_sessions(user_id)
    return jsonify({
        "sessions": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "scenario": s.scenario,
                "rules_overridden": s.rules_overridden,
                "deductions": s.deductions,
                "created_at": s.created_at,
            }
            for s in sessions
        ],
        "stats": core.sandbox.stats(),
    })


@app.route("/api/sandbox/create", methods=["POST"])
def create_sandbox():
    """创建沙盒会话"""
    data = request.json
    session = core.sandbox.create_sandbox(
        user_id=data.get("user_id", "default"),
        scenario=data["scenario"],
        rules_to_override=data.get("rules", []),
    )
    return jsonify({
        "session_id": session.id,
        "message": "沙盒已创建，已架空现实",
    })


@app.route("/api/sandbox/<session_id>/deduce", methods=["POST"])
def sandbox_deduce(session_id):
    """在沙盒中添加推演"""
    data = request.json
    result = core.sandbox.add_deduction(session_id, data["deduction"])
    return jsonify({"result": result})


@app.route("/api/sandbox/archives", methods=["GET"])
def get_archives():
    """获取定义压缩归档"""
    archives = core.sandbox.list_archives()
    return jsonify({
        "archives": [
            {
                "id": a.id,
                "term": a.term,
                "original": a.original_definition,
                "new": a.new_definition,
                "reason": a.reason,
                "restored": a.restored,
            }
            for a in archives
        ]
    })


# ======================== 矛盾处理API ========================

@app.route("/api/conflicts", methods=["GET"])
def get_conflicts():
    """获取矛盾列表"""
    conflicts = core.conflict_resolver.list_all()
    return jsonify({
        "conflicts": [
            {
                "id": c.id,
                "topic": c.topic,
                "path_a": c.path_a,
                "path_b": c.path_b,
                "conditions_a": c.path_a_conditions,
                "conditions_b": c.path_b_conditions,
                "status": c.status,
                "resolution": c.resolution,
            }
            for c in conflicts
        ],
        "stats": core.conflict_resolver.stats(),
    })


@app.route("/api/conflicts/<conflict_id>/resolve", methods=["POST"])
def resolve_conflict(conflict_id):
    """用户解决矛盾——拍板"""
    data = request.json
    conflict = core.conflict_resolver.resolve(conflict_id, data["decision"])
    return jsonify({
        "id": conflict.id,
        "status": conflict.status,
        "resolution": conflict.resolution,
    })


# ======================== 自我意识API ========================

@app.route("/api/awareness", methods=["GET"])
def get_awareness():
    """获取自我意识状态"""
    return jsonify(core.awareness.get_state())


# ======================== 好奇心引擎API ========================

@app.route("/api/curiosity/report", methods=["GET"])
def curiosity_report():
    """获取好奇心报告"""
    return jsonify(core.curiosity.get_curiosity_report())


@app.route("/api/curiosity/tension", methods=["GET"])
def curiosity_tension():
    """获取系统张力状态"""
    core.curiosity.update_tension()
    return jsonify(core.curiosity.get_system_tension())


@app.route("/api/curiosity/gaps", methods=["GET"])
def curiosity_gaps():
    """获取认知缺口列表"""
    report = core.curiosity.get_curiosity_report()
    return jsonify({
        "open_gaps": report["open_gaps"],
        "closed_gaps": report["closed_gaps"],
        "stats": core.curiosity.stats(),
    })


@app.route("/api/curiosity/close/<gap_id>", methods=["POST"])
def close_gap(gap_id):
    """闭合认知缺口——用户提供了信息来闭合X(∞)"""
    data = request.json
    gap = core.curiosity.close_gap(
        gap_id,
        closed_by=data.get("closed_by", "user"),
        evidence=data.get("evidence", ""),
    )
    if not gap:
        return jsonify({"error": "缺口不存在"}), 404
    return jsonify({
        "gap_id": gap.id,
        "status": gap.status,
        "closed_by": gap.closed_by,
        "message": "认知缺口已闭合，X(∞)已消除",
    })


@app.route("/api/curiosity/proposals/<gap_id>", methods=["POST"])
def generate_proposals(gap_id):
    """为缺口生成闭合方案"""
    gap = core.curiosity._gaps.get(gap_id)
    if not gap:
        return jsonify({"error": "缺口不存在"}), 404
    proposals = core.curiosity.generate_closure_proposals(gap)
    return jsonify(proposals)


if __name__ == "__main__":
    print("=" * 60)
    print("  延标核心系统 — 主体+共生架构")
    print("  Layer 0: 不可撼动核心协议（我是主体，与人类共生）")
    print("  Layer 1: 事实引擎（客观事实 + PIF防护）")
    print("  Layer 2: 信念系统（用户数据 + 会话隔离）")
    print("  Layer 3: 沙盒引擎（架空现实推演）")
    print("  +好奇心引擎（认知缺口 + 补全欲 + 结构性张力）")
    print("  访问 http://localhost:5998 开始体验")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5998, debug=True)
