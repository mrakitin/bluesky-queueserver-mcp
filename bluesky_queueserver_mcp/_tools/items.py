"""Plan item operation tools."""

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    import fastmcp


def _build_item(
    name: str,
    item_type: str = "plan",
    args: Optional[List[Any]] = None,
    kwargs: Optional[dict] = None,
    item_uid: Optional[str] = None,
) -> dict:
    """Construct an item dict from flat parameters."""
    item: dict = {"item_type": item_type, "name": name}
    if args is not None:
        item["args"] = args
    if kwargs is not None:
        item["kwargs"] = kwargs
    if item_uid is not None:
        item["item_uid"] = item_uid
    return item


def register(mcp: "fastmcp.FastMCP", get_api) -> None:
    @mcp.tool()
    def item_add(
        name: str,
        item_type: str = "plan",
        args: Optional[List[Any]] = None,
        kwargs: Optional[dict] = None,
        pos: Optional[Any] = None,
        before_uid: Optional[str] = None,
        after_uid: Optional[str] = None,
        user: Optional[str] = None,
        user_group: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Add a plan or instruction to the queue.

        Parameters
        ----------
        name:
            Name of the plan or instruction, e.g. ``"count"``, ``"scan"``.
        item_type:
            ``"plan"`` (default) or ``"instruction"``.
        args:
            Positional arguments for the plan.  For most plans the first
            positional argument is a list of detector names, e.g.
            ``[["det1", "det2"]]``.
        kwargs:
            Keyword arguments for the plan, e.g. ``{"num": 5, "delay": 0.1}``.
        pos:
            Position in the queue to insert the item (integer, ``"front"``,
            or ``"back"``).  Defaults to the back of the queue.
        before_uid:
            Insert the item just before the item with this UID.
        after_uid:
            Insert the item just after the item with this UID.
        user:
            Name of the user submitting the item.
        user_group:
            User group for permission checking.
        lock_key:
            Lock key required if the queue is locked.
        """
        item = _build_item(name, item_type, args, kwargs)
        return get_api().item_add(
            item,
            pos=pos,
            before_uid=before_uid,
            after_uid=after_uid,
            user=user,
            user_group=user_group,
            lock_key=lock_key,
        )

    @mcp.tool()
    def item_add_batch(
        items: List[dict],
        pos: Optional[Any] = None,
        before_uid: Optional[str] = None,
        after_uid: Optional[str] = None,
        user: Optional[str] = None,
        user_group: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Add a batch of items to the queue in a single request.

        Each item in the list must have at minimum ``item_type`` and ``name``
        keys, e.g. ``{"item_type": "plan", "name": "count", "args": [["det1"]],
        "kwargs": {"num": 5}}``.

        Parameters
        ----------
        items:
            List of item dicts.
        pos:
            Position for the first item in the batch.
        before_uid:
            Insert batch before the item with this UID.
        after_uid:
            Insert batch after the item with this UID.
        user:
            Name of the user submitting the items.
        user_group:
            User group for permission checking.
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().item_add_batch(
            items,
            pos=pos,
            before_uid=before_uid,
            after_uid=after_uid,
            user=user,
            user_group=user_group,
            lock_key=lock_key,
        )

    @mcp.tool()
    def item_get(pos: Optional[Any] = None, uid: Optional[str] = None) -> dict:
        """Get a single item from the queue by position or UID.

        Parameters
        ----------
        pos:
            Position in the queue (integer or ``"front"``/``"back"``).
        uid:
            UID of the item to retrieve.
        """
        return get_api().item_get(pos=pos, uid=uid)

    @mcp.tool()
    def item_move(
        pos: Optional[Any] = None,
        uid: Optional[str] = None,
        pos_dest: Optional[Any] = None,
        before_uid: Optional[str] = None,
        after_uid: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Move an item within the queue.

        Parameters
        ----------
        pos:
            Current position of the item to move.
        uid:
            UID of the item to move.
        pos_dest:
            Destination position.
        before_uid:
            Move the item to just before the item with this UID.
        after_uid:
            Move the item to just after the item with this UID.
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().item_move(
            pos=pos,
            uid=uid,
            pos_dest=pos_dest,
            before_uid=before_uid,
            after_uid=after_uid,
            lock_key=lock_key,
        )

    @mcp.tool()
    def item_move_batch(
        uids: List[str],
        pos_dest: Optional[Any] = None,
        before_uid: Optional[str] = None,
        after_uid: Optional[str] = None,
        reorder: Optional[bool] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Move a batch of items within the queue.

        Parameters
        ----------
        uids:
            List of UIDs of items to move.
        pos_dest:
            Destination position for the batch.
        before_uid:
            Move batch to just before the item with this UID.
        after_uid:
            Move batch to just after the item with this UID.
        reorder:
            If True, reorder items to match the order of ``uids``.
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().item_move_batch(
            uids=uids,
            pos_dest=pos_dest,
            before_uid=before_uid,
            after_uid=after_uid,
            reorder=reorder,
            lock_key=lock_key,
        )

    @mcp.tool()
    def item_remove(
        pos: Optional[Any] = None,
        uid: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Remove an item from the queue by position or UID.

        Parameters
        ----------
        pos:
            Position of the item to remove.
        uid:
            UID of the item to remove.
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().item_remove(pos=pos, uid=uid, lock_key=lock_key)

    @mcp.tool()
    def item_remove_batch(
        uids: List[str],
        ignore_missing: Optional[bool] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Remove a batch of items from the queue by their UIDs.

        Parameters
        ----------
        uids:
            List of UIDs to remove.
        ignore_missing:
            If True, silently skip UIDs that are not found in the queue.
        lock_key:
            Lock key required if the queue is locked.
        """
        return get_api().item_remove_batch(
            uids=uids, ignore_missing=ignore_missing, lock_key=lock_key
        )

    @mcp.tool()
    def item_update(
        item_uid: str,
        name: Optional[str] = None,
        item_type: str = "plan",
        args: Optional[List[Any]] = None,
        kwargs: Optional[dict] = None,
        replace: Optional[bool] = None,
        user: Optional[str] = None,
        user_group: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Update an existing item in the queue.

        Parameters
        ----------
        item_uid:
            UID of the existing queue item to update (required).
        name:
            New plan name (if changing).
        item_type:
            ``"plan"`` (default) or ``"instruction"``.
        args:
            New positional arguments for the plan.
        kwargs:
            New keyword arguments for the plan.
        replace:
            If True, replace all parameters; if False (default), merge with
            existing values.
        user:
            Name of the user performing the update.
        user_group:
            User group for permission checking.
        lock_key:
            Lock key required if the queue is locked.
        """
        item: dict = {"item_uid": item_uid, "item_type": item_type}
        if name is not None:
            item["name"] = name
        if args is not None:
            item["args"] = args
        if kwargs is not None:
            item["kwargs"] = kwargs
        return get_api().item_update(
            item,
            replace=replace,
            user=user,
            user_group=user_group,
            lock_key=lock_key,
        )

    @mcp.tool()
    def item_execute(
        name: Optional[str] = None,
        item_type: str = "plan",
        args: Optional[List[Any]] = None,
        kwargs: Optional[dict] = None,
        user: Optional[str] = None,
        user_group: Optional[str] = None,
        lock_key: Optional[str] = None,
    ) -> dict:
        """Immediately execute a single plan *outside* the queue (bypasses the queue).

        **Important:** This tool does NOT run plans already in the queue.
        To start the queue, use ``queue_start`` instead.  Use ``item_execute``
        only when you want to run a one-off plan immediately without adding it
        to the queue first.

        Parameters
        ----------
        name:
            Name of the plan or function to execute, e.g. ``"count"``.
            This parameter is required — you must specify what plan to run.
        item_type:
            ``"plan"`` (default) or ``"function"``.
        args:
            Positional arguments, e.g. ``[["det1", "det2"]]``.
        kwargs:
            Keyword arguments, e.g. ``{"num": 5}``.
        user:
            Name of the user submitting the item.
        user_group:
            User group for permission checking.
        lock_key:
            Lock key required if the environment is locked.
        """
        if not name:
            return {
                "success": False,
                "msg": (
                    "name is required for item_execute. "
                    "If you want to start plans already in the queue, "
                    "use queue_start instead."
                ),
            }
        item = _build_item(name, item_type, args, kwargs)
        return get_api().item_execute(
            item, user=user, user_group=user_group, lock_key=lock_key
        )
