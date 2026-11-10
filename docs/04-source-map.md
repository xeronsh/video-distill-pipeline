# 04 · Provenance: the SOURCE_MAP norm

Every project keeps one `SOURCE_MAP.md` at its root — the single source of
truth for *what the corpus is* and *where each piece came from*.

## Rules

1. **One row per item**: canonical ID ↔ mirror ID ↔ duration ↔ publish date
   ↔ acquisition status ↔ transcript status.
2. **Created before acquisition starts**, updated as each item lands —
   never reconstructed afterwards from filenames.
3. **Store originals, not summaries.** The map points at source artifacts
   (audio, captions); derived artifacts (transcripts, notes) reference the
   map, not each other.
4. **Unresolved = TODO, in the map.** "Probably episode 6" is not a mapping.
   If a match is uncertain, the row says so, and the item is treated as
   missing until proven otherwise.
5. **Method notes live at the bottom.** When a route took real work to find
   (an authenticated-download recipe, a mirror's naming quirk), write it
   into the map's method section while it is fresh. Future-you — and any
   agent continuing the project — will not rediscover it for free.

Blank template: [`templates/SOURCE_MAP.md`](../templates/SOURCE_MAP.md).

## Why bother

Twenty-item corpora fail quietly: one duplicated episode, one mislabeled
date, one "close enough" match, and the synthesis confidently cites the
wrong source for a year. The map is cheap insurance — an hour of bookkeeping
against a corpus you will query hundreds of times.
