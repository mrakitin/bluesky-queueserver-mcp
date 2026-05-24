"""Script upload and function execution tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def script_upload(
        script: str,
        update_lists: Optional[bool] = None,
        update_re: Optional[bool] = None,
        run_in_background: Optional[bool] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Upload and execute a Python script in the RE Worker environment.

        Parameters
        ----------
        script:
            Python source code to execute in the worker namespace.
        update_lists:
            If True, update the lists of existing plans and devices after
            the script is executed.
        update_re:
            If True, update the Run Engine instance after the script is executed.
        run_in_background:
            If True, run as a background task; if False, block until complete.
        lock_key:
            Lock key required if the environment is locked.
        """
        return get_api().script_upload(
            script,
            update_lists=update_lists,
            update_re=update_re,
            run_in_background=run_in_background,
            lock_key=lock_key,
        )

    @mcp.tool()
    def function_execute(
        name: str,
        args: Optional[list] = None,
        kwargs: Optional[dict] = None,
        run_in_background: Optional[bool] = None,
        user: Optional[str] = None,
        user_group: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Execute a function in the RE Worker environment.

        Parameters
        ----------
        name:
            Name of the function to execute (must be allowed for the user group).
        args:
            Positional arguments for the function.
        kwargs:
            Keyword arguments for the function.
        run_in_background:
            If True, run the function as a background task.
        user:
            Name of the user submitting the function.
        user_group:
            User group for permission checking.
        lock_key:
            Lock key required if the environment is locked.
        """
        item: dict = {"item_type": "function", "name": name}
        if args is not None:
            item["args"] = args
        if kwargs is not None:
            item["kwargs"] = kwargs
        return get_api().function_execute(
            item,
            run_in_background=run_in_background,
            user=user,
            user_group=user_group,
            lock_key=lock_key,
        )
