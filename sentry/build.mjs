import * as esbuild from "esbuild";
await esbuild.build({
  entryPoints: ["sentry-init.js"],
  bundle: true, minify: true, format: "iife", target: "es2019",
  sourcemap: true,   // emit sentry.bundle.js.map for Sentry symbolication
  outfile: "sentry.bundle.js",
});
console.log("built sentry.bundle.js (+ .map)");
