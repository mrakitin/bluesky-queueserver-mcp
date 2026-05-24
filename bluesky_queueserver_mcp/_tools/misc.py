"""Miscellaneous utility tools."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def set_user_name_to_login_name() -> None:
        """Set the API user name to the current OS login name.

        After calling this the API instance will use the login name of the
        process owner as the ``user`` parameter for all subsequent requests.
        """
        get_api().set_user_name_to_login_name()

    @mcp.tool()
    def get_default_lock_key(new_key: bool = False) -> str:
        """Return the default lock key stored on disk.

        Parameters
        ----------
        new_key:
            If True, generate and store a new random lock key.
        """
        return get_api().get_default_lock_key(new_key)

    @mcp.tool()
    def set_default_lock_key(lock_key: str) -> None:
        """Save a lock key as the default key on disk.

        Parameters
        ----------
        lock_key:
            Non-empty string to use as the default lock key.
        """
        get_api().set_default_lock_key(lock_key)
