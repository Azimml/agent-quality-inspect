import re
from typing import Any

from agent_inspect.core.utils import get_config_or_default


def regex_match(candidate: str, pattern: str, config: dict[str, Any] | None = None) -> bool:
    mode = get_config_or_default(config, "mode", "substring")
    flags = 0
    if mode == "full":
        return re.fullmatch(pattern, candidate, flags) is not None
    else:
        return re.search(pattern, candidate, flags) is not None
