# 05 · Keyframe screenshots

Text-only distillation loses the actual charts. For any series where the
speaker works on a visual canvas (charts, slides, code), capture **keyframes
at the exact moments your notes cite** and embed them in the notes.

## Method: seek-and-shoot in a logged-in player

Don't download whole videos for a handful of frames. Drive the platform's
own player in an already logged-in browser session (CDP):

1. Open the watch page in a fresh tab; set a wide viewport, theater mode,
   and pin the playback quality (e.g. hd1080).
2. For each anchor timestamp: seek, wait for `seeked` + `readyState >= 3`,
   let the controls fade (~2.5 s), then screenshot **clipped to the video
   element's bounding rect** — pure frame, no page chrome.
3. Anchor selection: timestamps already cited in your episode notes first;
   for un-timestamped notes, locate case discussions by searching the
   segment file for the case's name/ticker and shoot first-mention + ~10 s.
4. QA every frame visually (contact sheets). Expect ~8% duds; re-shoot or
   drop them. A note with 3–6 verified frames beats 10 unreviewed ones.

Reference implementation: [`scripts/seek_and_shoot.mjs`](../scripts/seek_and_shoot.mjs)
(Node ≥ 22, no dependencies — global `WebSocket` + the DevTools HTTP API).

## Failure modes (all observed in the validation run)

- **Cold-start stall.** Some videos sit at `readyState 0` forever on a cold
  open. Warm start helps: open the URL with `&t=<first-anchor>s`, and nudge
  with a synthetic click on the player + `play()` every few seconds until
  the media engages. A video that stalls once may still succeed standalone —
  retry flaky items individually, not in a batch chain.
- **Seeks trigger mid-roll ads.** An ad can start *after* your pre-seek ad
  check. Re-check for the ad state right before capturing; if an ad is
  showing, wait it out and **re-seek** (the ad replaces the media element's
  timeline). Capturing during an ad yields an ad frame — or, worse, a blank
  page frame when the clip rect is computed against the swapped layout.
- **Episode tails are BGM, not content.** Anchors in the last ~5% of an
  episode frequently land on the speaker's break/desktop/music screen.
  Prefer anchors before the outro; if a fix attempt lands on the same break
  twice, drop the slot — the note survives with one fewer frame.
- **Overlays are source material.** Chat popups and drawing layers burned
  into the original recording are not capture artifacts. Keep them; they're
  evidence of the live context.
- **Detached batches need real detachment.** A `nohup &` child launched
  through a remote-exec channel can still die with the channel's process
  group. Use `setsid` + full fd redirection, and make the runner
  skip-if-done per episode so a relaunch resumes instead of restarting.
