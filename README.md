# RAW Viewer

Browser-based RAW photo viewer and editor. Single-page app (`index.html`), vanilla JS, WebGL2 pipeline. No build step, no backend.

By **Patrick Gawron** ([pg0](https://github.com/pg0)) - <https://github.com/pg0/raw-viewer>
Live demo: <https://pg0.github.io/raw-viewer/>

## Features
- RAW decode (LibRaw + dcraw), plus JPEG / PNG / WebP / BMP / GIF / HEIC
- Real-time WebGL2 adjustments: exposure, contrast, highlights/shadows, white balance, saturation, vibrance, and film grain - additive, luma-weighted, band-limited (Perlin gradient noise + particle shaping, same math as the FilmGrain DCTL), image-anchored so it bakes into the export. Grain controls are minimal: intensity, film-stock type (Super 8 / 16mm / 35mm / 65mm), and size
- Two `.cube` LUT slots (converter + style) with per-slot intensity
- Overlays: stack images, SVGs, text, or emoji (grain, film strip, light leaks, dust, stickers, captions) blended over the photo. Add via the panel buttons (+ Image / + Text / + Emoji) or by dropping an image onto the panel. Per overlay: blend mode (Normal / Screen / Multiply / Add), opacity, keep-aspect (contain-fit vs stretch), tiling, scale/zoom (0.1x - 12x), X/Y offset, and an optional alpha (chroma-key) colour to knock a colour out to transparent. Select an overlay and drag it on the photo to reposition it, drag the grip handle in the list to reorder layers, and double-click a text overlay to edit it. An "Apply effects to overlays" toggle at the top of the panel grades the overlays together with the photo (LUT, grain, exposure and the rest land on the overlays too). Overlays track crop/rotation and bake into the export
- Free-angle rotation (type any degree, or 90&deg; CW/CCW icons), crop with aspect presets (Free / 1:1 / 5:4 / 16:9 / 20:9) and a Portrait/Landscape orientation toggle, zoom/pan
- Histogram, per-group show/hide (A/B compare), JPEG export at full resolution
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

## Files
| File | Purpose |
|---|---|
| `index.html` | the whole app (UI + WebGL2 shader pipeline) |
| `dcraw.js` | dcraw 9.26 asm.js decoder (offline fallback) |
| `libheif.js` | HEIC/HEIF decoding |
| `libraw/` | LibRaw-Wasm 1.6.0 (index.js, worker.js, libraw.js, libraw.wasm) |
| `coi-serviceworker.js` | cross-origin isolation shim for static hosts (MIT, G. Zuidhof) |
| `serve.py` / `serve.cmd` | dev server with COOP/COEP headers |

## Credits
- [LibRaw](https://www.libraw.org/) via [libraw-wasm](https://github.com/ybouane/libraw-wasm) (LibRaw 0.22.1)
- [dcraw](https://www.dechifro.org/dcraw/) 9.26 (Dave Coffin) via the `dcraw` npm asm.js build
- [libheif](https://github.com/strukturag/libheif)
- [coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker) - MIT, Guido Zuidhof
- Film grain approach inspired by [filmgrainer](https://github.com/larspontoppidan/filmgrainer)
