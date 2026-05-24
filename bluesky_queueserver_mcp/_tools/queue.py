"""Queue operation tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def queue_get(reload: bool = False) -> dict:
        """Return the list of items in the plan queue and the currently running plan.

        Parameters
        ----------
        reload:
            Force reload from server (True) or use cached copy (False).
        """
        return get_api().queue_get(reload=reload)

    @mcp.tool()
    def queue_start(lock_key: Optional[str] = None) -> dict:
        """Start executing plans from the queue.

        Use this tool when the user says things like "run the plan", "start the
        queue", "execute the queue", "run the experiment", or "go".  It
        instructs the RE Manager to begin processing items already in the queue
        one by one.  If you want to add a plan first, call ``item_add`` before
        calling this tool.

        Parameters
        ----------
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().queue_start(lock_key=lock_key)

    @mcp.tool()
    def queue_stop(lock_key: Optional[str] = None) -> dict:
        """Request the queue to stop after the currently running plan completes.

        Parameters
        ----------
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().queue_stop(lock_key=lock_key)

    @mcp.tool()
    def queue_stop_cancel(lock_key: Optional[str] = None) -> dict:
        """Cancel a previously requested queue stop.

        Parameters
        ----------
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().queue_stop_cancel(lock_key=lock_key)

    @mcp.tool()
    def queue_clear(lock_key: Optional[str] = None) -> dict:
        """Remove all items from the plan queue.

        Parameters
        ----------
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().queue_clear(lock_key=lock_key)

    @mcp.tool()
    def queue_autostart(enable: bool, lock_key: Optional[str] = None) -> dict:
        """Enable or disable autostart mode for the queue.

        When autostart is enabled the queue starts executing automatically when
        new items are added.

        Parameters
        ----------
        enable:
            True to enable autostart, False to disable.
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().queue_autostart(enable, lock_key=lock_key)

    @mcp.tool()
    def queue_mode_set(
        loop: Optional[bool] = None,
        ignore_failures: Optional[bool] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Set queue execution mode parameters.

        Parameters
        ----------
        loop:
            Enable loop mode (True) so the queue restarts after the last item.
        ignore_failures:
            When True the queue continues executing after a failed plan.
        lock_key:
            Lock key required if the queue is locked.
        """
        kwargs: dict = {}
        if loop is not None:
            kwargs["loop"] = loop
        if ignore_failures is not None:
            kwargs["ignore_failures"] = ignore_failures
        if lock_key is not None:
            kwargs["lock_key"] = lock_key
        return get_api().queue_mode_set(**kwargs)
