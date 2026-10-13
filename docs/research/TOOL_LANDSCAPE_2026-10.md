# R2 — Generation & production tool landscape (as of 2026-10-13)

**Evidence key:** V = read on a vendor/primary page this session; sec = third-party page only; U = UNVERIFIED. [Sn] = source list at end (page dates where shown; all fetched 2026-10-13). WebSearch quota ran out mid-run, so some items stay sec/U. Prices USD.

## 0. Facts most likely to change the architecture
1. **Sora is dead:** app off 2026-04-26, API off 2026-09-24 [S1].
2. **Licence traps (legal grey area, flag to owner):** HunyuanVideo 1.5 licence does not apply in EU/UK/South Korea, outputs included [S38]. MiniMax H3 card requires an application for USA/EU/UK/KR; secondary sources read it as exclusion [S39]. Qwen-Image 2.1 is research-licence only [S61]. A France-based studio should standardise on Wan 2.2 (Apache-2.0) and LTX-2.5 (free under $10M revenue).
3. **bpy wheels:** Python ==3.13, Linux x86_64 only, no aarch64 [S52]. Run Blender on x64 runners (public repo: 4 vCPU/16 GB/14 GB SSD, no GPU, 6 h/job) [S47].
4. **Oracle Always Free A1 halved** to 2 OCPU/12 GB (2026-06-15, unannounced) [S46].
5. **Grok Imagine API** is billed separately from SuperGrok and is priced at the low end of closed video ($0.14/s at 720p; lite $0.03/s) [S8,S9,S11]. No closed model has a free API tier [S2]; Grok free generation ended March 2026 (sec) [S16].
6. **CI can run Claude on a subscription token** or API key [S65]; Haiku 5.5 costs $0.10/$0.50 per MTok.
7. `gemini-2.5-flash-image` was due to shut down 2026-10-02; successors take up to 14 references [S2,S6].
8. UE 5.8 ships an experimental MCP plugin for Claude [S57].

## A. Closed AI video
| Model | Clip / res / audio | Control (I2V, first-last, extend, refs) | V2V / motion / lip-sync | Price, API |
|---|---|---|---|---|
| **Veo 3.1** (+Fast, Lite; preview ids) | 4/6/8 s; 720p, 1080p/4K only at 8 s; 24 fps; audio always on [S3] | I2V; first+last; up to 3 refs (3.1/Fast); extend +7 s x20 to 148 s at 720p (3.1/Fast); Lite is T2V/I2V only | V2V on 3.1/Fast; SynthID; 11 s-6 min latency | sec 2026-09-11: Std $0.40/s (4K $0.60), Fast $0.10-0.30, Lite $0.05-0.08 [S4]; absent from Google's page, so U [S2]. Runway resale 3.1 $0.40 audio/$0.20 silent [S20]. API yes |
| **Gemini Omni 1.1 Flash** (replaces Veo 3.1 in Gemini app) | 10 s in app; native audio [S5] | text, up to 5 photos, video in; scene extension | V2V edit, multi-turn edit [S5] | API ~$0.10/s at 720p ($17.50/M output tokens), no free tier [S2]. Runway 360p $0.034 to 4K $0.30/s [S20] |
| **Sora 2** | discontinued [S1] | | | |
| **Kling 3.0** (2026-02-05) / O3 Omni | 3-15 s; std 720p, pro 1080p, 4K; audio optional, multilingual speech [S22,S23] | start/end frame; multi-shot (<=512 chars/beat); O3 refs up to 7 images + video [S26] | O3 video edit; lip-synced speech claimed [S23]; motion control U | API sec: 3.0 $0.18-0.35/s (4K $0.44) [S23]; O3 $0.084-0.112/s [S26]. Plans $8.80-$159.99/mo; free watermarked, commercial needs paid [S25] |
| **Kling 4.0** (announced 2026-09-27) | 3-30 s, 4K, 10 keyframes, 15 refs [S24] | | | "full launch October", API "soon"; not confirmed live (U) |
| **Runway Gen-4.5 / Aleph 2.0** | Gen-4.5 5/10 s; API 720p [S20,S28]; audio U | I2V | Aleph 2.0 (editing line, details U); Act-Two performance capture | Gen-4.5 $0.12/s, Aleph 2.0 $0.28/s, Act-Two $0.05/s; no Gen-5 [S20]. Plans $15/$35/$95 [S21]. API yes; resells Veo, Seedance, Wan 3, Hailuo 3, Grok, Omni |
| **Luma Ray3.2** | 5/10 s, 360-1080p, 16-bit HDR/EXR (2x/3x credits); no audio on T2V/I2V [S27] | up to 16 keyframes | Modify Video V2V to 20 s, performance tracking, 8 faces | sec $0.15-$1.20 per 5 s [S28]; plans $30/$90/$300. API yes |
| **MiniMax Hailuo 3 / H3** (2026-07-31) | 4-15 s, 2K via API, native stereo audio [S29] | ref images, keyframes, ref video | | sec $0.13/s 2K [S29]; Runway 768p $0.10, 2K $0.15 [S20]. Weights: see B |
| **Seedance 2.0 / 2.5** | 2.0: 15 s, to 4K; 2.5: 30 s extendable, 1080p; native audio [S30] | refs 2.0: 12 (9 img/3 vid/3 audio); 2.5: 50 (30/10/10); first+last [S31] | | BytePlus $/s 2.0: 0.07/0.15/0.37/0.78 (480p-4K); 2.5: 0.103/0.231/0.569 [S30]. API yes |
| **Pika 2.5** | ~5-10 s, Pikaframes 25 s [S32] | | | $8/$28 per mo, API Club $10/mo; third-party site, U |
| **Midjourney V8.2 video** | image-to-video only; 5 s +4 s per extend to 21 s; 480p, 720p on Standard+ [S33] | | | $10/$30/$60/$120 per mo; no API (roadmap) |

