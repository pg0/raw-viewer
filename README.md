# RAW Viewer

Browser-based RAW photo viewer and editor. Single-page app (`index.html`), vanilla JS, WebGL2 pipeline. No build step, no backend.

By **Patrick Gawron** ([pg0](https://github.com/pg0)) - <https://github.com/pg0/raw-viewer>
Live demo: <https://pg0.github.io/raw-viewer/>

## Features
- RAW decode (LibRaw + dcraw), plus JPEG / PNG / WebP / BMP / GIF / HEIC / TIFF (uncompressed, LZW, PackBits, ZIP; 8- and 16-bit, via UTIF)
- Real-time WebGL2 adjustments: exposure, contrast, highlights/shadows, white balance, saturation, vibrance, and film grain - additive, luma-weighted, band-limited (Perlin gradient noise + particle shaping, same math as the FilmGrain DCTL), image-anchored so it bakes into the export. Grain controls are minimal and WYSIWYG: pick a film stock (Super 8 / 16mm / 35mm / 65mm / Custom) and it writes the visible Intensity + Grain size sliders to that format's real values (no hidden multiplier); editing a slider by hand flips it to Custom. Grain size is resolution-normalized (scales with image height / 1080p) so the look is identical at any resolution, and it starts off (Custom, intensity 0)
- Two `.cube` LUT slots (converter + style) with per-slot intensity
- Overlays: stack images, SVGs, text, or emoji (grain, film strip, light leaks, dust, stickers, captions) blended over the photo. Add via the panel buttons (+ Image / + Text / + Emoji) or by dropping an image onto the panel. Per overlay: blend mode (Normal / Screen / Multiply / Add), opacity, keep-aspect (contain-fit vs stretch), tiling, scale/zoom (0.1x - 12x), X/Y offset, and an optional alpha (chroma-key) colour to knock a colour out to transparent. Select an overlay and drag it on the photo to reposition it, drag the grip handle in the list to reorder layers, and double-click a text overlay to edit it. An "Apply effects to overlays" toggle at the top of the panel grades the overlays together with the photo (LUT, grain, exposure and the rest land on the overlays too). Overlays track crop/rotation and bake into the export
- Free-angle rotation (type any degree, or 90&deg; CW/CCW icons), crop with aspect presets (Free / 1:1 / 5:4 / 16:9 / 20:9) and a Portrait/Landscape orientation toggle, zoom/pan
- Histogram, per-group show/hide (A/B compare), JPEG export at full resolution
- Smile Detect: local face detection (MediaPipe FaceLandmarker WASM, vendored in `face/`, lazy-loaded; opening the panel or loading a new photo while it is open runs detection automatically, and dragging a morph slider re-analyzes the edited result live - the smile % and eye-openness % update to what the warp actually achieved). The panel header has the same eye toggle as the adjustment groups, bypassing the whole face bake for an A/B look. Reports per face whether the person smiles (mouthSmile blendshapes) and whether the eyes are open (landmark eye-aspect-ratio), plus a summary ("2 of 3 smiling - closed eyes: face 2"). Detection runs at a low confidence bar (0.15) so small faces in group shots are found, then junk is dropped by a nose-distance dedup (duplicate detections of one face) and a minimum inter-ocular size floor. An Advanced section adds "Deep scan (tiled)" - re-detection in 4 overlapping 2x-zoomed tiles, because the detector only proposes faces above a minimum size relative to the frame (lowering the confidence threshold finds nothing extra in group shots; zooming does) - plus debug info: input size, per-pass raw counts, what the filters removed, and per-face inter-ocular px / smile % / eye-aspect-ratios. It also exposes the rest of the MediaPipe vision suite as toggleable overlays, each loading its model on first use: **Objects** (EfficientDet-Lite0 boxes with class and score), **Segments** (selfie-multiclass segmentation tinting hair / skin / face / clothes / other), **Pose** (33 body landmarks, up to 6 people) and **Hands** (21 landmarks per hand, up to 8). Pose and Hands run well below MediaPipe's 0.5 default confidences (0.2 / 0.15) on purpose - at the defaults a group shot returns only the largest, most frontal person (measured on a 4-person photo: 0.4 gave 3 poses, 0.2 all 4; hands 0.3 gave 2, 0.15 gave 3). The counts and labels are summarised as text under the buttons. These need no detected face, so they work on any photo. A four-way mask overlay (None / Box / Mask / Eyes+mouth) draws per face either a numbered box, the full landmark tessellation, or the eye rings (green = open, red = closed) + lip outline; numbers match the status list and sliders, and the overlay tracks the smile warp (lip outlines follow the reshaped mouth). Clicking a face on the photo (or its label in the panel) selects it: the box and its number turn amber and the matching slider block is highlighted and bold, so it is unambiguous which sliders belong to whom in a group shot. Clicking it again, or clicking empty space, clears the selection. Per detected face two sliders side by side (Smile 0..150 and Mouth width 70-130%, which scales the lips along their axis and tames the smile's lateral stretch) reshape that mouth with a piecewise-affine warp: outer + inner lip rings are Delaunay-triangulated together with a pinned anchor ring (subnasale/nostrils, chin, jaw, nose, cheekbones) and drawn as displaced textured GPU triangles - displacement is exactly zero outside the anchor ring, so nothing but the mouth region can move (the earlier MLS field always bled into the rest of the face). Smile targets follow zygomaticus kinematics: corners travel supero-laterally at ~40 deg, the mouth widens, the upper lip elevates slightly, cheeks follow at about a third. "Closed Eye Photo" takes a second shot of the same person(s) - faces matched left-to-right after the same dedup/size filtering - and replaces closed eyes with the donor's open ones (per-eye similarity transform + feathered ellipse blend in linear light, luma-gain matched); the info line names the faces it applies to, and Eye size / Eye direction X/Y sliders tweak the donor content (scale around the eye center, shift in the rotated eye frame) when the 2D auto-fit can't match a 3D gaze difference. Runs as a pre-grade pass, so denoise/LUT/grain apply on top and it bakes into the export. Needs the server (or the live site) - the WASM engine can't load from `file://`
- Double-click (or double-tap on touch) any slider or its label to reset it
- "Full resolution" toggle appears only for RAW files (nothing to re-decode behind a JPEG/PNG)
- Always-visible top bar (title + Open / Save) and a mobile-friendly layout: photo pinned on top, controls scroll below, pinch-to-zoom, vertical drag scrolls the panel (doesn't nudge sliders), and a button to switch the photo pane between 2/3 and 1/3 of the screen

## Two ways to run

### 1. Quick (`file://`) - double-click `index.html`
Works for standard images, `.cube` LUTs, and RAW from cameras the bundled **dcraw 9.26** can decode. For newer RAW it cannot decode, it shows the embedded JPEG preview. LibRaw is unavailable here (service workers / module workers don't run on `file://`).

### 2. Full decoder - run `serve.cmd` (or deploy to Pages)
Starts a local server on `http://localhost:8791/` and enables the **LibRaw 0.22.1** decoder (`libraw/`).

```
serve.cmd            # or: python serve.py [port]   (Python 3)
```

LibRaw is a pthreads WebAssembly build (shared memory), so the page must be **cross-origin isolated** (`Cross-Origin-Opener-Policy: same-origin` + `Cross-Origin-Embedder-Policy: require-corp`). `serve.py` sends those headers - a plain `python -m http.server` will not work. On GitHub Pages (which can't set headers) a bundled `coi-serviceworker.js` shim provides the same isolation client-side.

## Supported RAW formats
The extension list many tools quote is **dcraw 9.26's** set (ARW, CR2, NEF, DNG, RAF, ORF, RW2, PEF, SRW, SR2, KDC, DCR, MRW, 3FR, ERF, MEF, MOS, X3F, ...) - and it's frozen at ~2016, so it misses recent bodies.

With the LibRaw path enabled (server / Pages) support jumps to **LibRaw 0.22.1's** full modern list: 1000+ cameras including **Sony ZV-E1**, Canon **CR3**, newer lossless-compressed ARW, current DNG, GoPro GPR, Phase One IIQ, and more. dcraw remains only as the offline (`file://`) fallback.

### Decoder cascade
For a RAW file the app tries, in order:
1. **LibRaw** (server/Pages) - full decode of virtually any modern RAW.
2. **dcraw** (also `file://`) - older cameras.
3. **Embedded JPEG** - last resort so the file stays viewable / croppable / exportable.

## Supporter key

RAW Viewer is free and stays free - no login, no paywall, no tracking. If it
saves you time, there's an optional "supporter key" honor-system nudge: the
♥ Support chip in the top bar opens a small modal explaining the deal, with
a link to <https://patrickgawron.com/support>.

Unlock works three ways:
- Paste a key into the modal's input and hit Unlock.
- Open the app with `?key=<key>` or `#key=<key>` in the URL (the key is
  saved to `localStorage` and stripped from the URL automatically).
- Nothing to do on repeat visits - a previously unlocked key is remembered.

Once unlocked, the chip becomes "♥ Thanks, `<name>`" (hover for the
supporter-since date), and the settings-preset row in the sidebar grows from
**3 slots to 9** - the app's only supporter perk. Nothing is removed or
gated for non-supporters; the tool stays fully functional either way.

Verification is 100% local: ECDSA P-256 + SHA-256 via the browser's
`crypto.subtle`, no network call, no server. Keys are issued with the
[`supporter-key`](../supporter-key) CLI - see that project for the format
spec, the issuing workflow, and how to embed the same verify snippet in
another tool.

## Files
| File | Purpose |
|---|---|
| `index.html` | the whole app (UI + WebGL2 shader pipeline) |
| `dcraw.js` | dcraw 9.26 asm.js decoder (offline fallback) |
| `libheif.js` | HEIC/HEIF decoding |
| `utif.js` | TIFF/TIF decoding (UTIF, MIT) |
| `pako_inflate.min.js` | inflate for ZIP-compressed TIFFs (pako, MIT) |
| `libraw/` | LibRaw-Wasm 1.6.0 (index.js, worker.js, libraw.js, libraw.wasm) |
| `face/` | MediaPipe tasks-vision 0.10.35 (vision_bundle.mjs, wasm/) plus the models: face_landmarker, pose_landmarker_lite, hand_landmarker, selfie_multiclass_256x256, efficientdet_lite0 (~61 MB total, each loaded only when its feature is used) |
| `coi-serviceworker.js` | cross-origin isolation shim for static hosts (MIT, G. Zuidhof) |
| `serve.py` / `serve.cmd` | dev server with COOP/COEP headers |

## Credits
- [LibRaw](https://www.libraw.org/) via [libraw-wasm](https://github.com/ybouane/libraw-wasm) (LibRaw 0.22.1)
- [dcraw](https://www.dechifro.org/dcraw/) 9.26 (Dave Coffin) via the `dcraw` npm asm.js build
- [libheif](https://github.com/strukturag/libheif)
- [UTIF.js](https://github.com/photopea/UTIF.js) - MIT, Ivan Kutskir (TIFF decoding)
- [pako](https://github.com/nodeca/pako) - MIT AND Zlib (inflate for ZIP-compressed TIFFs)
- [coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker) - MIT, Guido Zuidhof
- [MediaPipe tasks-vision](https://github.com/google-ai-edge/mediapipe) - Apache-2.0, Google (face landmarks + blendshapes for Smile Detect; pose, hand, segmentation and object-detection models for the Advanced overlays)
- Film grain approach inspired by [filmgrainer](https://github.com/larspontoppidan/filmgrainer)
