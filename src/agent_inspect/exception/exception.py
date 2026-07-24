from agent_inspect.exception.error_codes import (
    EvaluationComponent,
    ToolComponent,
    UserProxyComponent,
)


class EvaluationError(Exception):
    """Base exception class for Evaluation errors."""

    def __init__(self, internal_code: str, message: str):
        self.internal_code = EvaluationComponent.EVALUATION_ERROR_CODE.value + internal_code
        self.message = f"Internal Code: {self.internal_code}, Error Message: {message}"
        super().__init__(self.message)


class InvalidInputValueError(ValueError):
    """Raised when an input value fails validation.

    Subclasses :class:`ValueError` so callers can catch it as a standard invalid
    value, while still exposing the toolkit's stable ``internal_code`` contract.
    The ``component_code`` prefix defaults to the evaluation component but can be
    overridden by callers in other subsystems.
    """

    def __init__(
        self,
        internal_code: str,
        message: str,
        component_code=EvaluationComponent.EVALUATION_ERROR_CODE.value,
    ):
        self.internal_code = component_code + internal_code
        self.message = f"Internal Code: {self.internal_code}, Error Message: {message}"
        super().__init__(self.message)


class UserProxyError(Exception):
    """Base exception class for user-proxy (simulated user) errors."""

    def __init__(self, internal_code: str, message: str):
        self.internal_code = UserProxyComponent.USER_PROXY_ERROR_CODE.value + internal_code
        self.message = f"Internal Code: {self.internal_code}, Error Message: {message}"
        super().__init__(self.message)


class ToolError(Exception):
    """Base exception class for Tool errors."""

    def __init__(self, internal_code: str, message: str):
        self.internal_code = ToolComponent.TOOL_ERROR_CODE.value + internal_code
        self.message = f"Internal Code: {self.internal_code}, Error Message: {message}"
        super().__init__(self.message)