**Grok Imagine (xAI primary unless marked):**
- **Models:** `grok-imagine-video-1.5`, `-lite`, `grok-imagine-video` (edit/extend/classic refs), `grok-imagine-image-2.0` [S7,S10]. Video 1.5 launched 2026-06-16, References 07-31, Image 2.0 08-07 [S13].
- **Video:** 1-15 s (default 8); 480/720/1080p (1080p native for T2V/I2V; reference mode <=720p); audio on by default with lip-synced speech; `last_frame` plus up to 4 `keyframes`; reference-to-video up to **14 reference images** and **3 preset voices** (own-audio voices on request); edits capped 8.7 s/720p; aspect ratios to 21:9 [S7,S11,S13]. Fast mode: 6 s 720p in ~25 s (xAI claim) [S13].
- **API price/s:** 1.5 = $0.08/0.14/0.25 (480/720/1080p) +$0.01 per image/video input; lite = $0.02/0.03/0.14 [S8,S9]. Image 2.0 = $0.04 (1K low) to $0.08 (2K medium), +$0.01 per input image; n<=10; editing up to 5 images [S10,S12,S13]. Limits 10 req/s video, 6 req/s image.
- **Consumer tiers:** x.ai lists only Free and SuperGrok, no prices or caps [S14]. Third-party (2026-09-27): Lite $10, SuperGrok $30 (720p), Plus $100 (1080p), Heavy $300 [S15]; Lite ~15 videos/day, 480p, 6 s (Jul) [S17]. xAI publishes no per-tier caps; community estimate ~240 video attempts/month at $30 [S16]. Image/voice references launched first for Heavy and Plus [S13]. Heavy adds usage, priority, multi-agent, X Premium+, Build Mode beta [S13,S15]; no Imagine feature exclusive to Heavy found (U).
- **Imagine Agent:** beta since ~2026-04-30; web-only canvas, paid accounts; drafts a scenario, generates scene clips, stitches (one-minute film example); opened gradually to SuperGrok/Heavy [S18,S19]. No agent API found (U).
- **Flag:** browser-automating grok.com to burn subscription quota is likely a ToS problem (U); use the API.

