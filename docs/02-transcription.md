# 02 · Transcription

Goal: a `.txt` plus a timestamped `.segments.jsonl` per item, produced fast,
cheaply, and without babysitting — on rented GPU sessions (Colab-class).

## Setup that worked

- Engine: **openai-whisper, large-v3**, fp16, `language` pinned,
  `condition_on_previous_text=False` (long noisy recordings drift less).
  (faster-whisper/CTranslate2 builds fought the host CUDA image; the
  reference implementation just worked. Boring wins.)
- One worker session per GPU instance; N instances in parallel, each running
  a simple queue script under `tmux` so the job survives console disconnects.
- Each job writes **two** artifacts: plain text for reading, and a segments
  file (`{start, end, text}` JSONL) — the segments file is what makes
  mm:ss citations possible later. Never skip it.

## Checkpointing

The job script is **skip-if-done**: before transcribing an item it checks for
an existing output and moves on. Sessions die, quotas bite, networks flap —
with checkpointing, every failure costs minutes, not the run.

Skeleton: [`scripts/whisper_job_template.py`](../scripts/whisper_job_template.py).

## The reclaim trap (read this twice)

Rented notebook sessions are reclaimed when the *kernel looks idle* — and a
tmux job chewing through a 40-minute file can look exactly like that.
Observed loss: a finished transcript, sitting unretrieved in a session that
was reclaimed during a later job's wait loop. It had to be re-transcribed.

**Rule: download each output the moment it exists.** Never let finished
transcripts accumulate inside a rented session. Pull → verify size → only
then queue more work.

## Cost & shutdown discipline

- Parallelism is worth it: the validation run did ~20 hours of audio across
  4 concurrent sessions; total ≈ 11.6 compute units for the whole series.
- When the queue drains: stop **every** session and verify with the
  provider's own listing that active assignments = 0, and record the
  remaining balance in the project README. "I stopped them" is a claim;
  the listing is the evidence.
