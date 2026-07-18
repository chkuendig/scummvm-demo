// Sentry init for the ScummVM Emscripten demo. Bundled (with the wasm
// integration, which the CDN Loader lacks) via esbuild into sentry.bundle.js
// and injected into the served HTML by CI. Config comes from window.__SENTRY_CFG__
// (dsn/release/environment), set by the same CI injection step.
import * as Sentry from "@sentry/browser";
import { wasmIntegration } from "@sentry/wasm";

const cfg = (typeof window !== "undefined" && window.__SENTRY_CFG__) || {};

if (cfg.dsn) {
  Sentry.init({
    dsn: cfg.dsn,
    release: cfg.release || undefined,
    environment: cfg.environment || "production",
    // wasmIntegration rewrites wasm stack frames to module + instruction addr +
    // debug-id so Sentry can symbolicate them against the uploaded debug files.
    integrations: [wasmIntegration()],
    // Emscripten aborts (e.g. OOM "Cannot enlarge memory") throw and are caught
    // by Sentry's default global handlers; attach memory context to every event.
    beforeSend(event, hint) {
      try {
        // Emscripten unwinds the stack on a normal exit() by *throwing* an
        // ExitStatus object ({name, message, status}); Sentry's global handler
        // would report every clean shutdown (e.g. dismissing a ScummVM error
        // dialog) as "Object captured as exception". Not an error - drop it.
        const ex = hint && hint.originalException;
        if (ex && (ex.name === "ExitStatus" || (typeof ex.status === "number" && typeof ex.message === "string" && /Program terminated|exit\(/.test(ex.message))))
          return null;
      } catch (e) { /* fall through to send */ }
      try {
        const mem = {};
        const heap = (typeof HEAPU8 !== "undefined" && HEAPU8) || (typeof window !== "undefined" && window.HEAPU8);
        if (heap) mem.wasm_heap_mb = +(heap.length / 1048576).toFixed(1);
        if (typeof performance !== "undefined" && performance.memory)
          mem.js_heap_mb = +(performance.memory.usedJSHeapSize / 1048576).toFixed(1);
        event.contexts = event.contexts || {};
        event.contexts.memory = mem;
      } catch (e) { /* best-effort */ }
      return event;
    },
  });
  window.Sentry = Sentry;

  // WebGL context loss is the signature of the GPU/texture OOM tab-kill.
  const hookCanvas = (tries) => {
    const c = document.getElementById("canvas");
    if (c) {
      c.addEventListener("webglcontextlost", () =>
        Sentry.captureMessage("WebGL context lost", "fatal"));
    } else if ((tries || 0) < 60) {
      setTimeout(() => hookCanvas((tries || 0) + 1), 500);
    }
  };
  if (document.readyState !== "loading") hookCanvas(0);
  else document.addEventListener("DOMContentLoaded", () => hookCanvas(0));
}