## B. Open-weight video
| Model | Licence | VRAM / CPU | Length, res, audio, I2V |
|---|---|---|---|
| **Wan 2.2** (2025-07; newest downloadable Wan; 2.5-3.0 API-only [S34]) | Apache-2.0 | TI2V-5B: >=24 GB single-GPU command, "<9 min" for 5 s 720p on one consumer GPU; A14B >=80 GB (offload flags); community fp8/GGUF [S35] | 720p/24 fps; no native audio; I2V; S2V-14B, Animate-14B; Wan-Dancer/Animate-2 (Apache, Jul-Aug 2026) [S34] |
| **LTX-2.5** (22B; 2.3 Mar 2026) | LTX-2.x Community: free <$10M group revenue [S36] | Official INT8/NVFP4 24 GB+; community GGUF Q3_K_S 12.65 GB, Q4_K_M 15.69 GB for 16 GB cards [S37]; ComfyUI node says 32 GB+ | Synced audio+video, multishot, T2V/I2V/V2V/A2V, IC-LoRAs, 24 fps, 1080p, 4K via upscaler [S36]; LTX-2.3 720p ~5-8 min on RTX 5090 (sec) [S41] |
| **HunyuanVideo 1.5** (8.3B, 2025-11-20) | Tencent Community; **EU/UK/South Korea excluded**, 100M MAU cap [S38] | 14 GB with offload | 480/720p + SR to 1080p; 121 frames; I2V; no audio listed |
| **MiniMax H3** (weights 2026-08-02; 33B) | Community: commercial under $20M revenue, attribution; US/EU/UK/KR need authorisation [S39] | 42.5 GB smallest set; 12 GB with ComfyUI offload + 64 GB RAM (sec) | 768p local (2K needs hosted module), 4-15 s, native stereo audio |
| Kandinsky 5.0 (2B/19B), Mochi 1 (10B), CogVideoX, Allegro | MIT repo / Apache / CogVideoX licence / Apache [S40] | Mochi ~80 GB reference | Kandinsky <=10 s; no audio |
| SkyReels, LongCat-Video, HappyHorse 1.0 (Alibaba) | U | U | HappyHorse press release claims open-source #1; OpenRouter lists API only |

**Free runtimes:** Kaggle P100 or 2x T4 16 GB, ~30 GPU-h/week typical, 12 h sessions [S43]; Colab free <=12 h, GPU unspecified (T4 reported) [S50]; ZeroGPU 5 min/day free, PRO $9/mo = 40 min, RTX Pro 6000 Blackwell 48 GB [S44]; Modal $30/mo [S45]. **Seconds per 5 s clip on a T4: no published figure (U).** T4 lacks bf16/fp8; expect LTX-2.5 GGUF to need CPU offload and tens of minutes; Wan 2.1 1.3B (~8 GB) fits [S40]. CPU-only video: not viable (U).
**Best free AI-video path:** Kaggle 2x T4 with Wan 2.2 5B or LTX-2.5 GGUF (speed U); ZeroGPU Spaces for hosted demos; then pay-per-clip (Grok lite, 6 s 720p, about $0.19 incl. input).

## C. Image models (keyframes, sheets, backgrounds)
| Model | Facts |
|---|---|
| **Nano Banana 2.1** `gemini-nano-banana-2.1` | 1K/2K/4K; <=14 refs (10 objects + 4 characters) [S6]; ~$0.034/0.050/0.113 per 1K/2K/4K [S2] |
| Nano Banana 2 / 2 Lite / **Pro** | `gemini-3.1-flash-image` ~$0.067 (1K); `gemini-3.1-flash-lite-image` ~$0.034 (1K); `gemini-3-pro-image` <=14 refs (6 obj, 5 char, 3 style), $0.134 (1K/2K), $0.24 (4K) [S2,S6]. SynthID on all. Free tier: only 3.1 Flash Image in AI Studio. Imagen shut down |
| **GPT Image 2** | sec 2026-09-06: $0.006/0.053/0.211 per 1024^2 low/med/high; Batch -50% [S61]. "2.5" ids appear only in Runway docs (U) |
| **FLUX** | FLUX 3 Image 2026-10-01 (API, <=10 refs, weights not announced); FLUX.2 pro <=8 refs, max <=10; klein 4B Apache-2.0 ~13 GB; klein 9B and dev (32B) non-commercial; no 2026 Kontext [S61] |
| **Midjourney V8.2** | Edit model (testing since 08-27) replaces Omni/Character Reference, <=4 refs; no API [S33] |
| **Grok Imagine Image 2.0** | text layout, <=5 refs, background removal [S12,S13] |
| **Qwen-Image 2.1** (7B, 2026-09-21) | <=10 refs, native RGBA, ~24 GB+; **research licence** [S61]. Qwen-Image-Edit-2511 (20B) Apache-2.0 |
| Seedream 5, Ideogram 4.5 | via Runway $0.04-0.09 and $0.01-0.25 per image [S20]; otherwise U |
| HunyuanImage 3.0 (80B MoE) | Tencent Community (territory terms U); Instruct 2026-01-26, <=3 input images [S61] |
| **Z-Image-Turbo** (6B) | Apache-2.0, 8 NFE, fits 16 GB; no CPU timing published; Edit "to be released" at last check [S61] |

