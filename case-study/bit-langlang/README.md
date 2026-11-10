> **Case-study copy** for [video-distill-pipeline](https://github.com/xeronsh/video-distill-pipeline) — distilled outputs (synthesis + episode notes + source map + keyframe screenshots). Transcripts and audio are **not** published here: transcripts are verbatim source text and audio exceeds GitHub limits; both live in the private knowledge base and its Drive backup.

# Bit浪浪交易复盘全集 · 蒸馏项目

来源：YouTube 播放列表 PLv62PVNSGzGD2614LkngWETWL-fZebdja（23 集 / 19.99h，2023-10-28 → 2024-06-01）
获取路线与逐集映射见 `SOURCE_MAP.md`（Bilibili 中山公爵同系列搬运，日期+时长双匹配 22/23）。

## 目录
- `audio/` — 全量音频存档（m4a，B站 64kbps 流；ThinkPad ~/muse-workspace/bitlang/audio/ 为原始全集）
- `transcripts/` — Colab L4 openai-whisper large-v3（torch fp16）转写：`<集号>.txt` + `<集号>.segments.jsonl`（带时间戳）
- `episodes/` — 逐集解读（每集一文件：本集行情背景 / 核心观点 / 操作与交割 / 规则增量 / 金句原文）
- `STRATEGY.md` — 跨集汇总的合约交易策略总纲（所有规则标注出处集数）
- 信号提醒：用户 2026-11-09 拍板「先只做策略蒸馏，信号提醒之后再说」——未落地，重启时以 DerivScope 为数据层另行设计

## 管线状态（2026-11-09 深夜，收尾）
- [x] 播放列表盘点：23 集 / 19.99h；确认无平台字幕、无自动字幕
- [x] 路线突破：VM 出口被 YouTube 机器人墙（含 cookies+PO Token 均失败）→ B站「中山公爵」同系列搬运，ThinkPad 家宽 yt-dlp 下载音频 23 文件 / 558MB，本地存档 23/23 完成
- [x] Colab 音频就位（上传 ~2MB/s；Colab 直连 B站 CDN 只有 140KiB/s 且断流，不可用）
- [x] Colab 转写 **全部完成**：引擎 = openai-whisper large-v3（torch，fp16，condition_on_previous_text=False）。faster-whisper/CTranslate2 在该 Colab 镜像（CUDA 13 + py3.13）有 cublas12/驱动冲突，弃用。四机并发跑完 22 个队列项，转写稿 23 文件全量回收至 `transcripts/`。**全部 Colab 会话已停，验证 Active assignments: 0**；全程 CU 消耗约 9.7（2489.27 → 2479.57）
- [x] 逐集蒸馏 **全集完成**（`episodes/` 共 24 篇：22 集正片 + 12b 大群 + extra；ep23 短片按设计跳过；ep06 笔记 2026-11-10 盘点时发现漏写并补齐）；STRATEGY.md 约 44.6KB，14 章，规则全标注出处集数
- [x] 关键 K 线截图层（2026-11-10 补）：按用户要求以 **YouTube 原版为优先源**，在 ThinkPad 登录会话的播放器里逐锚点实拍（`frames/`，22 集共 **95 张**），逐张看图筛选后嵌入各集笔记文末「关键截图」节（锚点=笔记时间戳或案例币种定位；剔除广告帧/桌面/片尾 BGM 帧 8 张，EP04 一处锚点因该视频反复冷启停滞未补、保留 4 张）。12b/extra 为 B 站独有材料，未拍。
- [x] ep07（20231209）已补齐（2026-11-10）：YouTube 原版路线打通（登录完整会话 + PO Token + yt-dlp 外置 curl，方法学见 SOURCE_MAP 文末），音频/转写（1460 段）/笔记/STRATEGY 增补全部落地
- [x] ep10 已补齐（2026-11-10）：查明本集为大群段（B 站拷贝）+ 小群段（YT 原版 42.3min）两段独立录像，小群段同路线补下转写（822 段），笔记合并为「小群段补遗」，STRATEGY §5/§8/§9/§13 已增补。**至此全集 23 集 + 2 补充全部齐备，无未决缺口**；补缺 Colab 两会话均已停、验证 Active assignments: 0（余额 2477.64 CU）
- [ ] （可选）Gemini Ultra 读关键帧/图表：仅图表密集段需要时再做

## 问答方式
蒸馏完成后，直接在对话里问（如「浪浪怎么处理假突破」），回答从本目录 transcripts/episodes/STRATEGY.md 取证并标注集数与时间戳，不凭记忆编。
