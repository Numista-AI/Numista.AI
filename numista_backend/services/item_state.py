"""item_state.py: item-state helpers shared by the readers of users/{uid}/coins (PLAN v1.2, R3).

Mark Sold, never delete: a sold item keeps its doc with status == "sold". The doc is a record, not part of
the owned collection, so every reader that counts, values, de-duplicates, reports on or clears the
collection must skip it. Sold is keyed on `status` (never `transferStatus`, which moves to "pending"
while a buyer transfer is open).

Kept free of heavy imports so it can be imported anywhere.
"""
from typing import Any, Dict, Iterable, Iterator


def is_sold_item(data: Dict[str, Any]) -> bool:
    return (data or {}).get("status") == "sold"


def unsold_docs(docs: Iterable[Any]) -> Iterator[Any]:
    """Filter Firestore snapshots, dropping Sold items."""
    for doc in docs:
        if not is_sold_item(doc.to_dict() or {}):
            yield doc