**CPU (i7-12700, OpenVINO) [S61]:** SD-Turbo 512^2 1 step 5 s (1.7 s with tiny decoder); SDXL-Turbo 5.6 s; FLUX.1-schnell 512^2 3 steps ~4.5 min (int4). stable-diffusion.cpp lists a CPU backend (AVX/AVX2/AVX512) and SD-Turbo, FLUX, FLUX.2 klein, Z-Image, Qwen-Image 2.1, Wan; speeds unpublished. Cloudflare Workers AI free 10,000 neurons/day includes flux-1-schnell [S49].

## D. Audio
**TTS**
- **ElevenLabs** API per 1K chars: v4 $0.08, v4 Turbo/Flash $0.04, v3 $0.08; plans $6/$22/$99/$299/$990 [S62]. Runway resells v4 at 5 cr/1K chars ($0.05) after the 2026-10-12 promo [S20].
- **Gemini TTS** `gemini-3.8-flash-tts` $0.50/M text in, $9/M audio out, free tier; doubles 2027-01-01 [S2]. OpenAI TTS: U.
- **Open:** Kokoro-82M Apache-2.0, CPU-usable, ~80 MB quantized ONNX, no cloning [S62]. Chatterbox MIT, 0.5B, zero-shot cloning, 25 languages (v3). Qwen3-TTS Apache-2.0, 0.6B/1.7B, 3 s cloning, VoiceDesign, 10 languages (2026-01-22). Dia Apache-2.0, 1.6B, two-speaker tags, ~4.4 GB, no CPU yet. Higgs Audio v3 (2026): licence U. VibeVoice MIT, but TTS code pulled 2025-09-05 with a "not for commercial use" advisory. **Non-commercial:** Fish S2 weights, F5-TTS weights, XTTS v2 [S62].

**Music**
- **Suno v6:** Free (v6-mini) no downloads, no commercial; Pro $8 (20 downloads/mo); Premier $24 (60/mo, Studio); commercial rights only on paid downloads; new ToS 2026-09-03 [S62].
- **Udio:** downloads disabled on all plans since 2025-10-29 (label settlements); unusable as an asset source (sec) [S62].
- **Lyria 3.5** (`lyria-3.5`, ~2 min, vocals, 44.1 kHz) and Lyria 3 Clip (30 s) in the Gemini API, SynthID; no price on doc page [S62]. ElevenLabs Music $0.15/min, 5 min cap, commercial on Starter+ [S62].
- **Open:** ACE-Step 1.5 MIT, <4 GB VRAM, up to 10 min, ~2 s/song on A100, CPU listed but untimed. YuE Apache-2.0, 360 s per 30 s on a 4090. Stable Audio Open 1.0: Stability Community Licence, <=47 s, better at SFX than music [S62]. MusicGen weights CC-BY-NC, HeartMuLa: U.

**SFX:** ElevenLabs SFX $0.12/min; MMAudio code MIT, **weights CC-BY-NC**, ~6 GB, 8 s clips; HunyuanVideo-Foley 8-20 GB, 48 kHz, licence terms not shown (U); **ThinkSound: commercial use not permitted**; AudioX U [S62]. Procedural foley (filtered-noise beds, CC0 Freesound, FluidSynth): U.

**Lip-sync:** LatentSync 1.6 Apache-2.0, 512^2, 18 GB (1.5: 8 GB). MuseTalk 1.5 256^2 face, 30 fps+ on V100, licence not shown. InfiniteTalk Apache-2.0, Wan2.1-14B base, dubbing or image+audio, ~1 min. Sync Labs lipsync-2 $0.05/s, lipsync-2-pro $0.083/s, plans $5-$249 [S63]. Native: Kling, Grok 1.5, Seedance, H3. Hedra, OmniHuman-1.5, Wav2Lip: U. **Rhubarb Lip Sync** (CPU CLI, Win/macOS/Linux): 6-9 mouth shapes, TSV/XML/JSON/Moho dat, exporters for After Effects, Spine, Moho, OpenToonz; English or language-independent phonetic mode; licence not shown (U) [S63]. Only Rhubarb, Kokoro and (slowly) ACE-Step are CPU-practical.

