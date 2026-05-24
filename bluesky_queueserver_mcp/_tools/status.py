"""Status, ping, and config tools."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def status(reload: bool = False) -> dict:
        """Load status of RE Manager.

        Parameters
        ----------
        reload:
            Force immediate reload from the server (True) or return cached status (False).
        """
        return get_api().status(reload=reload)

    @mcp.tool()
    def ping(reload: bool = False) -> dict:
        """Ping RE Manager to check connectivity and retrieve basic status.

        Parameters
        ----------
        reload:
            Force reload (True) or return cached result (False).
        """
        return get_api().ping(reload=reload)

    @mcp.tool()
    def config_get() -> dict:
        """Get configuration of RE Manager (startup script/module/directory, etc.)."""
        return get_api().config_get()
