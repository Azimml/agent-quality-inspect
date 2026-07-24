from enum import Enum, unique


@unique
class EvaluationComponent(Enum):
    EVALUATION_ERROR_CODE = "05"


@unique
class UserProxyComponent(Enum):
    USER_PROXY_ERROR_CODE = "06"


@unique
class ClientComponent(Enum):
    CLIENT_ERROR_CODE = "07"


@unique
class ToolComponent(Enum):
    TOOL_ERROR_CODE = "08"


@unique
class ErrorCode(Enum):
    """Stable, machine-readable error identifiers.

    The numeric string values are part of the public error contract and must
    never be reused or renumbered once released; new codes are appended. Members
    are grouped by the subsystem that raises them so the enum stays navigable as
    it grows.
    """

    # --- Generic input / value validation ---
    MISSING_VALUE = "0008"
    INVALID_VALUE = "0009"

    # --- LLM-as-a-judge & majority voting ---
    INVALID_LLM_JUDGE_RESULT_ERROR = "0000"
    INVALID_JUDGE_TRIALS_ERROR = "0002"
    INVALID_JUDGE_RESPONSE_FORMAT_ERROR = "0003"
    INSUFFICIENT_JUDGE_RESPONSES_ERROR = "0007"
    UNSUCCESSFUL_MAJORITY_VOTING = "0016"

    # --- Metric scoring (progress / AUC / PPT / success / tool correctness) ---
    EMPTY_VALIDATION_RESULT = "0004"
    EMPTY_PROGRESS_SCORE = "0005"
    AUC_CALCULATION_ERROR = "0006"
    PPT_CALCULATION_ERROR = "0012"
    UNSUPPORTED_ATTRIBUTION_TYPE = "0013"

    # --- User proxy ---
    INVALID_USER_MESSAGE_REFLECTION = "0010"
    INVALID_USER_PROXY_RESPONSE = "0011"

    # --- Client / transport ---
    MAX_RETRY_EXCEEDED_ERROR = "0001"
    CLIENT_REQUEST_ERROR = "0017"

    # --- Error-analysis tooling ---
    INVALID_JSON_DECODE_ERROR = "0014"
    UNSUCCESSFUL_LLM_SUMMARIZATION = "0015"
    INVALID_ERROR_ANALYSIS_ERROR_CLUSTERS = "0018"