## E. Finishing
| Task | Tool |
|---|---|
| Upscale | Topaz Video $59/mo desktop, web $19-29/mo [S64]; also in Runway Pro/Max [S21]. SeedVR2 Apache-2.0, one-step, reference 1x H100-80G for 100 frames 720x1280 [S64]. Magnific video upscaler via Runway $0.007/frame at 720p [S20]. Real-ESRGAN, STAR: U |
| Interpolation | Practical-RIFE 4.26 (4.25 recommended), MIT, `--scale 0.5` for 4K, CPU undocumented [S64]. Runway `enhance_frame_rate` 1 cr/2 s [S20]. FILM: U |
| Depth | Depth Anything 3 (2025-11-14): Small/Base Apache-2.0; Large/Giant/Nested CC-BY-NC; Streaming <12 GB for long video [S64]. DA V2, Marigold: U |
| Segmentation | SAM 3 (848M, SAM Licence, 3.1 on 2026-03-27, text prompts + video tracking, CUDA 12.6+, gated checkpoints) [S64] |
| Matting | BiRefNet MIT, 3.5 GB FP16 at 1024^2, 17 fps on 4090, GPU-benchmarked only [S64]. RMBG-2.0 licence: U |
| Colour | OpenColorIO BSD-3, ACES configs [S64]; Blender 5.0+ ACEScg and HDR/wide-gamut export [S51]; Luma EXR ACES2065-1 [S27]. Permissive LUT libraries, halation/grain tools: U (build with OCIO + ffmpeg) |

## F. Procedural / animation tooling
| Tool (version) | Price / OS | Headless / CI | Role |
|---|---|---|---|
| **Blender 5.2.2 LTS** (2026-09-15; 5.2 LTS 07-14, fixes to 07-2028) [S51] | GPL, free; Win x64/ARM, macOS arm64, Linux x64 | `bpy` 5.2.2 (Py 3.13, x64 Linux 401.7 MB); 4.5 LTS bpy still shipped (4.5.14) [S52]. Cycles CPU fine; EEVEE needs GL/Vulkan, software GL slow (U); no Linux ARM build/wheel | 3D, NPR line art, Cycles. 5.2: EEVEE 2x faster instance scenes, Grease Pencil Delaunay fill, render-time strokes [S51]; Vulkan default status U |
| Blender add-ons | Rigify (bundled, U), Auto-Rig Pro (paid, U), Rokoko (U), Freestyle (built-in) | | Mixamo: free with Adobe ID, humanoids only, commercial use per FAQ summary [S60] |
| **Three.js r186** (24 Sep) [S54] | MIT (U), browser | Needs a browser. Remotion `--gl=swangle` (ANGLE+SwiftShader) is the documented no-GPU route, default on Lambda; slow; `angle` fails on GitHub runners in Remotion 4.0 and becomes default in 5.0 [S55]. Playwright flags: U | WebGPU/TSL renderer; 3D scenes |
| **Remotion 4.0.535** (2026-10-12) [S55] | Free <=3 people; Company: Creators $25/seat/mo, Automators $0.01/render ($100/mo min); Enterprise from $500/mo | `npx remotion render` on headless Chrome; Lambda 1-min video ~$0.02, 10-min HD ~$0.10 | Compositing/titles. **Official agent skills** `npx skills add remotion-dev/skills` (12 skills incl. create, render, captions); no MCP |
| Motion Canvas / Revideo / Manim CE | MIT / MIT / v0.21.0, Py>=3.11 [S59] | Revideo: headless render API, parallel workers; Motion Canvas U | Vector motion, math |
| Rive / Spine / Cavalry / Live2D / Cascadeur | Rive free with splash, $9-$32/seat; Spine Essential $69-99, Pro $379-449; Cavalry free, macOS/Windows; Live2D 42-day PRO trial, price U; Cascadeur free non-commercial, Indie $19/mo ($8 annual), Pro $49/mo [S60] | none documented | 2D rigs, mocap-style animation |
| **Godot 4.7.2** (2026-08-18) [S56] | MIT (U) | `--write-movie out.avi --fixed-fps 30`; AVI-MJPEG (4 GB cap), PNG+WAV; `--headless` compatibility undocumented (U) | Real-time cinematic renderer |
| **Unreal 5.8** (June 2026; last UE5 major) [S57] | Free below $1M revenue, 5% above (games; film/TV not addressed). Unity 6 Personal free <$200K [S58] | Heavy; U | MetaHuman Animator, Movie Render Graph |
| **ComfyUI** (GPL-3.0, releases ~2 weeks) [S42] | Win/Linux/macOS | local API; "4 GB VRAM + 8 GB RAM" claim; `--cpu` U | Hub. Nodes: Kijai WanVideoWrapper (Apache, fp8/GGUF/block swap, VACE, Animate), Lightricks LTXVideo (IC-LoRA). IPAdapter/PuLID: U. Krita AI Diffusion (GPL-3.0; Flux 2, Z-Image, ControlNet pose/depth) [S60]. Procreate: U |

