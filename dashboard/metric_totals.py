#!/usr/bin/env python3
"""Compatibility helpers for grouped dashboard metrics.

Older data stores platform/activity splits (instagram/tiktok/hellotalk and
running/gym). Daily-note input stores one honest total because /today asks for
one number per public metric. Readers must support both shapes during migration.
"""


def grouped_total(value):
    """Return a non-negative integer total from a scalar or grouped mapping.

    A mapping's explicit ``total`` is authoritative. This prevents double
    counting if a migration temporarily leaves legacy detail keys beside it.
    """
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return max(0, int(value))
    if not isinstance(value, dict):
        return 0

    explicit = value.get("total")
    if isinstance(explicit, (int, float)) and not isinstance(explicit, bool):
        return max(0, int(explicit))

    return sum(
        max(0, int(item))
        for item in value.values()
        if isinstance(item, (int, float)) and not isinstance(item, bool)
    )
