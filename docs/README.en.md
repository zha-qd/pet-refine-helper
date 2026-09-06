# Pet Refine Helper | 宠物洗练助手

A Windows desktop assistant for the calibrated pet refinement screen. It reads values with OCR, clicks the game UI, verifies replacements against the saved stat values, and stops single-stat refinement at the cap. The application interface is in Chinese.

[中文说明](../README.md) · [Download releases](https://github.com/zha-qd/pet-refine-helper/releases)

## Quick start — portable Windows release

1. Download `pet-refine-helper-v1.0.0-windows-x64.zip` from Releases.
2. Extract the entire archive into a writable folder. Do not run inside the ZIP.
3. Double-click `start.bat`. Python and OCR models are included; a separate Python installation is not required.
4. Open the matching pet refinement screen in the game. Keep the window visible and unobstructed.
5. Enter the target window title. It intentionally starts empty. Click **检测窗口** (Detect window).
6. While stopped, click **校准** (Check coordinates) and observe where the pointer moves. This checks existing coordinates; it does not learn or change them.
7. Select the mode and stats, then click **开始洗炼** (Start) or press **F5**. Press **F5** again to stop.

The automatically generated GitHub **Source code** downloads do not include the runtime or models. Use the Windows ZIP for the ready-to-run package.

## Requirements and limitations

- Windows x64. The portable build uses Python 3.10, PaddleOCR 2.7.0.3 and PaddlePaddle 2.6.2.
- Only the calibrated portrait game layout is supported. Different layouts, scaling, title bars or DPI settings may require coordinate changes.
- The program captures the real desktop and controls the mouse. It does not support background or minimized windows.
- Do not move, resize or cover the game window while running. Avoid other mouse automation.
- Start with a small batch and compare the logs with the game before longer runs.
- Prefer ordinary user privileges. Window permission differences can affect input and capture.

## Controls

| Chinese label | Meaning |
| --- | --- |
| 游戏窗口 | Game window; enter an unambiguous title or substring |
| 检测窗口 | Detect position and size; uses the first matching window |
| 校准 | Move the pointer to the stored button coordinates; use only while stopped |
| 单洗 / 双洗 / 三洗 | Single / dual / triple-stat refinement |
| 点击间隔 | Delay after clicking; default 0.8 seconds |
| 动画等待 | Delay before reading changes; default 0.2 seconds |
| 开始洗炼 / 停止洗炼 | Start / stop |
| 调试模式 | Save change-region screenshots to `debug_img/` |
| 运行日志 | Per-round decisions, verification results and summary |

F5 is the only global shortcut. Holding it down does not repeatedly toggle. P, S and Escape have no assigned shortcut. Stop and wait for the summary before closing the window.

## Selection rules

Single mode accepts only a positive change to the selected stat. Zero and negative changes are rerolled. When no red/green change text is detected, the current version treats the value as unchanged.

Dual and triple modes accept a replacement when the **sum of selected changes is positive**. Individual selected stats may therefore decrease.

| Mode | Selected stats |
| --- | --- |
| 射手双洗 | Shield infantry health + archer penetration |
| 矛兵双洗 | Shield infantry health + spear infantry penetration |
| 射手三洗 | Shield infantry health + archer penetration + archer health |
| 矛兵三洗 | Shield infantry health + spear infantry health + spear infantry penetration |

Mode selection is captured when a run starts. Changing the dropdown during a run does not change that run. Do not recalibrate or change the target window while it is running.

## Replacement verification

The assistant reads `current%/cap%` and requires two consecutive identical reads. After clicking Replace and Confirm, it reads the saved stats again. Every selected stat must match the expected old value plus its change, capped at the maximum.

Example: `33.75%/44.69%` with `+0.12%` must become `33.87%/44.69%`. Values are compared at the displayed two-decimal precision. A bounded number of rereads allows for rendering delay.

If verification fails, the run stops and that replacement is excluded from the totals. The replacement may still have happened in the game; check the actual values before restarting. Screen-based verification cannot eliminate every OCR error or delay.

Single mode stops if the stat is already full before a roll, or reaches its cap after a verified replacement. Dual/triple modes do not stop merely because one selected stat is full.

## Stopping and totals

F5 prevents further refinement/reroll actions. If Replace has already opened its confirmation dialog, the assistant finishes that confirmation and its bounded verification reads before stopping. This can take several seconds.

The stop summary reports **positive increases from verified replacements**, per selected stat. Negative changes are not deducted, so this is not the final net gain in dual/triple mode. Rerolled and unverified results are excluded. A capped increase uses the actual saved increase, not the unclamped proposed change. Totals reset on each new run.

The counter bar still shows processed rounds, replacements, rerolls, OCR failures and replacement rate. OCR retries do not add rounds; OCR failures are counted per failed stat read.

## Troubleshooting

- **Will not start:** fully extract the ZIP and keep `runtime/` alongside `start.bat`. Read `logs/startup.log` or run `debug_run.bat` for console output.
- **Window not found:** enter a nonempty, specific part of the actual window title. Detection does not bring the window to the foreground.
- **Unstable total values:** check the screen, occlusion, aspect ratio and DPI. The run stops after bounded failed reads.
- **Repeated change OCR failures:** increase the delays and inspect debug screenshots. Missing red/green text is treated as zero, not an OCR failure.
- **Verification failed:** inspect the saved values and click positions. The assistant does not automatically repeat the replacement.
- **Coordinates are wrong:** see [coordinate reference](coordinates.md). Proportional scaling does not compensate for a rearranged UI.
- **F5 conflicts:** run only one instance and avoid other tools using F5. Wait for stop completion before restarting.

Startup logs are overwritten at each launch. Runtime log text is not automatically exported. Debug screenshots stay in `debug_img/`; review files before sharing a bug report.

## Running from source

Use Windows x64 Python 3.10:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe auto_refine_gui.py
```

The portable build is the tested dependency environment. Core versions are pinned in `requirements.txt`, but transitive dependencies in a fresh installation may change. See [runtime-packages.json](runtime-packages.json) for the installed portable inventory. Do not upgrade directly to PaddleOCR 3.x; its API differs.

Without `models/`, PaddleOCR may download its models and requires network access. Portable releases load `models/det`, `models/rec` and `models/cls` locally.

## Tests and validation

```powershell
runtime\python.exe tests\test_verification.py
runtime\python.exe tests\test_logs.py
```

Tests cover parsing, consecutive reads, mismatch stopping, initial/full cap behavior, clamped gains, all selection modes, positive-only accumulation and per-round logs. Five total-stat regions were also checked against two real game screenshots. The copied portable runtime and bundled models passed an offline GUI startup test with an empty default title.

This does not certify all emulators, DPI settings or long-running workloads. See [third-party notices](../THIRD_PARTY_NOTICES.md). No license has yet been selected for the project's own code; public availability does not grant unrestricted redistribution rights.
