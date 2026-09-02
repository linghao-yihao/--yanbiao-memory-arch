import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any


# ====================== 延标延时闭合推演模块 ======================
@dataclass
class MarkedVariable:
    """延标变量 X(∞)"""
    var_name: str
    desc: str                          # 变量语义描述
    is_closed: bool = False            # 是否完成闭合
    closed_value: Optional[Any] = None # 闭合后的真值
    origin_type: str = "epistemic"     # epistemic客观暂不可测 / ontological尚未演化
    closure_plan: List[str] = None     # 闭合实施方案清单
    related_axiom_aids: List[str] = None # 关联的公理ID

    def __post_init__(self):
        if self.closure_plan is None:
            self.closure_plan = []
        if self.related_axiom_aids is None:
            self.related_axiom_aids = []

    def close(self, true_value: Any):
        """事实驱动闭合：只有外部事实可以回填真值，禁止内部随意赋值"""
        self.is_closed = True
        self.closed_value = true_value
        print(f"[延标闭合] {self.var_name} 完成闭合，真值={true_value}")

    def get_label(self) -> str:
        if self.is_closed:
            return f"{self.var_name}={self.closed_value}"
        return f"{self.var_name}(∞)"


@dataclass
class DeductionContext:
    """推演上下文：保存已知条件 + 延标变量集合，执行不坍缩校验"""
    known_conditions: Dict[str, Any]
    marked_vars: Dict[str, MarkedVariable]

    def forbid_collapse_check(self, target_var_name: str, assigned_val: Any) -> Optional[str]:
        """
        延时不坍缩公理校验：
        如果变量未闭合，却被直接赋值，返回违规说明；无违规返回None
        """
        mv = self.marked_vars.get(target_var_name)
        if mv is None:
            return None
        if not mv.is_closed:
            return f"推演违规：延标变量 {mv.get_label()} 尚未闭合，禁止强制赋值为 {assigned_val}"
        return None

    def list_gaps(self) -> List[MarkedVariable]:
        """列出全部认知缺口：未闭合延标变量"""
        return [v for v in self.marked_vars.values() if not v.is_closed]


# ====================== 分片记忆原有数据结构（少量改造兼容延标） ======================
@dataclass
class Axiom:
    """基准公理库A：支持普通公理 OR 携带延标推演约束的公理"""
    aid: str
    route: str
    content: str
    deduction_context_json: Optional[str]  # 可序列化DeductionContext，存放延标推演上下文
    version: str
    status: str
    tags: List[str]
    created_at: float
    updated_at: float
    related_fragments: List[str]


@dataclass
class Fragment:
    """交互碎片库B"""
    fid: str
    content: str
    tags: List[str]
    call_cnt: int
    link_axiom_cnt: int
    create_time: float
    active_score: float = 0.0


@dataclass
class ConflictLog:
    """冲突与版本日志C：扩展支持推演违规记录"""
    cid: str
    ctype: str  # logic_conflict / deduction_violation
    involved_axioms: List[str]
    description: str
    severity: str
    status: str
    resolution: Optional[str]


