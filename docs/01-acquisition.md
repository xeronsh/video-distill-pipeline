# 01 · Acquisition

Goal: one audio (or video) file per series item, logged in the SOURCE_MAP,
obtained by the cheapest reliable route. Work the ladder top-down; only
descend when a rung actually fails.

## The ladder

### Rung 1 — Platform subtitles

Check for human or auto captions first, on every platform that carries the
series. If they exist, you may not need ASR at all. Download them with the
series metadata (episode order, publish dates) — you will need dates and
durations as fingerprints for rung 2.

### Rung 2 — Mirror / re-upload sources

Popular series are usually re-uploaded to other platforms (in our validation
run: a complete mirror on a second video site, found by searching the series
title + uploader). Match mirror items to canonical episodes by
**publish date + duration (±1 min)** — titles alone lie. Log every match in
the SOURCE_MAP with both IDs. Expect ~90–95% coverage; the residue goes to
rung 3.

### Rung 3 — Original download with an authenticated session

For the items only the original platform has. Stock `yt-dlp` plus a logged-in
browser session *can* work, but four failure modes ate a full evening before
the recipe below was pinned down. All four are about the session being less
complete than it looks:

1. **A login-state cookie jar is not a viewing session.**
   Exporting cookies from a browser that has only ever *logged in* (never
   opened the target site) yields a jar missing the site's own session
   cookies (visitor/session identifiers the player expects). Symptom:
   extraction "succeeds" but formats are empty or age/session-gated.
   **Fix:** open one watch page in that browser, let it sit ~15 s so the
   player fully initializes, *then* export cookies. The jar roughly doubles.

2. **Signature challenges need a JS runtime.**
   Modern extraction needs a JavaScript challenge solver: install the
   `yt-dlp-ejs` companion and pass `--js-runtimes node` (or deno).

3. **Media URLs are token-bound (PO Token).**
   Even with perfect cookies, media segment URLs return 403 without a
   proof-of-origin token. Use a token provider server
   (`bgutil-ytdlp-pot-provider`, self-hosted, one port) — and note the trap:
   **the visitor data used to mint tokens must be the live page's config
   value** (read from the running page, e.g. via CDP
   `ytcfg.get('VISITOR_DATA')`), which is a long opaque string. The similarly
   named cookie holds a short unrelated value and mints worthless tokens.
   Token binding also means you cannot mint externally and inject with
   `--extractor-args` reliably — let the provider plugin do it inside the
   same run, against the same session.

4. **Extraction ≠ download.**
   With tokens in place, yt-dlp's built-in downloader can still 403 on DASH
   formats while a plain `curl` against the same URL returns 206. Add
   `--external-downloader curl`. If a client profile
   (`--extractor-args youtubepot-webpo…` etc.) yields no formats, fall back
   to the default client set rather than cycling exotic clients.

Finally: the CDN throttles authenticated downloads hard (~30 KB/s observed).
Run downloads **detached** (`nohup … &`, log to file), and keep
`--continue` on — interrupted runs resume cleanly, including at 99%.

## Rules

- Prefer downloading from a network the account normally lives on (the
  account's home connection), not a datacenter IP.
- One SOURCE_MAP row per item *before* downloading anything.
- Audio-only (`-f bestaudio`) is enough when ASR is the next stage — it is
  ~10× smaller and the whole archive stays manageable.
