"""Plans and devices listing tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def _devices_table(devices: dict) -> str:
    """Format a devices dict as a markdown table."""
    rows = []
    for name, info in sorted(devices.items()):
        rows.append((
            name,
            info.get("classname", ""),
            info.get("module", ""),
            "✓" if info.get("is_readable") else "",
            "✓" if info.get("is_movable") else "",
            "✓" if info.get("is_flyable") else "",
        ))
    header = "| Name | Class | Module | Readable | Movable | Flyable |\n"
    sep    = "|------|-------|--------|----------|---------|--------|\n"
    body   = "".join(
        f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |\n"
        for r in rows
    )
    return header + sep + body


def _plans_table(plans: dict) -> str:
    """Format a plans dict as a markdown table."""
    rows = []
    for name, info in sorted(plans.items()):
        module = info.get("module", "")
        doc = (info.get("description") or "").split("\n")[0].strip()
        rows.append((name, module, doc))
    header = "| Name | Module | Description |\n"
    sep    = "|------|--------|-------------|\n"
    body   = "".join(
        f"| {r[0]} | {r[1]} | {r[2]} |\n"
        for r in rows
    )
    return header + sep + body


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def list_devices(
        reload: bool = False,
        user_group: Optional[str] = None,
    ) -> str:
        """List all allowed devices as a formatted table.

        Use this tool when the user asks to "list devices", "show devices",
        "what devices are available", "show me the devices", "devices in a
        table", or any similar request for a human-readable device overview.

        Returns a markdown table with columns:
        Name | Class | Module | Readable | Movable | Flyable

        Parameters
        ----------
        reload:
            Force reload from server (True) or return cached list (False).
        user_group:
            User group whose allowed devices to retrieve.
        """
        r = get_api().devices_allowed(reload=reload, user_group=user_group)
        devices = r.get("devices_allowed", {})
        if not devices:
            return f"No devices found. API response: {r}"
        return _devices_table(devices)

    @mcp.tool()
    def list_plans(
        reload: bool = False,
        user_group: Optional[str] = None,
    ) -> str:
        """List all allowed plans as a formatted table.

        Use this tool when the user asks to "list plans", "show plans",
        "what plans are available", "show me the plans", "plans in a table",
        or any similar request for a human-readable plan overview.

        Returns a markdown table with columns:
        Name | Module | Description

        Parameters
        ----------
        reload:
            Force reload from server (True) or return cached list (False).
        user_group:
            User group whose allowed plans to retrieve.
        """
        r = get_api().plans_allowed(reload=reload, user_group=user_group)
        plans = r.get("plans_allowed", {})
        if not plans:
            return f"No plans found. API response: {r}"
        return _plans_table(plans)

    @mcp.tool()
    def plans_allowed(reload: bool = False, user_group: Optional[str] = None) -> dict:
        """Get the raw list of plans allowed for the current (or specified) user group.

        Returns the full structured dict including parameter schemas.
        For a human-readable overview, use ``list_plans`` instead.

        Parameters
        ----------
        reload:
            Force reload from server (True) or return cached list (False).
        user_group:
            User group whose allowed plans to retrieve.  Defaults to the
            user group configured on the API instance.
        """
        return get_api().plans_allowed(reload=reload, user_group=user_group)

    @mcp.tool()
    def plans_existing(reload: bool = False) -> dict:
        """Get the list of all plans that exist in the RE Worker environment.

        Parameters
        ----------
        reload:
            Force reload from server (True) or return cached list (False).
        """
        return get_api().plans_existing(reload=reload)

    @mcp.tool()
    def devices_allowed(reload: bool = False, user_group: Optional[str] = None) -> dict:
        """Get the raw list of devices allowed for the current (or specified) user group.

        Returns the full structured dict including component trees.
        For a human-readable overview, use ``list_devices`` instead.

        Parameters
        ----------
        reload:
            Force reload from server (True) or return cached list (False).
        user_group:
            User group whose allowed devices to retrieve.
        """
        return get_api().devices_allowed(reload=reload, user_group=user_group)

    @mcp.tool()
    def devices_existing(reload: bool = False) -> dict:
        """Get the list of all devices that exist in the RE Worker environment.

        Parameters
        ----------
        reload:
            Force reload from server (True) or return cached list (False).
        """
        return get_api().devices_existing(reload=reload)
