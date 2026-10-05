# ScummVM upstream branch set

Prepared from the deployed integration and rebased on ScummVM upstream master `71cb05b1c03aa6bdcd34f78c20cef12c10067ba5` on 2026-10-05. The five branches live in the `scummvm/` submodule. They are prepared locally; no upstream PRs have been opened.

## Suggested PR order

| Order | Branch | Review base | Scope |
| --- | --- | --- | --- |
| 1 | `upstream/emscripten-runtime` | `upstream/master` | Shared Emscripten runtime, streamed VFS, SDK update, Asyncify configuration and loading progress |
| 2 | `upstream/cloud-streaming` | runtime | Range downloads and cloud filesystem streaming |
| 3 | `upstream/touch-controls` | runtime | Touch presets, on-screen controls and controller switching |
| 4 | `upstream/hpl1-webgl` | runtime | HPL1 WebGL2 rendering, shaders and controller-friendly menus |
| 5 | `upstream/emscripten-recorder` | runtime | Browser event recording, replay and timer integration |

Runtime is the foundation. The other four branches depend on it and can be reviewed independently once it lands. Branch heads, commit lists, file counts and exact bases are recorded in [upstream-pr-branches.json](upstream-pr-branches.json).

## Runtime details

The runtime branch includes the browser loading-progress correction: the fill now tracks the downloaded-byte text without a lagging CSS transition, and unknown or zero content lengths avoid invalid percentages. It also includes the SDL3 audio callback Asyncify guard. The Add Game exception was not reproduced during live browsing; a live-code A/B probe verified the guard returns before a callback enters wasm while Asyncify is suspended. The transient HTTP retry change remains deferred because its C++ implementation has not yet been compiled or runtime-tested.

The Emscripten dependency script now downloads a52dec 0.7.4 from Debian's original source archive and verifies its SHA-256 before extraction. The prior VideoLAN endpoint returned an Anubis challenge page to GitHub Actions; see the JSON manifest for the failed run and the retry status.

Full Asyncify imports are used for plugin builds, including release builds. The narrowed import list had omitted recorder/plugin imports. The demo enables `--enable-eventrecorder` and uses the full list.

## AI attribution

The repository's [AI-GUIDELINES.md](../scummvm/AI-GUIDELINES.md) requires commit-message disclosure with `Assisted-by: AGENT_NAME:MODEL_VERSION` and prohibits AI authorship or co-authorship. The prepared commits preserve Christian Kündig as author and record assistance in trailers. Historical model labels were preserved from existing metadata; no AI co-author trailers remain. Human contributors remain responsible for review and testing.

## Validation and deployment

The refreshed integration is `demo/upstream-integration`, based on the master commit above, and combines all five branches. `git diff --check`, shell syntax checks, the Asyncify audio-guard fixture test, JavaScript syntax/logic checks, and verification of the replacement source archive passed. The deployment retry is pending; the prior live deployment is identified in the JSON manifest and does not validate this integration.

The Add Game trap was not reproduced organically in live browser testing. A stress scan did produce an HTTP 429 and fatal dialog; its proposed transient-request retry is intentionally excluded from this deployment until it is compiled and exercised. The event-recorder replay also remains incomplete: it loaded the recording and requested the expected FT files, then stalled before framebuffer checks. Investigation continues in the dedicated event-recorder workspace.

No iOS build, cloud-account gameplay test, physical touch/controller test, or HPL1 gameplay test has been completed for this refreshed branch set. The deployment build and browser smoke will add evidence for the combined integration, not replace those platform-specific checks.

## Review commands

```sh
git -C scummvm diff upstream/master...upstream/emscripten-runtime
git -C scummvm diff upstream/emscripten-runtime...upstream/cloud-streaming
git -C scummvm diff upstream/emscripten-runtime...upstream/touch-controls
git -C scummvm diff upstream/emscripten-runtime...upstream/hpl1-webgl
git -C scummvm diff upstream/emscripten-runtime...upstream/emscripten-recorder
```

The live [demo](https://scummvm.kuendig.io/scummvm.html) and its [build provenance](https://scummvm.kuendig.io/build-info.json) identify the deployed source and all five branch tips. See the JSON manifest for exact SHAs, current publication state and test evidence.
