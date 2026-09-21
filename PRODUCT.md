# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python generates static SVG. GitHub Actions regenerate it on a schedule and rewrite
README.md around it. The README embeds the SVG through `raw.githubusercontent.com`.

Constraint this places on design: an SVG loaded through `<img>` cannot fetch a web
font. A face outside the system stack must be embedded as a subset data URI inside
the SVG, or converted to paths. Verified, not assumed.

## Users

**Primary: investors and prospective hires** who open the GitHub profile cold, in a
browser tab, alongside other tabs. They arrive from a pitch, a link, or a search.
They spend seconds, not minutes, and they have seen many profiles.

Secondary: KB, weekly, when he enters the numbers by hand. That entry is deliberate —
the act of writing the number is the review, and automating it away would remove the
only moment he stops to check whether he did what he said mattered.

## Product Purpose

A public weekly record of whether KB did the work he said was important.

Success is a reader concluding, without being told, that this person runs on a system:
that the work is measured, that the measurement is honest about its own gaps, and that
the whole thing is presented with care.

Failure is the reader concluding it is a vanity dashboard, or not being able to tell
which numbers are trustworthy.

## Positioning

Most profile dashboards show only what a machine can count, because that is the part
that never embarrasses anyone. This one carries six rows, of which **one is measured
and five are testimony**, and it says which is which on the surface rather than
flattening them into one number.

A competitor cannot copy that by adding a widget. It requires publishing the gaps.

## Capabilities

Six weekly rows, twelve weeks of history.

| Row | Source | Goal |
|---|---|---|
| Pull requests merged | GitHub search API, counted | 60 |
| Talks with users | entered by hand | 7 |
| Social posts | entered by hand | 7 |
| Workouts | entered by hand | 7 |
| Coffee chats | entered by hand | 2 |
| Blog posts | entered by hand | 1 |

Token usage is still collected and stored in `dashboard/data.json`; it is no longer
displayed. Removed 2026-09-20 — it measured spend, not work.

## Constraints

- **Four states share one cell today.** A `0` currently means any of: measured zero,
  reported zero, never reported, or the unfilled default. The design must separate
  them; this is the product's core honesty problem, not a polish item.
- **Unfilled default is `1`**, decided 2026-09-20. It reads as "not yet entered," and
  the surface must not present it as an achievement.
- **Five consecutive weeks (W33–W37) carry no hand-entered figures.** That is the
  current truth and the design shows it rather than hiding it behind zeros.
- Entry happens in the daily note (`200-Daily/`) via the `today` skill, summed weekly.
  Slack prompts are being retired.
- `apps/piesson/**` mirrors to the **public** repo `Piesson/Piesson`. Working files
  live under `.impeccable/`, which is gitignored for that reason.
- Upstream Actions rewrite `README.md` and the dashboard SVGs on a schedule. Any design
  change lives in the generator, never in the committed output alone.

## Evidence

Every figure is real. PR counts come from `gh search`; hand-entered rows come from
`dashboard/data.json`. No illustrative or placeholder numbers appear on the surface.

## Accessibility

The artifact is an image inside a README. Screen readers reach only its `alt` text, so
the README must carry a text equivalent beside it. Contrast holds at 4.5:1 for figures
and labels. GitHub serves both light and dark themes; the artifact handles both.

## Open decisions

- Which of three visual directions is built (in review 2026-09-20).
- Whether the twelve-week table and the line chart both survive, or one artifact
  replaces them.
