import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFile } from "node:child_process";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const candidatePath = path.join(root, "research", "tra-19-directory-image-candidates.json");
const auditPath = path.join(root, "research", "tra-19-directory-image-acquisition.json");
const sourceDir = path.join(root, "research", "image-sources", "directory-images");
const concurrency = 10;
const execFileAsync = promisify(execFile);

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
      // Try the next runtime.
    }
  }
  throw new Error("sharp was not found");
}

const sharp = loadSharp();
const discovery = JSON.parse(fs.readFileSync(candidatePath, "utf8"));
const current = JSON.parse(fs.readFileSync(path.join(root, "data", "project-images.json"), "utf8"));
const retained = new Set(
  current.entries
    .filter((entry) => entry.source_kind === "upstream-project-asset")
    .map((entry) => entry.entry_id || `project:${entry.project_id}`),
);

function safeName(entryId) {
  return entryId.toLowerCase().replace(/[^a-z0-9._-]+/g, "--").replace(/^-+|-+$/g, "");
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

async function downloadCandidate(candidate) {
  let original;
  let finalUrl = candidate.url;
  let responseMime = "UNKNOWN";
  try {
    const response = await fetch(candidate.url, {
      headers: {
        "user-agent": "Mozilla/5.0 (compatible; KitAgainImageResearch/1.0; +https://kitagain.com/)",
        accept: "image/avif,image/webp,image/png,image/jpeg,image/gif,image/svg+xml;q=0.9,*/*;q=0.1",
      },
      redirect: "follow",
      signal: AbortSignal.timeout(25000),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const length = Number(response.headers.get("content-length") || 0);
    if (length > 20_000_000) throw new Error(`content-length ${length} exceeds limit`);
    original = Buffer.from(await response.arrayBuffer());
    finalUrl = response.url;
    responseMime = response.headers.get("content-type") || "UNKNOWN";
  } catch (fetchError) {
    const curl = process.platform === "win32" ? "curl.exe" : "curl";
    try {
      const result = await execFileAsync(curl, [
        "--location", "--silent", "--show-error", "--fail", "--max-time", "25",
        "--max-filesize", "20000000", "--user-agent",
        "Mozilla/5.0 (compatible; KitAgainImageResearch/1.0; +https://kitagain.com/)",
        candidate.url,
      ], { encoding: "buffer", maxBuffer: 21_000_000 });
      original = Buffer.from(result.stdout);
    } catch (curlError) {
      const fetchMessage = fetchError instanceof Error ? fetchError.message : String(fetchError);
      const curlMessage = curlError instanceof Error ? curlError.message.split("\n", 1)[0] : String(curlError);
      throw new Error(`${fetchMessage}; curl fallback: ${curlMessage}`);
    }
  }
  if (original.length < 2_000) throw new Error(`only ${original.length} bytes`);
  if (original.length > 20_000_000) throw new Error(`downloaded ${original.length} bytes exceeds limit`);
  const image = sharp(original, { animated: false, failOn: "error" });
  const metadata = await image.metadata();
  if (!metadata.width || !metadata.height) throw new Error("dimensions unavailable");
  if (metadata.width < 180 || metadata.height < 150 || metadata.width * metadata.height < 50_000) {
    throw new Error(`dimensions ${metadata.width}x${metadata.height} below threshold`);
  }
  const ratio = metadata.width / metadata.height;
  if (ratio < 0.2 || ratio > 5) throw new Error(`aspect ratio ${ratio.toFixed(2)} rejected`);
  const normalized = await sharp(original, { animated: false, failOn: "error" })
    .rotate()
    .resize({ width: 1200, height: 900, fit: "inside", withoutEnlargement: true })
    .webp({ quality: 82, effort: 5 })
    .toBuffer();
  if (normalized.length < 2_000) throw new Error(`normalized image only ${normalized.length} bytes`);
  return {
    candidate,
    final_url: finalUrl,
    response_mime: responseMime,
    original_bytes: original.length,
    original_sha256: sha256(original),
    width: metadata.width,
    height: metadata.height,
    format: metadata.format || "UNKNOWN",
    normalized,
    normalized_sha256: sha256(normalized),
  };
}

async function acquire(record) {
  if (retained.has(record.entry_id)) return { ...record, status: "retained-existing-upstream-asset", attempts: [] };
  const attempts = [];
  for (const candidate of record.candidates) {
    try {
      const accepted = await downloadCandidate(candidate);
      return { ...record, status: "candidate-accepted", attempts, accepted };
    } catch (error) {
      attempts.push({ url: candidate.url, error: error instanceof Error ? error.message : String(error) });
    }
  }
  return { ...record, status: record.candidates.length ? "all-candidates-rejected" : "no-candidate", attempts };
}

async function mapLimit(items, limit, mapper) {
  const results = new Array(items.length);
  let next = 0;
  async function worker() {
    while (true) {
      const index = next++;
      if (index >= items.length) return;
      results[index] = await mapper(items[index]);
    }
  }
  await Promise.all(Array.from({ length: limit }, worker));
  return results;
}

const results = await mapLimit(discovery.records, concurrency, acquire);
const seen = new Map();
const ledgerEntries = [];
fs.mkdirSync(sourceDir, { recursive: true });
for (const result of results) {
  if (result.status !== "candidate-accepted") continue;
  const duplicateOf = seen.get(result.accepted.normalized_sha256);
  if (duplicateOf) {
    result.status = "duplicate-image-rejected";
    result.duplicate_of = duplicateOf;
    delete result.accepted.normalized;
    continue;
  }
  seen.set(result.accepted.normalized_sha256, result.entry_id);
  const name = `${safeName(result.entry_id)}.webp`;
  const relativeSource = path.posix.join("research", "image-sources", "directory-images", name);
  fs.writeFileSync(path.join(sourceDir, name), result.accepted.normalized);
  const isPhotoLike = ["og:image", "twitter:image"].includes(result.accepted.candidate.origin)
    && result.accepted.width / result.accepted.height >= 0.75
    && result.accepted.width / result.accepted.height <= 2.4;
  ledgerEntries.push({
    entry_id: result.entry_id,
    content_id: result.content_id,
    entry_kind: result.entry_kind,
    project_id: result.entry_kind === "reviewed-project" ? result.content_id : undefined,
    source_file: relativeSource,
    local_file: path.posix.join("assets", "directory", name),
    source_kind: "upstream-source-page-image",
    source_url: result.accepted.final_url,
    source_page: result.source_page,
    image_license_status: "not-separately-stated",
    fit: isPhotoLike ? "cover" : "contain",
    alt_zh: `“${result.title_zh}”的上游来源图片`,
    alt_en: `Upstream source image for “${result.title_en}”`,
    caption_zh: `上游来源页为“${result.title_zh}”发布的图片；图片授权未单独声明。`,
    caption_en: `Image published on the upstream source page for “${result.title_en}”; no separate image license was stated.`,
    source_download_sha256: result.accepted.original_sha256,
    normalized_sha256: result.accepted.normalized_sha256,
    decoded_width: result.accepted.width,
    decoded_height: result.accepted.height,
    decoded_format: result.accepted.format,
    normalized_source: true,
  });
  delete result.accepted.normalized;
}

const audit = {
  schema_version: "1.0",
  policy: {
    minimum_bytes: 2000,
    minimum_width: 180,
    minimum_height: 150,
    minimum_pixels: 50000,
    maximum_source_bytes: 20000000,
    duplicate_normalized_sha256: "reject-after-first",
  },
  counts: {
    listed: results.length,
    retained_existing_upstream_asset: results.filter((item) => item.status === "retained-existing-upstream-asset").length,
    accepted_new_unique: ledgerEntries.length,
    duplicate_rejected: results.filter((item) => item.status === "duplicate-image-rejected").length,
    all_candidates_rejected: results.filter((item) => item.status === "all-candidates-rejected").length,
    no_candidate: results.filter((item) => item.status === "no-candidate").length,
  },
  ledger_entries: ledgerEntries,
  records: results,
};
fs.writeFileSync(auditPath, `${JSON.stringify(audit, null, 2)}\n`);
console.log(JSON.stringify(audit.counts));
