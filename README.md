# video-distill-pipeline

A field-tested pipeline for turning a **long-form video series** (10–20+ hours)
into a **queryable, citation-backed knowledge base**: full transcripts,
per-episode distilled notes, and one cross-episode synthesis where every rule
traces back to an episode and a timestamp.

Built for series you actually want to *interrogate* later — course lectures,
weekly review shows, conference talks, internal training recordings — not for
one-off video summaries.

> This repository contains the **method** (pipeline design, hard-won
> operational lessons, blank templates) plus **one worked case study**: the
> distilled outputs of the validation run, under `case-study/`. It contains
> no video files, no audio, and no verbatim transcripts. Bring your own
> corpus, and publish your own outputs wherever your rights allow.

## Pipeline

```
            ┌──────────────────── 1 · ACQUISITION ────────────────────┐
            │ subtitles first → mirror sources → original download    │
            │ (every item fingerprinted & logged in a SOURCE_MAP)     │
            └──────────────────────────┬──────────────────────────────┘
                                       ▼
            ┌──────────────────── 2 · TRANSCRIPTION ──────────────────┐
            │ parallel Whisper workers on rented GPU sessions       │
            │ (.txt + timestamped .segments.jsonl per item)         │
            └──────────────────────────┬──────────────────────────────┘
                                       ▼
            ┌──────────────────── 3 · DISTILLATION ───────────────────┐
            │ per-episode notes → cross-episode synthesis           │
            │ every rule cited: [episode, mm:ss]                    │
            └──────────────────────────┬──────────────────────────────┘
                                       ▼
                     Q&A over the corpus, answers with receipts
```

| Stage | Doc | What it covers |
|---|---|---|
| 1 · Acquisition | [docs/01-acquisition.md](docs/01-acquisition.md) | Source-routing ladder, session/cookie completeness, PO tokens, throttling & resume |
| 2 · Transcription | [docs/02-transcription.md](docs/02-transcription.md) | Parallel GPU workers, checkpointing, the reclaim trap, cost accounting |
| 3 · Distillation | [docs/03-distillation.md](docs/03-distillation.md) | Note structure, citation discipline, gap honesty, synthesis rules |
| 4 · Provenance | [docs/04-source-map.md](docs/04-source-map.md) | The SOURCE_MAP norm: one row per item, originals over summaries |

Templates live in [`templates/`](templates/); a checkpointed Whisper batch-job
skeleton lives in [`scripts/`](scripts/).

## Principles

1. **Subtitles before speech recognition.** Platform captions are free,
   instant, and exact. ASR is the fallback, not the default.
2. **Store originals, not summaries.** Summaries rot; transcripts can be
   re-distilled forever. Every derived artifact links back to a transcript,
   and every transcript to a source row.
3. **Citations or it didn't happen.** A distilled rule without an episode and
   timestamp is an opinion. The synthesis cites everything.
4. **Gaps are declared, never smoothed over.** Missing items go in an appendix
   as open TODOs. A pipeline that hides its holes will eventually fabricate.
5. **Audit the inventory, not the vibes.** Completion = file counts reconciled
   against the source map, not "the long ones are done". (This rule was added
   after an audit caught one silently skipped episode in a "finished" run.)
6. **Rented compute is a meter, not a machine.** GPU sessions are stopped the
   moment outputs are retrieved, and "zero active sessions" is verified, not
   assumed.

## Validated on

A 23-episode, ~20-hour weekly review series (no platform subtitles anywhere):

- 25 audio items acquired (mirrors + 2 originals recovered via the
  authenticated-download route in doc 01)
- 25 transcript pairs produced by 4 parallel Whisper (large-v3) workers,
  ≈ 11.6 GPU compute units total, all sessions verified stopped
- 24 per-episode notes + a 14-chapter cross-episode synthesis (~45 KB),
  every rule cited to episode and timestamp
- 2 acquisition gaps found, declared, and later closed; 1 distillation gap
  found by inventory audit and closed

The distilled outputs of that run are published as the worked example in
[`case-study/bit-langlang/`](case-study/bit-langlang/) — the full synthesis
and all episode notes, with citations intact. Transcripts and audio are not
included (transcripts are verbatim source text; audio exceeds repo limits).

## What this is not

- Not a downloader tool — acquisition uses stock open-source tooling
  (yt-dlp and friends); the value here is the routing, the failure modes,
  and the discipline around them.
- Not a summary generator — the point is a *durable, auditable* knowledge
  base, built once and queried many times.

## License

MIT — see [LICENSE](LICENSE). The method and templates are free to use;
content you process with them is yours (and its original creators') problem.