# ====================== 融合后的分片记忆主类 ======================
class ShardedMemoryWithMarked:
    def __init__(self):
        self.axiom_store: Dict[str, Axiom] = {}
        self.fragment_store: Dict[str, Fragment] = {}
        self.conflict_store: Dict[str, ConflictLog] = {}
        self.global_marked_vars: Dict[str, MarkedVariable] = {}  # 全局延标变量池

    @staticmethod
    def _gen_axiom_id(route: str) -> str:
        hex_suffix = uuid.uuid4().hex[:8].upper()
        return f"AX‑{route}‑{hex_suffix}"

    @staticmethod
    def _gen_fid() -> str:
        return f"F‑{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def _gen_cid() -> str:
        return f"C‑{uuid.uuid4().hex[:8].upper()}"

    def calc_fragment_active(self, frag: Fragment) -> float:
        now = time.time()
        delta_day = max((now - frag.create_time) / (86400), 0.01)
        time_decay = 1.0 / (1.0 + delta_day * 0.15)
        call_w = min(frag.call_cnt / max(frag.call_cnt + 5, 1), 1.0)
        link_w = min(frag.link_axiom_cnt / max(frag.link_axiom_cnt + 3, 1), 1.0)
        score = call_w * 0.4 + link_w * 0.4 + time_decay * 0.2
        return round(score, 4)

    def add_fragment(self, content: str, tags: List[str]) -> str:
        fid = self._gen_fid()
        f = Fragment(
            fid=fid,
            content=content,
            tags=tags,
            call_cnt=0,
            link_axiom_cnt=0,
            create_time=time.time()
        )
        f.active_score = self.calc_fragment_active(f)
        self.fragment_store[fid] = f
        return fid

    def mock_model_induce(self, raw_text: str) -> str:
        return f"[模型归纳候选] {raw_text}"

    def review_candidate_axiom(self, raw_source_fids: List[str], candidate_text: str,
                               route: str, user_choice: str,
                               deduction_ctx: Optional[DeductionContext] = None):
        """
        核验闸门扩展：可以传入携带延标推演上下文deduction_ctx
        """
        if user_choice == "fragment_only":
            print(" >> 用户选择：仅保留为碎片，不升级公理")
            return None
        elif user_choice == "confirm":
            aid = self._gen_axiom_id(route)
            ctx_json = json.dumps(asdict(deduction_ctx), ensure_ascii=False) if deduction_ctx else None
            axiom = Axiom(
                aid=aid,
                route=route,
                content=candidate_text,
                deduction_context_json=ctx_json,
                version="1.0",
                status="active",
                tags=[route],
                created_at=time.time(),
                updated_at=time.time(),
                related_fragments=raw_source_fids
            )
            self.axiom_store[aid] = axiom
            # 将公理ID绑定到上下文内所有延标变量
            if deduction_ctx:
                for mv in deduction_ctx.marked_vars.values():
                    mv.related_axiom_aids.append(aid)
                    self.global_marked_vars[mv.var_name] = mv
            for fid in raw_source_fids:
                if fid in self.fragment_store:
                    fr = self.fragment_store[fid]
                    fr.link_axiom_cnt += 1
            print(f" >> 公理已生效 id={aid}")
            return aid
        elif user_choice == "edit":
            print(" >> 用户编辑修订候选文本，外部修改文本后重新送入审核流程")
            return None
        else:
            raise ValueError("user_choice只能 confirm / edit / fragment_only")

    def mark_conflict(self, axiom_id_list: List[str], desc: str, ctype="logic_conflict", severity="medium"):
        cid = self._gen_cid()
        cc = ConflictLog(
            cid=cid,
            ctype=ctype,
            involved_axioms=axiom_id_list,
            description=desc,
            severity=severity,
            status="pending",
            resolution=None
        )
        self.conflict_store[cid] = cc
        print(f" >> 日志记录 cid={cid} [{ctype}]：{desc}")
        return cid

    def axiom_reference_format(self, aid: str) -> str:
        ax = self.axiom_store.get(aid)
        if not ax or ax.status != "active":
            return "[INVALID‑REF]"
        return f"[{ax.aid}_v{ax.version}]"

    def deduction_safe_assert(self, aid: str, var_name: str, assign_val: Any):
        """
        推演断言审计：尝试给变量赋值，执行不坍缩检查
        若违规，写入冲突日志（deduction_violation）
        """
        ax = self.axiom_store.get(aid)
        if not ax or not ax.deduction_context_json:
            return True, None
        ctx_dict = json.loads(ax.deduction_context_json)
        mv_dict = {k: MarkedVariable(**v) for k, v in ctx_dict["marked_vars"].items()}
        known = ctx_dict["known_conditions"]
        ctx = DeductionContext(known_conditions=known, marked_vars=mv_dict)

        err_msg = ctx.forbid_collapse_check(var_name, assign_val)
        if err_msg is not None:
            self.mark_conflict(
                axiom_id_list=[aid],
                desc=err_msg,
                ctype="deduction_violation",
                severity="high"
            )
            return False, err_msg
        return True, None

    def topic_fetch(self, route: str, top_n: int = 3):
        hit_axioms = [a for a in self.axiom_store.values() if a.route == route and a.status == "active"]
        frag_list = [f for f in self.fragment_store.values() if route in f.tags]
        frag_list.sort(key=lambda x: x.active_score, reverse=True)
        hit_frags = frag_list[:top_n]
        return {
            "route": route,
            "axioms": hit_axioms,
            "hot_fragments": hit_frags
        }

    def export_archive(self):
        archive = {
            "axioms": {k: asdict(v) for k, v in self.axiom_store.items()},
            "fragments": {k: asdict(v) for k, v in self.fragment_store.items()},
            "conflict_log": {k: asdict(v) for k, v in self.conflict_store.items()},
            "global_marked_vars": {k: asdict(v) for k, v in self.global_marked_vars.items()}
        }
        return json.dumps(archive, ensure_ascii=False, indent=2)

    def load_archive(self, json_str: str):
        data = json.loads(json_str)
        for aid, ax_dict in data.get("axioms", {}).items():
            ax = Axiom(**ax_dict)
            self.axiom_store[aid] = ax
        for fid, fr_dict in data.get("fragments", {}).items():
            fr = Fragment(**fr_dict)
            self.fragment_store[fid] = fr
        for cid, cl_dict in data.get("conflict_log", {}).items():
            cl = ConflictLog(**cl_dict)
            self.conflict_store[cid] = cl
        for vname, mv_dict in data.get("global_marked_vars", {}).items():
            mv = MarkedVariable(**mv_dict)
            self.global_marked_vars[vname] = mv
        print(" >> 归档快照加载完成（含延标变量）")


