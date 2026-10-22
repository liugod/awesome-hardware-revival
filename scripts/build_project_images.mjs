import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const manifestPath = path.join(root, "data", "project-images.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

function loadSharp() {
  const candidates = [
    process.env.KITAGAIN_NODE_MODULES,
    process.env.NODE_PATH,
    path.join(os.homedir(), ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules"),
    path.join(root, "node_modules"),
  ].filter(Boolean);
  for (const modulesDir of candidates) {
    try {
      return createRequire(path.join(modulesDir, "_kitagain_loader.cjs"))("sharp");
    } catch {
      // Try the next configured dependency directory.
    }
  }
  throw new Error("sharp was not found. Set KITAGAIN_NODE_MODULES to a node_modules directory containing sharp.");
}

const sharp = loadSharp();
let built = 0;
for (const entry of manifest.entries) {
  const input = path.join(root, entry.source_file);
  const output = path.join(root, "docs", entry.local_file);
  if (!fs.existsSync(input)) throw new Error(`Missing source image: ${entry.source_file}`);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  await sharp(input)
    .rotate()
    .resize({ width: 1600, height: 1600, fit: "inside", withoutEnlargement: true })
    .webp({ quality: 82, effort: 5 })
    .toFile(output);
  built += 1;
}

console.log(`Built ${built} project images from ${path.relative(root, manifestPath)}.`);
