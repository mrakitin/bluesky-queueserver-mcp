"""Background task status and wait tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def task_status(task_uid: Optional[str] = None) -> dict:
        """Get the status of a background task.

        Call this after ``script_upload``, ``function_execute``, or
        ``environment_update`` to check whether the task is still running.
        Those calls return a ``task_uid`` in their response — pass it here.

        Parameters
        ----------
        task_uid:
            UID of the background task.  Obtain it from the ``task_uid`` field
            in the response of ``script_upload``, ``function_execute``, or
            ``environment_update``.  This parameter is required.
        """
        if not task_uid:
            return {
                "success": False,
                "msg": (
                    "task_uid is required. First call script_upload, "
                    "function_execute, or environment_update and use the "
                    "task_uid from their response."
                ),
            }
        return get_api().task_status(task_uid)

    @mcp.tool()
    def task_result(task_uid: Optional[str] = None) -> dict:
        """Get the result of a completed background task.

        Call this after ``task_status`` reports the task has finished to
        retrieve the return value or error details.

        Parameters
        ----------
        task_uid:
            UID of the completed background task.  Obtain it from the
            ``task_uid`` field in the response of ``script_upload``,
            ``function_execute``, or ``environment_update``.  This parameter
            is required.
        """
        if not task_uid:
            return {
                "success": False,
                "msg": (
                    "task_uid is required. First call script_upload, "
                    "function_execute, or environment_update and use the "
                    "task_uid from their response."
                ),
            }
        return get_api().task_result(task_uid)

    @mcp.tool()
    def wait_for_completed_task(
        task_uid: Optional[str] = None,
        timeout: float = 600,
        treat_not_found_as_completed: bool = True,
    ) -> dict:
        """Block until a background task completes.

        Useful after ``script_upload``, ``function_execute``, or
        ``environment_update`` when you want to wait for the task to finish
        before proceeding.

        Parameters
        ----------
        task_uid:
            UID of the background task to wait for.  Obtain it from the
            ``task_uid`` field in the response of ``script_upload``,
            ``function_execute``, or ``environment_update``.  This parameter
            is required.
        timeout:
            Maximum time to wait in seconds (default 600).
        treat_not_found_as_completed:
            If True, treat a task that cannot be found as completed.
        """
        if not task_uid:
            return {
                "success": False,
                "msg": (
                    "task_uid is required. First call script_upload, "
                    "function_execute, or environment_update and use the "
                    "task_uid from their response."
                ),
            }
        return get_api().wait_for_completed_task(
            task_uid,
            timeout=timeout,
            treat_not_found_as_completed=treat_not_found_as_completed,
        )

    @mcp.tool()
    def wait_for_idle(timeout: float = 600) -> dict:
        """Block until RE Manager reaches the ``idle`` state.

        Parameters
        ----------
        timeout:
            Maximum time to wait in seconds (default 600).
        """
        return get_api().wait_for_idle(timeout=timeout)

    @mcp.tool()
    def wait_for_idle_or_paused(timeout: float = 600) -> dict:
        """Block until RE Manager reaches ``idle`` or ``paused`` state.

        Parameters
        ----------
        timeout:
            Maximum time to wait in seconds (default 600).
        """
        return get_api().wait_for_idle_or_paused(timeout=timeout)

    @mcp.tool()
    def wait_for_idle_or_running(timeout: float = 600) -> dict:
        """Block until RE Manager reaches ``idle`` or ``running`` state.

        Parameters
        ----------
        timeout:
            Maximum time to wait in seconds (default 600).
        """
        return get_api().wait_for_idle_or_running(timeout=timeout)
