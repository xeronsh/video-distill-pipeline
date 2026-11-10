# 03 · Distillation

Goal: turn 20 hours of transcripts into something a human (or an agent) can
actually use — per-episode notes for lookup, plus one synthesis for the
system as a whole. The distillation follows the Cangjie RIA-TV++ style flow,
run by the agent itself in single-Skill mode; no third-party summarization
API is involved, so no content leaves your own stack.

## Per-episode notes

One note per item, written from the transcript (never from the title or from
memory of other episodes). Fixed skeleton — see
[`templates/episode-note.md`](../templates/episode-note.md):

- **Context** — what the market/topic situation was when it was recorded
- **Core claims** — the principles stated, each with a timestamp
- **Cases** — every worked example, with the numbers as given
- **Rule increments** — what this episode *adds* to the system
- **Quotes** — the author's own formulations, verbatim, timestamped

Timestamps come from the `.segments.jsonl`; anchor every timestamp to a
keyword search of the segments so citations are checkable in seconds.

## Cross-episode synthesis

After all notes exist, write the synthesis (template:
[`templates/STRATEGY-skeleton.md`](../templates/STRATEGY-skeleton.md)):

- Organize by **topic, not by episode** — a system is a graph, not a playlist.
- **Every rule carries its citations** — episode IDs at minimum, timestamps
  for the load-bearing ones. A rule cited by two independent episodes is
  worth more than a rule stated once, loudly; say so when it happens.
- When episodes contradict each other (they will — authors evolve, contexts
  differ), record both positions with dates. Do not silently average them.
- Later corrections beat earlier statements for practice, but the earlier
  statement stays in the notes: you are building an archive, not a wiki of
  current truth.

## Gap honesty

Maintain an appendix in the synthesis: **missing material, uncertain
mappings, anything not yet distilled**. An item is either distilled or it is
in the appendix — there is no third state. When a gap is later closed, the
appendix entry is updated to say so (the history of the gap is part of the
archive's trustworthiness).

## The inventory audit

Before declaring the project done, reconcile three counts:

1. items in the SOURCE_MAP,
2. transcript pairs on disk,
3. notes on disk.

If the counts don't match, something was silently skipped — find it before
you write the completion report, not after. (In the validation run, this
audit caught one episode whose transcript existed but whose note was never
written and which the synthesis had never cited. The fix took an hour; the
lesson is now principle #5 in the README.)
