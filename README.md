# RAW Viewer

Browser-based RAW photo viewer and editor. Single-page app (`index.html`), vanilla JS, WebGL2 pipeline.

## Two ways to run

### 1. Quick (double-click `index.html`, `file://`)
Works for: JPEG/PNG/WebP/HEIC, `.cube` LUTs, and RAW files from older cameras that the bundled **dcraw 9.26** can decode (e.g. Sony A7R II / A7 II). For RAW files dcraw cannot decode, it shows the embedded JPEG preview.

### 2. Full decoder (run `serve.cmd`)
Starts a local server and opens `http://localhost:8791/`. This enables the **LibRaw 0.22.1** decoder (`libraw/`), which decodes modern bodies dcraw can't - **Sony ZV-E1**, CR3, new lossless-compressed ARW, DNG, and more - at full quality.

LibRaw is a pthreads WebAssembly build, so it needs a **cross-origin isolated** origin (`Cross-Origin-Opener-Policy: same-origin` + `Cross-Origin-Embedder-Policy: require-corp`). `serve.py` sends those headers; a plain `python -m http.server` will not work. Requires Python 3.

```
serve.cmd            # or: python serve.py [port]
```

## Decoder cascade
For a RAW file the app tries, in order:
1. **LibRaw** (server only) - full decode of virtually any modern RAW.
2. **dcraw** (also `file://`) - older cameras.
3. **Embedded JPEG** - last resort so the file stays viewable/croppable/exportable.

## Files
| File | Purpose |
|---|---|
| `index.html` | the whole app (UI + WebGL2 shader pipeline) |
| `dcraw.js` | dcraw 9.26 asm.js decoder (offline fallback) |
| `libheif.js` | HEIC/HEIF decoding |
| `libraw/` | LibRaw-Wasm 1.6.0 (index.js, worker.js, libraw.js, libraw.wasm) |
| `serve.py` / `serve.cmd` | dev server with COOP/COEP headers |
