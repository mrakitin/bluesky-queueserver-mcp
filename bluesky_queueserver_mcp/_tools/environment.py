"""RE Worker environment tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def environment_open(lock_key: Optional[str] = None) -> dict:
        """Open the RE Worker environment.

        Initiates opening of the worker environment.  The ``manager_state`` status
        parameter changes to ``creating_environment`` while the operation is in
        progress and back to ``idle`` when complete.  Check
        ``worker_environment_exists`` in the status to confirm success.

        Parameters
        ----------
        lock_key:
            Lock key required if the environment is locked.
        """
        return get_api().environment_open(lock_key=lock_key)

    @mcp.tool()
    def environment_close(lock_key: Optional[str] = None) -> dict:
        """Close the RE Worker environment gracefully.

        Parameters
        ----------
        lock_key:
            Lock key required if the environment is locked.
        """
        return get_api().environment_close(lock_key=lock_key)

    @mcp.tool()
    def environment_destroy(lock_key: Optional[str] = None) -> dict:
        """Forcibly destroy the RE Worker environment.

        Use this when ``environment_close`` fails or the environment is unresponsive.

        Parameters
        ----------
        lock_key:
            Lock key required if the environment is locked.
        """
        return get_api().environment_destroy(lock_key=lock_key)

    @mcp.tool()
    def environment_update(
        run_in_background: Optional[bool] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Update the RE Worker environment (reload startup script/module).

        Parameters
        ----------
        run_in_background:
            Run the update as a background task (True) or wait for completion (False).
        lock_key:
            Lock key required if the environment is locked.
        """
        return get_api().environment_update(
            run_in_background=run_in_background, lock_key=lock_key
        )