**Blender MCP:** `ahujasid/blender-mcp` MIT, 28.7k stars, Blender >=3.0; scene info, object/material edits, `execute_blender_code` (arbitrary Python), GLB/FBX export, Poly Haven/Sketchfab/Hyper3D/Hunyuan3D. Socket server has no auth; set `BLENDER_MCP_SAFE_MODE=1`; telemetry on by default [S53].

## G. Free / cheap compute
| Service | Facts |
|---|---|
| **GitHub Actions** | Public repos: Linux x64 and arm64 4 vCPU/16 GB/14 GB SSD; Windows 4/16/14; macOS arm64 3/7 GB. Private: Linux 2/8/14. No GPU (paid larger runners only). 6 h/job; Free plan 20 concurrent jobs, 2,000 min, 500 MB artifacts, 10 GB cache; private 2-core $0.006/min x64, $0.005 arm64 [S47] |
| **Kaggle** | P100 or 2x T4; ~30 GPU-h/week typical; 12 h sessions; phone verification [S43] |
| **Colab free** | <=12 h; limits unpublished [S50]; Pro for Education closed [S43] |
| **HF ZeroGPU** | 2 min anon, 5 min free, 40 min PRO ($9); 60 s default per call [S44] |
| **Modal** | $30/mo credits; per hour: T4 $0.59, L4 $0.80, L40S $1.95, A100-80 $2.50, H100 $3.95, B200 $6.25 (from per-second rates) [S45] |
| **Lightning AI** | free top-up to 15 credits/mo; one free Studio, 4 h restarts; no $/h mapping [S43] |
| **Oracle Always Free** | A1 2 OCPU/12 GB (was 4/24), 200 GB block, 10 TB egress, idle reclaim <20% over 7 days [S46] |
| **Cloudflare** | Workers AI 10,000 neurons/day free [S49]; R2 free tier U |
| **RunPod / Vast** | RunPod 4090 $0.34 community, $0.69 secure; A100-80 $1.19-1.49; H100 $1.99-2.99 (2026-08-11) [S48]. Cheapest secure on-demand 2026-10-13: 4090 $0.51, 5090 $0.68, A100-80 $1.07, L40S $0.97, H100 $2.59-2.90 [S48]. Interruptible "50%+ cheaper", no rate |

