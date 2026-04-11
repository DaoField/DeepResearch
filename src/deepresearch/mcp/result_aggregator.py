# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

from datetime import datetime
from typing import Optional
from uuid import uuid4

from .types import AgentResult, CollaborationResult, CollaborationSession

import logging

logger = logging.getLogger(__name__)


class ResultAggregator:
    """结果聚合器

    聚合多个智能体的输出，生成最终的协作结果。
    """

    def __init__(self):
        pass

    def add_agent_result(
        self,
        session: CollaborationSession,
        agent_id: str,
        agent_name: str,
        output: str,
        score: float = 0.0,
        feedback: Optional[str] = None,
    ) -> AgentResult:
        """添加智能体结果

        Args:
            session: 协作会话
            agent_id: 智能体ID
            agent_name: 智能体名称
            output: 输出内容
            score: 质量评分
            feedback: 反馈内容

        Returns:
            创建的 AgentResult 对象
        """
        result = AgentResult(
            agent_id=agent_id,
            agent_name=agent_name,
            output=output,
            score=score,
            feedback=feedback,
            timestamp=datetime.now(),
        )

        if session.result is None:
            session.result = CollaborationResult(
                id=str(uuid4()),
                session_id=session.session_id,
                summary="",
                agent_results=[],
                overall_score=0.0,
            )

        session.result.agent_results.append(result)

        return result

    def calculate_overall_score(self, session: CollaborationSession) -> float:
        """计算总体评分

        计算所有智能体结果的平均分

        Args:
            session: 协作会话

        Returns:
            总体评分
        """
        if session.result is None or not session.result.agent_results:
            return 0.0

        total = sum(r.score for r in session.result.agent_results)
        return total / len(session.result.agent_results)

    def generate_summary(
        self,
        session: CollaborationSession,
        custom_summary: Optional[str] = None,
    ) -> str:
        """生成最终汇总

        Args:
            session: 协作会话
            custom_summary: 自定义汇总，如果提供则直接使用

        Returns:
            汇总文本
        """
        if custom_summary is not None:
            if session.result:
                session.result.summary = custom_summary
            return custom_summary

        if session.result is None:
            return ""

        # 如果没有自定义汇总，自动生成一个基本汇总
        agent_outputs = []
        for ar in session.result.agent_results:
            agent_outputs.append(f"## {ar.agent_name} 输出\n\n{ar.output}")

        summary = "\n\n".join(agent_outputs)
        session.result.summary = summary
        return summary

    def get_final_result(self, session: CollaborationSession) -> Optional[CollaborationResult]:
        """获取最终结果

        Args:
            session: 协作会话

        Returns:
            最终结果，如果没有结果返回 None
        """
        if session.result is None:
            return None

        session.result.overall_score = self.calculate_overall_score(session)
        if not session.result.summary:
            self.generate_summary(session)

        return session.result


# 全局单例
result_aggregator = ResultAggregator()
