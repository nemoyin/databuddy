from __future__ import annotations
from jwbuddy.config import settings
from jwbuddy.llm.backends import LLMBackend, OpenAICompatibleBackend, LLMResult


class LLMGateway:
    """LLM 路由网关 — 根据上下文选择合适的后端"""

    def __init__(self):
        self._internal: OpenAICompatibleBackend | None = None
        self._cloud: OpenAICompatibleBackend | None = None

    @property
    def internal(self) -> OpenAICompatibleBackend:
        if self._internal is None:
            self._internal = OpenAICompatibleBackend(
                base_url=settings.llm_internal_base_url,
                api_key=settings.llm_internal_api_key,
                model=settings.llm_internal_model,
            )
        return self._internal

    @property
    def cloud(self) -> OpenAICompatibleBackend:
        if self._cloud is None:
            self._cloud = OpenAICompatibleBackend(
                base_url=settings.llm_cloud_base_url,
                api_key=settings.llm_cloud_api_key,
                model=settings.llm_cloud_model,
            )
        return self._cloud

    def route(self, is_sensitive: bool = False, requires_reasoning: bool = False) -> LLMBackend:
        """路由决策: 涉密/推理→内网, 云端未配置→内网, 否则云端优先"""
        if is_sensitive or requires_reasoning:
            return self.internal
        # 如果云端未配置，直接走内网
        if not settings.llm_cloud_base_url or not settings.llm_cloud_api_key:
            return self.internal
        if settings.llm_fallback_enabled:
            return self.cloud
        return self.internal

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        is_sensitive: bool = False,
        requires_reasoning: bool = False,
    ) -> LLMResult:
        backend = self.route(is_sensitive, requires_reasoning)
        return await backend.chat(messages, tools)


gateway = LLMGateway()