## H. Claude-side tooling
- **Skills/MCP:** Remotion official skills [S55]; Blender MCP (above); ffmpeg MCP `misbahsy/video-audio-mcp` (trim, concat, overlays, burn subtitles, extract audio; MIT, 84 stars); Manim MCP `abhiemj/manim-mcp-server` (runs Manim code; MIT, 644 stars); DaVinci Resolve MCP `samuelgursky` (MIT, 2.2k stars, 35 compound/353 tools; external scripting needs Resolve Studio); After Effects MCP `Dakkshin` (MIT, 540 stars, 14 tools, AE 2022+, ExtendScript bridge panel); OpenCut (MIT, 89.8k stars) is mid-rewrite, MCP and headless mode roadmap only [S66]; UE 5.8 experimental MCP [S57].
- **Claude Code GitHub Action** `anthropics/claude-code-action@v1`: free action; cost = runner minutes + tokens. Auth `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`; Pro/Max/Team/Enterprise); Bedrock/Vertex/Foundry via OIDC; `--max-turns`, `--model`; cron triggers work, public-repo schedules pause after 60 idle days [S65].
- **Agent SDK:** Python and TypeScript; same tools, hooks, subagents, MCP, skills, plugins. Use API keys; third parties may not offer claude.ai login or rate limits [S65].
- **Lineup, $/MTok in/out** [S65]: **Haiku 5.5** 0.10/0.50 (prompts <=100K; 0.50/2.50 above); **Sonnet 5.5** 2/10; **Opus 5.5** 4/20; **Fable 5.1 / Mythos 5.1** 10/50 (Mythos price on platform page only); legacy Haiku 4.5 1/5, Sonnet 4.6 3/15, Opus 4.x 5/25. Batch -50%; cache hit 0.01/0.10/0.20/0.25 (Haiku/Sonnet/Opus/Fable); tokenizer 4.7+ ~+30% tokens. Plans: Pro $20/mo ($17 annual), Max from $100.
- **Budget model:** bulk (tagging, QA, captions, shot lists) on Haiku; code and prompts on Sonnet; creative direction and story review on Opus; Fable only for the hardest calls. A 40K-in/4K-out call costs ~$0.006 / $0.12 / $0.24 / $0.60 across the four tiers.

