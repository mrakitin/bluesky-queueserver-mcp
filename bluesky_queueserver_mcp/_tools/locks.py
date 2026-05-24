"""Queue and environment lock management tools."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import fastmcp


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def lock(
        lock_key: Optional[str] = None,
        environment: Optional[bool] = None,
        queue: Optional[bool] = None,
        note: Optional[str] = None,
        user: Optional[str] = None,
    ) -> dict:
        """Lock RE Manager resources (queue and/or environment).

        Parameters
        ----------
        lock_key:
            Lock key to use.  If not provided the default lock key is used.
        environment:
            If True, lock the RE Worker environment.
        queue:
            If True, lock the plan queue.
        note:
            Optional note describing the reason for the lock.
        user:
            Name of the user acquiring the lock.
        """
        return get_api().lock(lock_key, environment=environment, queue=queue, note=note, user=user)

    @mcp.tool()
    def lock_all(
        lock_key: Optional[str] = None,
        note: Optional[str] = None,
        user: Optional[str] = None,
    ) -> dict:
        """Lock both the RE Worker environment and the plan queue.

        Parameters
        ----------
        lock_key:
            Lock key to use.  If not provided the default lock key is used.
        note:
            Optional note describing the reason for the lock.
        user:
            Name of the user acquiring the lock.
        """
        return get_api().lock_all(lock_key, note=note, user=user)

    @mcp.tool()
    def lock_environment(
        lock_key: Optional[str] = None,
        note: Optional[str] = None,
        user: Optional[str] = None,
    ) -> dict:
        """Lock only the RE Worker environment.

        Parameters
        ----------
        lock_key:
            Lock key to use.  If not provided the default lock key is used.
        note:
            Optional note describing the reason for the lock.
        user:
            Name of the user acquiring the lock.
        """
        return get_api().lock_environment(lock_key, note=note, user=user)

    @mcp.tool()
    def lock_queue(
        lock_key: Optional[str] = None,
        note: Optional[str] = None,
        user: Optional[str] = None,
    ) -> dict:
        """Lock only the plan queue.

        Parameters
        ----------
        lock_key:
            Lock key to use.  If not provided the default lock key is used.
        note:
            Optional note describing the reason for the lock.
        user:
            Name of the user acquiring the lock.
        """
        return get_api().lock_queue(lock_key, note=note, user=user)

    @mcp.tool()
    def lock_info(lock_key: Optional[str] = None, reload: bool = False) -> dict:
        """Get information about the current lock state.

        Parameters
        ----------
        lock_key:
            Lock key to verify against the current lock.
        reload:
            Force reload (True) or return cached lock info (False).
        """
        return get_api().lock_info(lock_key, reload=reload)

    @mcp.tool()
    def unlock(lock_key: Optional[str] = None) -> dict:
        """Unlock previously locked RE Manager resources.

        Parameters
        ----------
        lock_key:
            Lock key that was used to acquire the lock.  If not provided the
            default lock key is used.
        """
        return get_api().unlock(lock_key)
