#!/usr/bin/env python3
"""Shared ISO-week identifiers for dashboard writers and readers."""


def iso_week_id(day):
    """Return an ISO year/week id such as ``2030-W01``.

    The ISO year can differ from the calendar year around New Year's Day.
    """
    iso_year, iso_week, _ = day.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"
