"""Plan execution history tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def history_get(reload: bool = False) -> dict:
        """Get the plan execution history.

        Parameters
        ----------
        reload:
            Force reload from server (True) or return cached history (False).
        """
        return get_api().history_get(reload=reload)

    @mcp.tool()
    def history_clear(
        size: Optional[int] = None,
        item_uid: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Clear the plan execution history.

        Parameters
        ----------
        size:
            Number of most recent history entries to keep (0 clears all).
        item_uid:
            Clear all entries up to and including the entry with this UID.
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().history_clear(size=size, item_uid=item_uid, lock_key=lock_key)
