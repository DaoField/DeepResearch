"""DeepResearch 项目相关异常定义。"""


class DeepResearchError(RuntimeError):
    """DeepResearch 项目错误基类。"""


class ConfigError(DeepResearchError):
    """配置相关错误，如配置缺失或不合法导致的错误。"""


class SearchError(DeepResearchError):
    """搜索相关错误，如搜索失败、搜索配置错误等。"""


class LLMError(DeepResearchError):
    """LLM 相关错误，如 LLM 调用失败、响应格式错误等。"""


class ReportError(DeepResearchError):
    """报告生成相关错误，如报告生成失败、格式错误等。"""

    def __init__(self, message: str, *, section: str | None = None) -> None:
        super().__init__(message)
        self.section = section
