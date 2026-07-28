# RAW Viewer

Browser-based RAW photo viewer and editor. Single-page app (`index.html`), vanilla JS, WebGL2 pipeline. No build step, no backend.

By **Patrick Gawron** ([pg0](https://github.com/pg0)) - <https://github.com/pg0/raw-viewer>
Live demo: <https://pg0.github.io/raw-viewer/>

![Editor - Sony ARW at full RAW resolution](screenshots/editor.jpg)

| Grain, LUTs, denoise | A/B split compare |
|---|---|
| ![Grain and LUT panels](screenshots/grain-lut.jpg) | ![A/B split with a Portra 800 LUT](screenshots/ab-split.jpg) |

## Features
- RAW decode (LibRaw + dcraw), plus JPEG / PNG / WebP / BMP / GIF / HEIC / TIFF (uncompressed, LZW, PackBits, ZIP; 8- and 16-bit, via UTIF)
- Real-time WebGL2 adjustments: exposure, contrast, highlights/shadows, white balance, saturation, vibrance, and film grain - additive, luma-weighted, band-limited (Perlin gradient noise + particle shaping, same math as the FilmGrain DCTL), image-anchored so it bakes into the export. Grain controls are minimal and WYSIWYG: pick a film stock (Super 8 / 16mm / 35mm / 65mm / Custom) and it writes the visible Intensity + Grain size sliders to that format's real values (no hidden multiplier); editing a slider by hand flips it to Custom. Grain size is resolution-normalized (scales with image height / 1080p) so the look is identical at any resolution, and it starts off (Custom, intensity 0)
- Sharpness (Effects panel): one slider, contrast-adaptive. A 3x3 unsharp mask on a perceptually encoded luma, with the gain scaled down where local contrast is already high or close to clipping (the idea behind AMD's CAS) and the result clamped into the local min/max with an overshoot allowance. That clamp is what keeps the top of the slider usable, and it is also what limits it: raising the gain alone saturates against it (doubling it bought 38% more effect), so the slider opens the allowance as it climbs, 0.25 to 0.45. Measured across 0 -> 100 on a 1200x1600 photo, detail rises 66% (mean gradient 37.3 -> 61.9) with no new highlight clipping, 0.02% of pixels newly hitting black, and mean brightness unchanged (139.0 -> 138.5). Luma only, so no chroma fringing. It runs as a full-res image-space pass after denoise, cached like it, and the export runs the identical pass - judge it at 100% zoom, it thins out on a zoomed-out preview like in any raw converter
- Two `.cube` LUT slots (converter + style) with per-slot intensity
- Overlays: stack images, SVGs, text, or emoji (grain, film strip, light leaks, dust, stickers, captions) blended over the photo. Add via the panel buttons (+ Image / + Text / + Emoji) or by dropping an image onto the panel. Per overlay: blend mode (Normal / Screen / Multiply / Add), opacity, keep-aspect (contain-fit vs stretch), tiling, scale/zoom (0.1x - 12x), X/Y offset, and an optional alpha (chroma-key) colour to knock a colour out to transparent. Select an overlay and drag it on the photo to reposition it, drag the grip handle in the list to reorder layers, and double-click a text overlay to edit it. An "Apply effects to overlays" toggle at the top of the panel grades the overlays together with the photo (LUT, grain, exposure and the rest land on the overlays too). Overlays track crop/rotation and bake into the export
- Free-angle rotation (type any degree, or 90&deg; CW/CCW icons), crop with aspect presets (Free / 1:1 / 5:4 / 16:9 / 20:9) and a Portrait/Landscape orientation toggle, zoom/pan. At a free angle a crop has no axis-aligned rectangle in texture space, so it is applied as framing (scale and centre the view on it) - exact only when the viewport carries the crop's aspect ratio, which the export guarantees and the screen does not. The preview is therefore clipped to the crop rectangle, or the axis that is not the limiting one would keep showing image, and rotation wedges, past the crop edge
- Reset all clears the Face/Smile Detect edits too - every morph, the eye tweaks, the protect layer, the loaded eye photos. The detection survives it: that is a read of the photo, not an edit of it
- Histogram, per-group show/hide (A/B compare), JPEG export at full resolution - or downscaled via the Export panel: longest side (px), megapixels, or an exact pixel box (fit inside, aspect kept; downscale only, stepped high-quality resampling, the label previews the output size)
- Face/Smile Detect: detection, smile solvers, retouch sliders, child-protect anonymization, closed-eye donor fix, object/scene detections with EXIF keywords - all local, see [Face/Smile detect](#facesmile-detect)
- Double-click (or double-tap on touch) any slider or its label to reset it
- "Full resolution" toggle appears only for RAW files (nothing to re-decode behind a JPEG/PNG)
- Always-visible top bar (title + Open / Save) and a mobile-friendly layout: photo pinned on top, controls scroll below, pinch-to-zoom, vertical drag scrolls the panel (doesn't nudge sliders), and a button to switch the photo pane between 2/3 and 1/3 of the screen

## Face/Smile detect

Local face detection and retouch - MediaPipe FaceLandmarker WASM, vendored in `face/`, lazy-loaded, no cloud. Everything bakes into the export. Needs the server or the live site (the WASM engine can't load from `file://`).

### Detection and status

- Auto-detects when the panel opens or a new photo loads, and escalates to the tiled scan by itself when the full-frame pass comes back empty. The full-frame pass misses small or tilted faces by construction (the detector only proposes faces above a minimum size relative to its input), so no faces found is exactly the case the tiled scan exists for - making the user notice the second button and press it is not a feature. "Detect (tiled)" re-scans in overlapping 2x tiles and stays available for the case where the full-frame pass found something but not everyone.
- Low confidence bar (0.15), then junk is dropped by nose-distance dedup and a minimum face size.
- One status line per face: smile % and eyes open %, nothing else. Click a line to select that face - the same toggle as clicking it on the photo - and the selected face's line is marked wherever the selection came from. Header shows counts: "2🙂 1😐" (smiling = 30%+).
- The expression bucket (happy / neutral / surprised / angry / sad, off the MediaPipe blendshapes) is no longer written into that line. It is the one reading there that guesses at a mood instead of measuring the photo, and next to two numbers it read as a verdict on the person. `faceAnalyze` still computes it: "angry" is browDown above 0.5 *without* squinting eyes - browDown plus eyeSquint is a sun squint or a laugh, only a glare has one without the other, and a Duchenne grin fires browDown hard (0.65 measured on an 84% smile). The brow-driven labels freeze at the original detection because re-reading them off a baked small face is nonsense (browDown 0.99 where the unbaked face measured 0.65), and a measured smile past 30% takes the label back off them, since the ranking puts a smile above browDown.
- Faces an edit changed get a delta marker ("+21%" green for a boost, gray for a deliberate drop); tooltip shows the pre-edit value.
- Live re-analysis while dragging a slider - only the dragged face is re-measured, each face costs a full detector pass.
- Click a face (photo or panel label) to select it; solvers and Child protect then edit only that face. Its × badge or Delete removes a wrong detection.
- Mask overlay per face: None / Box / Mask / Eyes+mouth; outlines track the warp.
- The panel header's eye toggle bypasses the whole face bake - combined with A/B or the split view it compares edited vs. untouched.

### Smile solvers

- **Auto / Neutral / Model** close a feedback loop: set a value, bake, re-measure with MediaPipe, correct - until each face hits the target measured smile (Auto ~55%, Neutral closed with a hint of a smile, Model closed and near flat).
- The mouth close meets in landmark pairs just under the upper lip, with the contact line pulled to the corner-to-corner chord plus a per-button centre dip - flat is the worst allowed outcome, corners never droop.
- While the mouth is being sealed or parted, a point on the curve is inserted between every pair of neighbouring lip landmarks (four-point rule, so it lands where the lip actually runs rather than on the chord). Between two landmarks the mesh edge is a straight chord while the real lip edge bows past it, and that difference is where teeth survive - bright wedges, one per landmark pair, widest mid-segment. It also halves the triangle size along the seam, so the contact line stops coming out serrated.
- With that in place the contours simply meet: there used to be a 5% overlap past the contact line to cover the same wedges, but overlapping makes the contours *cross*, and a crossed triangle is inverted - it redraws the source mirrored, and the source there is teeth. It only looked clean while the painted seam was at full strength.
- The seal wins over what would reopen it. The smile's lip rise and the height morph land on the same axis and are not equal on the two contours (the upper lip elevates more), so a smiling mouth drifted back apart after being driven together - measured 1.2 to 1.6 px on an 80 px mouth, the "closes to 98%, never quite 100" case. They are subtracted from the seal target, faded by the same gap measure as the seal itself so the commissures, which have no partner to meet, keep their full rise instead of tearing away from their sealed neighbours. Residual now 0.0 to 0.1 px.
- Cheeks relax in proportion to how far the mouth was open; a painted contact shadow (sampled from the lip, kept red, width tapering sublinearly) covers what texture filtering leaves. It fades on already-closed mouths and is skipped under a covering Child-protect mode.
- **Mouth line** sets its opacity, per face, next to Mouth pos Y. Per face because how much cover the seam needs depends on how much aperture there was to collapse, and on a group shot that differs per mouth. It defaults to fully opaque - that is what covers the squashed-teeth remnant, and translucent over red lips the remnant grays the line out - but on a mouth that was barely open an opaque line reads as drawn on. The slider only scales the alpha: the point at which the line appears stays on the raw seal amount, so turning it down fades the line instead of moving its threshold. Measured over the mouth region against the line fully off: 1.4 / 3.0 / 4.8 / 6.8 mean channel difference at 25 / 50 / 75 / 100%, and turning one face's line off leaves every other face byte-identical.
- The measurement replays the exact detection tile that found each face - a full-frame re-detect can't see tiled faces. A face the detector loses mid-solve keeps the analytic estimate.

### Smile parameters

Eight sliders per face: Smile, Mouth open, Mouth width, Mouth height, Mouth pos Y, Mouth line, Eye smile, Brows (the upper lids follow the raise, so the eyes open with the brows). Each face has its own reset next to its name; the one in the panel header wipes every face. Mouth open runs both ways on one axis - right parts the lips as a jaw drop (lower lip carries 85% of it, corners stay pinned as the hinge, the parting fades out on a mouth that is already open so teeth are not stretched), left is the same seal the Neutral / Model buttons drive, so after a solve the slider shows how far they shut the mouth. The closing half runs to -120 rather than -100. At -100 the contours meet exactly now, so the extra travel is a sub-pixel press for a hairline left by landmark noise - anything larger would rebuild the crossed-triangle band described above. The warp is piecewise-affine: lip rings Delaunay-triangulated with a pinned anchor ring, zero displacement outside - nothing but the mouth region can move. Triangles whose corners all stayed put are dropped from the draw, so untouched skin is copied, never resampled. Smile targets follow real muscle kinematics (corner curvature over width, damped far side on turned heads); negative values relax rather than mirror the smile.

**The mesh resamples with Catmull-Rom, not bilinear.** Every pixel a triangle covers is fetched at a fractional offset, and the hardware bilinear filter drops about a fifth of the detail doing it - visible as a soft patch over a face that is otherwise sharp, worst wherever the mesh is dense. Snapping the displacements to whole pixels does not help: inside a triangle the mapping is an affine, so the sampling offset varies per pixel no matter where the corners land. Nine bilinear taps carrying the 4x4 cubic support fix it at the filter instead. Measured at full smile on a 95 px-IOD face (mean gradient energy, higher is sharper):

| region | untouched | bilinear | Catmull-Rom |
|---|---|---|---|
| mouth | 18.78 | 14.51 | 16.88 |
| cheek | 19.32 | 15.81 | 18.29 |
| eye | 19.20 | 16.60 | 18.35 |

What is left is the real geometric cost of squeezing and stretching pixels, which no filter can give back.

Control points are accumulated per landmark index rather than pushed in a list, so the mouth, brow and eye blocks can share landmarks (cheeks, lateral brow, eye corners) without putting a duplicate vertex into the Delaunay - the same index twice adds the displacements, which is what the muscles do to each other anyway.

**Closing a grin also relaxes the fold it dug.** The nasolabial crease from the nose wing to the mouth corner is shading, not geometry: the warp slides it around and it stays exactly as deep, so a wide open-mouth smile driven to Neutral came out as closed lips on a face still creased for a laugh. So it is painted out the way the furrow above is painted in - a soft wide stroke along the fold, each segment in the mean skin colour of both sides of it (the cheek alone paints a bright bar down the face), gated on the pre-close aperture because a mouth that was already closed has no grin-fold to relax. Alpha peaks at 0.40, which is a knee rather than a maximum: measured on an open grin at full relax, the crease contrast drops 34% while 80% of the skin texture in the band survives; pushing to 0.70 buys 49% for 68%. It is a flatten, not an erase - a real face keeps some fold at rest.

The fold path is the landmark chain 129-203-206-216-212 (and 358-423-426-436-432), verified in the mouth frame: it runs from the alar crease out and down to just past the mouth corner, lateral of it, and sampling luminance across it finds the expected dark valley, up to 33% below the skin either side on the widest grin in the test frame.

### Eye smile (Duchenne / AU6)

A smile that only moves the mouth reads dead, so the eye half rides on the Smile slider by default: orbicularis oculi contracts toward the orbit, the infraorbital pad lifts and closes the tear trough, the lateral brow sinks, and a furrow shadow appears under the lower lid. Below smile 0.25 nothing happens (a faint social smile genuinely has no AU6 in it), it eases in above that, and it is never mirrored on a negative smile - the anatomical opposite is a stare. Neutral / Model keep a 12% floor so a closed mouth does not read empty, and a face that already measured a big smile before editing gets scaled back so squint is not stacked on squint. The Eye smile slider shifts from that coupled amount: 0 is auto, up for a real grin with dead eyes, down when it pinches.

**Nothing inside the palpebral fissure moves.** Narrowing the lid gap is anatomically the loudest part of AU6 and it was the first thing built, but it hangs a dark spike off the bottom of every iris: the iris has to stay pinned (an oval pupil is the artifact everyone spots), so raising the lid shears the triangles between the two and drags iris texture down to the pinned vertex. That is not a tuning problem. A real lid slides *over* the eyeball, and occlusion is the one thing a mesh warp cannot express. So the aperture - both lid contours plus the iris - is pinned as one rigid unit and the expression is carried by what sits outside it, plus the painted furrow.

The cheek is capped against that pinned aperture, and the binding point is not the one anatomy suggests: in a real open eye the lids already cover the top and bottom of the iris and the landmarker still reports the full circle, so the iris bottom sits *behind* the lid, only 4 to 6 px above the tear-trough ring on a 100 px interpupillary face. Uncapped, the cheek drives through it and folds a visible patch of mesh at full slider. Two more guards, both per eye: an eye that is already half shut is skipped (measured off the original landmarks, never off the re-measured baked result, which would feed back on itself), and the far eye of a turned head is damped like the mouth is.

The furrow is painted, not warped - same technique as the closed-lip contact line: skin colour sampled from the pad below the eye, darkened per channel toward a warm shadow, stroked soft along the pinned lid margin, and clipped to the skin below that margin. The clip is not cosmetic: the stroke is deliberately wide and soft, and unclipped, half its blur landed back over the lash line on the eyeball - 8% of the iris contrast and 2% of its brightness, to a shadow that anatomically cannot fall there. A hard edge at the margin is right, because the lashes are a hard edge too and a crease starts where the skin starts. That split is the honest one, because the tell of a real smile there is a crease and a cast shadow, and a displacement warp can only move pixels that already exist. It cannot invent crow's feet either: it compresses whatever fine lines are in the photo but never draws new ones.

### Child protect

Anonymize faces per person: eye bar (black/white), emoji smiley (double-click on the photo to swap), mosaic, or blur - clipped to the face silhouette, head-roll aware. With a face selected the buttons set only that face, otherwise the default for everyone. Drawn into the bake, so it survives the export; mosaic/blur read the ungraded base, so the grade still applies on top.

![Child protect - emoji mode, clipped to the detected face](screenshots/feature_childprotect.jpg)

### Closed eye photo

Every face has an **Eyes from photo** picker in its header row: point it at another shot of the same people and that face takes **both** its eyes from there (per-eye similarity transform, feathered blend in linear light, colour matched per channel). Both eyes, open or shut - refusing to touch an open eye would make the picker do nothing exactly when it is used. The button then carries the file name, and its active state shows the result rather than the click: a face the automatic repair patched by itself also reads as on.

**The source is per face, not per session.** On a group shot the frame where one person's eyes are open is rarely the frame where the next person's are, so one shared photo would be the wrong question. Each loaded photo becomes one bake pass, ping-ponging between the two face targets, and the passes stack: face 1's eyes come from frame A while face 2's come from frame B, in one render. The same file picked twice is one texture.

A face with no photo of its own still gets its **shut** eyes repaired, from the first loaded photo that offers an open eye in that slot - the unattended pass over a group shot, where more loaded photos simply mean more chances. Faces are matched to a photo's faces left-to-right, so a photo with fewer faces can only answer for the first few.

Taking it back off is that face's reset, right next to the picker. The refusal is sticky and covers the automatic repair too, otherwise a face whose eyes are genuinely shut would be patched again one frame later from whatever else is loaded; picking a photo for that face lifts it. The panel header reset unloads every photo - they are inputs rather than edits, but they are the only inputs the panel loads, so keeping them would leave transplanted eyes on screen with no control that takes them off.

Selection deliberately assigns nothing. Aiming a photo with a click on the face reads well for one face and falls apart on the second: picking another face to move a slider is a navigation gesture, and it was silently transplanting eyes there too.

**The lid shape stays the target's.** A similarity transform is rigid, so the donor's whole eye used to arrive - its aperture, its lid line, its lashes - and the face kept looking like the person in the other photo. The patch is now bent onto the target's own eye contour: a Gaussian RBF field over the 16 ring landmarks, weights solved on the CPU (16x16, small ridge for stability) so the donor's lid margin lands on the target's rather than being averaged toward it. On a donor with a 25% wider eye the mean node error drops from 0.0208 to 0.0034 eye widths, 0.80 px to 0.13 px on a 38.5 px eye; the same field through a plain inverse-distance blend only reached 0.0124, which is why it is an RBF and not a Shepard average. The field fades out before the blend ellipse edge, so the patch still meets the surrounding skin as a plain similarity - measured 5.4/255 of change inside the eye and 0.01/255 on the cheek beside it. An identity donor (the photo used as its own source) still bakes pixel-identical to no donor at all.

It is gated on how open the **target** eye is, with the same ramp the rest of the face code uses, and that gate matters more than the feature: a shut eye's ring is a slit, and pulling an open donor onto it would deliver a shut transplant - exactly what the closed-eye repair exists to fix. So the repair keeps the rigid fit, byte for byte, and only an open target eye gets its own lid shape back. Cost is 0.2 ms per bake.

**Gaze is matched, not inherited.** The similarity fit lines up the eye corners, which says nothing about where the pupil sits inside them - so the donor's line of sight used to come along with its pixels. The sampling is now anchored on the iris instead: an open target eye states its own gaze, a shut one borrows from the other eye of the same face (gaze is conjugate, both eyes always point the same way), and with both shut the donor keeps its own placement, which beats centring because under head yaw "looking at the camera" is not a centred iris. Measured by faking one open eye shut and predicting its known iris from the other: 1.1 px on a 39 px eye, 4.2 px on a 43 px one. The shift is capped at 0.15 eye widths, because the whole donor eye slides with the iris and past that its own lid structure would leave the target aperture - a larger difference is a job for the Dir sliders or a different frame.

The patch samples the donor with the same Catmull-Rom reconstruction the smile mesh uses, and it has more to gain from it: the similarity fit is almost never 1:1, because the donor texture is capped at 3000 px while the base can be 6000. Measured with a donor at half the base resolution (iris region, mean gradient energy): bilinear 8.73, Catmull-Rom 12.10 - a third more detail out of the same donor pixels. What separates that from the 22.59 of the untouched eye is the donor's own resolution, which no filter invents back. A donor shot much closer than the base minifies instead, and there a cubic is neither better nor worse than bilinear.

Scale comes from each eye's own corner distance, but the rotation is read off the outer-canthus baseline of the whole face. That arm is ten times longer, so the same landmark jitter is a fraction of the angle - and on the eye that needs patching the lid is shut, which is precisely when its own corner axis is least trustworthy. The eye's private tilt against the face cancels in the donor-minus-base difference, so nothing is lost by measuring roll on the longer arm.

Eye size / direction / angle sliders cover what the 2D auto-fit can't (3D gaze and head-tilt mismatch). Dir X and Y move both eyes the same way in the face's own frame: taken raw the eye axis runs outer to inner, which points at the nose, so the two eyes would get mirrored frames and one slider would walk them apart instead of moving the pair.

**Mirror eyes** flips the donor along the eye's own axis, for a donor frame shot from the other side where the corner fit lines up but the eye still reads as the wrong one. The reflection is taken about the axis, not about the image, so it follows head roll, and the blend ellipse does not move (it squares that coordinate). The gaze fit follows the flip rather than fighting it: the reflection is its own inverse, so the correction is mirrored on the way in and the pupil still lands on the target's line of sight. Verified with the photo used as its own donor - mirror off is pixel-identical to no donor at all (mean difference 0.00/255), mirror on changes the eye by 7.6/255 and the cheek beside it by 0.04/255, and the dark iris blob stays 0.03 eye widths from the target iris instead of jumping to the mirrored side.

### Other detections

- The rest of the MediaPipe suite as overlays, each model loaded on first use: **Objects** (tiled EfficientDet boxes; click to select, double-click to rename), **Scene** (ImageNet labels), **Segments** (hair / skin / face / clothes), **Select** (click any object to mask it; ctrl adds, shift cuts), **Pose**, **Hands**. Confidences run below MediaPipe's defaults on purpose - at the defaults a group shot returns only the largest, most frontal person.
- **Save PNG** writes the active results out with alpha, one file per source: **Select** and **Segments** cut the graded photo out along their mask, **Pose** writes the skeleton lines onto a transparent frame (lines only, no photo, no joints). In Segments, click a layer on the photo to pick it - click again to drop it, click a second layer to add it, click the background to clear; unpicked layers dim so the pick reads as one. With nothing picked the cut-out is the whole person (every non-background class). Masks are placed with the same projection the on-screen overlay uses, so a crop or a rotation moves them with the pixels, and the Export panel's size row applies as it does to the JPEG.
- "to EXIF" writes detected object classes into the exported JPEG as keywords (EXIF XPKeywords = Windows "Tags", plus XMP `dc:subject` for Lightroom/Bridge). Works without any detected face.
- A debug block lists input size, per-pass counts, what the filters dropped, and per-face metrics.
- **Measure sharpness** puts a number on what the warp costs: mean gradient energy per region (mouth, cheek, eye, iris, chin), baked against the untouched photo at the same detection scale, so the two are pixel-aligned. Reports the picked face, or the first four when none is picked. Useful as a regression check - a change that softens the resampling shows up here before it shows up in a screenshot.

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
| `face/` | MediaPipe tasks-vision 0.10.35 (vision_bundle.mjs, wasm/) plus the models: face_landmarker, pose_landmarker_lite, hand_landmarker, selfie_multiclass_256x256, efficientdet_lite0, efficientnet_lite0, magic_touch (~72 MB total, each loaded only when its feature is used) |
| `coi-serviceworker.js` | cross-origin isolation shim for static hosts (MIT, G. Zuidhof) |
| `serve.py` / `serve.cmd` | dev server with COOP/COEP headers |

## Credits
- [LibRaw](https://www.libraw.org/) via [libraw-wasm](https://github.com/ybouane/libraw-wasm) (LibRaw 0.22.1)
- [dcraw](https://www.dechifro.org/dcraw/) 9.26 (Dave Coffin) via the `dcraw` npm asm.js build
- [libheif](https://github.com/strukturag/libheif)
- [UTIF.js](https://github.com/photopea/UTIF.js) - MIT, Ivan Kutskir (TIFF decoding)
- [pako](https://github.com/nodeca/pako) - MIT AND Zlib (inflate for ZIP-compressed TIFFs)
- [coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker) - MIT, Guido Zuidhof
- [MediaPipe tasks-vision](https://github.com/google-ai-edge/mediapipe) - Apache-2.0, Google (face landmarks + blendshapes for Smile Detect; pose, hand, segmentation, object-detection and image-classification models for the Advanced overlays)
- Film grain approach inspired by [filmgrainer](https://github.com/larspontoppidan/filmgrainer)