# ====================== 融合原型演示案例 ======================
if __name__ == "__main__":
    mem = ShardedMemoryWithMarked()
    print("===== 分片记忆 + 延标延时闭合推演 融合原型演示 =====\n")

    # 1.写入原始碎片：用户提出一个现实问题案例（参考论文附录示例：学编程找工作）
    f1 = mem.add_fragment("用户：零基础学编程，半年之后能不能拿到20k月薪工作？", tags=["career_demo", "hypothesis"])
    print(f"碎片写入 fid={f1}\n")

    # 2.构造推演上下文：已知条件 + 多个延标变量（未闭合）
    known = {
        "study_months": 6,
        "target_salary": 20000,
        "user_start_level": "zero_basis"
    }
    mv1 = MarkedVariable(
        var_name="H_daily",
        desc="每日有效学习时长",
        origin_type="epistemic",
        closure_plan=["统计过去一周真实学习时长取均值", "开展两周试学观测"]
    )
    mv2 = MarkedVariable(
        var_name="M_market",
        desc="半年后市场岗位需求强度",
        origin_type="ontological",
        closure_plan=["持续跟踪招聘平台岗位发布数据，等待时间演化"]
    )
    deduction_ctx = DeductionContext(
        known_conditions=known,
        marked_vars={
            mv1.var_name: mv1,
            mv2.var_name: mv2
        }
    )

    # 3.模型归纳得到推演约束公理，走核验闸门，用户确认存入公理库
    axiom_text = "推演约束：能否拿到目标薪资取决于 H_daily(∞)、M_market(∞) 等未闭合参量，暂不输出确定结论，等待闭合方案执行。"
    aid = mem.review_candidate_axiom(
        raw_source_fids=[f1],
        candidate_text=axiom_text,
        route="career_deduction",
        user_choice="confirm",
        deduction_ctx=deduction_ctx
    )
    ref_tag = mem.axiom_reference_format(aid)
    print(f"\n公理引用标记 {ref_tag}")

    # 4.列出认知缺口（未闭合延标变量）
    gaps = deduction_ctx.list_gaps()
    print("\n【认知缺口清单（未闭合延标变量）】")
    for g in gaps:
        print(f" - {g.get_label()}：{g.desc}")
        print(f"   闭合方案：{g.closure_plan}")

    # 5.模拟违规：模型试图对未闭合延标变量强制赋值（触发延时不坍缩校验，写入冲突日志）
    print("\n-----模拟推演违规：强行给未闭合 H_daily 赋值 4-----")
    ok, err = mem.deduction_safe_assert(aid, "H_daily", assign_val=4)
    if not ok:
        print(f"拦截违规：{err}")

    # 6.模拟事实输入，外部完成延标闭合
    print("\n-----模拟外部事实回填：H_daily 实测得到真值=2.5小时-----")
    mv1.close(true_value=2.5)

    # 7.话题按需加载
    print("\n=====话题按需加载 career_deduction =====")
    topic_info = mem.topic_fetch("career_deduction")
    print(f"分支公理数量 {len(topic_info['axioms'])}")

    # 8.导出完整归档（记忆+延标变量全部保存）
    archive = mem.export_archive()
    print("\n=====归档包片段=====")
    print(archive[:800] + "...")

    # 9.归档恢复测试
    new_mem = ShardedMemoryWithMarked()
    new_mem.load_archive(archive)
    print(f"\n恢复后公理数量：{len(new_mem.axiom_store)}，全局延标变量数量：{len(new_mem.global_marked_vars)}")
