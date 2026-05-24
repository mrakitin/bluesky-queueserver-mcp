"""User group permissions tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def permissions_get() -> dict:
        """Get the current user group permissions from RE Manager."""
        return get_api().permissions_get()

    @mcp.tool()
    def permissions_set(
        user_group_permissions: dict, lock_key: Optional[str] = None
    ) -> dict:
        """Upload new user group permissions to RE Manager.

        Parameters
        ----------
        user_group_permissions:
            Dict of user group permissions to upload.  The structure must match
            the permissions YAML schema used by RE Manager.
        lock_key:
            Lock key required if permissions management is locked.
        """
        return get_api().permissions_set(
            user_group_permissions, lock_key=lock_key
        )

    @mcp.tool()
    def permissions_reload(
        restore_plans_devices: Optional[bool] = None,
        restore_permissions: Optional[bool] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Reload user group permissions and/or plans/devices lists from disk.

        Parameters
        ----------
        restore_plans_devices:
            If True, reload the list of existing plans and devices from disk.
        restore_permissions:
            If True, reload user group permissions from disk.
        lock_key:
            Lock key required if permissions management is locked.
        """
        return get_api().permissions_reload(
            restore_plans_devices=restore_plans_devices,
            restore_permissions=restore_permissions,
            lock_key=lock_key,
        )
