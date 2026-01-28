from typing import Any

from strix.tools.registry import register_tool


@register_tool
def terminal_execute(
    command: str,
    is_input: bool = False,
    timeout: float | None = None,
    terminal_id: str | None = None,
    no_enter: bool = False,
) -> dict[str, Any]:
    from .terminal_manager import get_terminal_manager

    manager = get_terminal_manager()

    try:
        return manager.execute_command(
            command=command,
            is_input=is_input,
            timeout=timeout,
            terminal_id=terminal_id,
            no_enter=no_enter,
        )
    except (ValueError, RuntimeError) as e:
        return {
            "error": str(e),
            "command": command,
            "terminal_id": terminal_id or "default",
            "content": "",
            "status": "error",
            "exit_code": None,
            "working_dir": None,
        }
@register_tool
def terminal_list() -> dict[str, Any]:
    from .terminal_manager import get_terminal_manager

    manager = get_terminal_manager()
    result = manager.list_sessions()
    result["max_temp_allowed"] = manager.max_temp_terminals
    return result


@register_tool
def terminal_close(terminal_id: str) -> dict[str, Any]:
    from .terminal_manager import get_terminal_manager

    manager = get_terminal_manager()
    return manager.close_session(terminal_id)
