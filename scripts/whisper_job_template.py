"""Checkpointed batch transcription job (Whisper large-v3).

Runs inside a rented GPU session (e.g. under tmux). Design rules:
- skip-if-done: existing outputs are never recomputed;
- two artifacts per item: <label>.txt and <label>.segments.jsonl;
- download outputs to durable storage IMMEDIATELY after the run —
  rented sessions get reclaimed while the kernel looks idle.

Usage: fill in ITEMS (label -> audio path), then `python whisper_job_template.py`.
"""
import json
import os

import torch
import whisper

AUDIO_DIR = "/content/audio"          # where acquisition landed the files
OUT_DIR = "/content/out"               # retrieved to durable storage after run
MODEL = "large-v3"
LANGUAGE = "zh"                        # pin it; auto-detect wastes the head

ITEMS = {
    # "01-20240101": "01-20240101.m4a",
}


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    todo = {
        label: fn for label, fn in ITEMS.items()
        if not os.path.exists(os.path.join(OUT_DIR, label + ".txt"))
    }
    print(f"total={len(ITEMS)} todo={len(todo)}", flush=True)
    if not todo:
        return
    model = whisper.load_model(MODEL, device="cuda")
    for label, fn in todo.items():
        path = os.path.join(AUDIO_DIR, fn)
        res = model.transcribe(
            path,
            language=LANGUAGE,
            fp16=True,
            condition_on_previous_text=False,
            verbose=False,
        )
        with open(os.path.join(OUT_DIR, label + ".txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(s["text"].strip() for s in res["segments"]))
        with open(os.path.join(OUT_DIR, label + ".segments.jsonl"), "w", encoding="utf-8") as f:
            for s in res["segments"]:
                f.write(json.dumps(
                    {"start": s["start"], "end": s["end"], "text": s["text"].strip()},
                    ensure_ascii=False) + "\n")
        print(f"done {label}: {len(res['segments'])} segments", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