## Sources
S1 help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation | S2 ai.google.dev/gemini-api/docs/pricing | S3 ai.google.dev/gemini-api/docs/veo | S4 benchlm.ai/media-pricing/veo (2026-09-11) | S5 gemini.google/overview/video-generation/ | S6 ai.google.dev/gemini-api/docs/image-generation | S7 docs.x.ai/developers/model-capabilities/video/generation | S8 docs.x.ai/developers/models/grok-imagine-video-1.5 | S9 docs.x.ai/developers/models/grok-imagine-video-1.5-lite | S10 docs.x.ai/developers/models/grok-imagine-image-2.0 | S11 docs.x.ai/developers/model-capabilities/video/reference-to-video | S12 docs.x.ai/developers/model-capabilities/images/generation | S13 x.ai/news (posts grok-imagine-video-1-5, -references, grok-imagine-image-2) | S14 x.ai/grok | S15 justinmckelvey.com/blog/supergrok-pricing (2026-09-27) | S16 sloane.world/guides/grok-imagine-limits-2026 (2026-10-13) | S17 alloypress.com/blogs/grok-ai-pricing (Jul 2026) | S18 testingcatalog.com/xai-debuts-imagine-agent-in-grok-with-open-canvas-ai-workspace/ (2026-04-30) | S19 progressiverobot.com/2026/09/05/grok-imagine-agent-image-2-0-model-update/ | S20 docs.dev.runwayml.com/guides/pricing/ | S21 runway.com/pricing | S22 ir.kuaishou.com Kling 3.0 release (2026-02-05) | S23 krea.ai/blog/kling-3-0-api-access-guide-pricing-code-examples-for-multi-shot-ai-video | S24 fal.ai/learn/tools/what-is-kling-4-0 (2026-09-29) | S25 toolcolumn.com/tools/kling-ai (2026-08-24) | S26 atlascloud.ai/collections/kling | S27 lumalabs.ai/ray | S28 toolcolumn.com/tools/luma-dream-machine (2026-07-24); therundown.ai/tools/runway-gen-4-5 (2026-08-28) | S29 huggingface.co/blog/ResterChed/minimax-h3-hailuo-3-0 | S30 camclo3d.com/blog/seedance-pricing (2026-09-29) | S31 openrouter.ai/bytedance/seedance-2.0 | S32 pikaslabs.com | S33 javisreview.com/review/midjourney-review-2026/ (2026-10-05) | S34 howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2 | S35 github.com/Wan-Video/Wan2.2 | S36 huggingface.co/Lightricks/LTX-2.5 | S37 ltxworkflow.com/guide/ltx-2-5-vram-requirements | S38 github.com/Tencent-Hunyuan/HunyuanVideo-1.5/blob/main/LICENSE | S39 huggingface.co/MiniMaxAI/MiniMax-H3; atlascloud.ai/blog/guides/minimax-h3-open-source-weights | S40 turingpost.com/p/6-opensource-video-generation-models (2026-09-26); presenc.ai/research/best-open-weight-video-generation-models-2026 (Allegro) | S41 spheron.network/blog/ai-video-generation-gpu-guide/ | S42 github.com/comfyanonymous/ComfyUI | S43 aimultiple.com/free-cloud-gpu (2026-09-16); gpuperhour.com/blog/free-cloud-gpus-and-credits (2026-09-21) | S44 huggingface.co/docs/hub/spaces-zerogpu | S45 modal.com/pricing | S46 docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm; infoq.com/news/2026/07/oracle-cloud-free-tier-limits/ (2026-07-03) | S47 docs.github.com Actions: runners, limits, billing pages | S48 gpuperhour.com (2026-10-13); spheron.network/blog/gpu-cloud-pricing-comparison-runpod-vs-vastai-2026/ | S49 developers.cloudflare.com/workers-ai/platform/pricing/ | S50 research.google.com/colaboratory/faq.html | S51 blender.org/download/, /download/releases/5-2/, /5-0/ | S52 pypi.org/project/bpy/ | S53 github.com/ahujasid/blender-mcp | S54 github.com/mrdoob/three.js/releases | S55 remotion.dev docs (gl-options, ai/skills, lambda/cost-example), remotion.pro/license, github.com/remotion-dev/remotion/releases | S56 godotengine.org/download/archive/; godot-docs creating_movies.rst | S57 unrealengine.com/license; unrealengine.com/news/state-of-unreal-2026-top-news-from-the-show (2026-06-17) | S58 unity.com/products/pricing-updates | S59 github.com/redotvideo/revideo, motion-canvas/motion-canvas, ManimCommunity/manim/releases | S60 rive.app/pricing; esotericsoftware.com/spine-purchase; cavalry.studio/en/; live2d.com/en/cubism/download/editor/; toolradar.com/tools/cascadeur/pricing; app.cinevva.com/guides/free-character-animations-rigging (2026-09-20); github.com/Acly/krita-ai-diffusion | S61 image: huggingface.co (FLUX.2-dev, FLUX.2-klein-4B, Z-Image-Turbo, Qwen-Image-Edit-2511, HunyuanImage-3.0); docs.bfl.ml/release-notes; marktechpost.com/2026/09/21/alibaba-qwen-releases-qwen-image-2-1/; aifreeapi.com/en/posts/openai-image-generation-api-pricing (2026-09-06); localaimaster.com/blog/image-generation-without-gpu (2026-09-27); github.com/leejet/stable-diffusion.cpp | S62 audio: elevenlabs.io/pricing/api; suno.com/pricing, suno.com/blog/suno-updates-tos (2026-08-10); undetectr.com/blog/udio-review-2026 (2026-09-25); ai.google.dev/gemini-api/docs/music-generation; localaimaster.com/blog/best-local-tts-models (2026-07-20); GitHub: ace-step/ACE-Step-1.5, QwenLM/Qwen3-TTS, nari-labs/dia, microsoft/VibeVoice, boson-ai/higgs-audio, thewh1teagle/kokoro-onnx, multimodal-art-projection/YuE, hkchengrex/MMAudio, FunAudioLLM/ThinkSound, Tencent-Hunyuan/HunyuanVideo-Foley; huggingface.co/stabilityai/stable-audio-open-1.0 | S63 GitHub: bytedance/LatentSync, TMElyralab/MuseTalk, MeiGen-AI/InfiniteTalk, DanielSWolf/rhubarb-lip-sync; sync.so/pricing | S64 GitHub: facebookresearch/sam3, ByteDance-Seed/Depth-Anything-3, ZhengPeng7/BiRefNet, ByteDance-Seed/SeedVR, hzwer/Practical-RIFE, AcademySoftwareFoundation/OpenColorIO; topazlabs.com/pricing | S65 platform.claude.com/docs/en/about-claude/pricing; claude.com/pricing; code.claude.com/docs/en/github-actions; code.claude.com/docs/en/agent-sdk/overview | S66 GitHub: samuelgursky/davinci-resolve-mcp, Dakkshin/after-effects-mcp, abhiemj/manim-mcp-server, misbahsy/video-audio-mcp, OpenCut-app/OpenCut
