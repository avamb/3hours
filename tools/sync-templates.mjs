/**
 * Sync question templates from one admin instance to another.
 *
 * Source/target are admin panel base URLs (NOT /api).
 * Uses existing admin API endpoints:
 *   - GET  /api/templates?limit=&offset=
 *   - POST /api/templates
 *   - POST /api/templates/:id/update
 *   - POST /api/templates/:id/delete
 *
 * Examples:
 *   node tools/sync-templates.mjs --dry-run
 *   node tools/sync-templates.mjs --from http://localhost:18088 --to https://3hours.andreevmaster.com
 *   node tools/sync-templates.mjs --delete-extra
 */

function getArgValue(name) {
  const idx = process.argv.indexOf(name);
  if (idx === -1) return undefined;
  return process.argv[idx + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

const FROM_BASE = getArgValue("--from") || "http://localhost:18088";
const TO_BASE = getArgValue("--to") || "https://3hours.andreevmaster.com";
const DRY_RUN = hasFlag("--dry-run");
const DELETE_EXTRA = hasFlag("--delete-extra");
const CONCURRENCY = Math.max(1, Math.min(parseInt(getArgValue("--concurrency") || "6", 10) || 6, 25));

function normalizeBaseUrl(base) {
  return base.replace(/\/+$/, "");
}

function templateKey(t) {
  const lang = (t.language_code || "").trim();
  const formal = t.formal === true ? "1" : "0";
  const category = (t.category || "").trim();
  const text = (t.template_text || "").trim();
  return `${lang}|${formal}|${category}|${text}`;
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} ${res.statusText} for ${url}\n${body}`);
  }

  return res.json();
}

async function fetchAllTemplates(baseUrl) {
  const base = normalizeBaseUrl(baseUrl);
  const all = [];
  const limit = 100;
  let offset = 0;
  for (;;) {
    const url = `${base}/api/templates?limit=${limit}&offset=${offset}`;
    const { templates, total } = await fetchJson(url);
    all.push(...(templates || []));
    if (!templates || templates.length === 0) break;
    if (typeof total === "number" && all.length >= total) break;
    offset += limit;
  }
  return all;
}

async function runPool(items, worker, concurrency) {
  const queue = items.slice();
  const results = [];
  const runners = new Array(concurrency).fill(0).map(async () => {
    while (queue.length) {
      const item = queue.shift();
      results.push(await worker(item));
    }
  });
  await Promise.all(runners);
  return results;
}

async function main() {
  const from = normalizeBaseUrl(FROM_BASE);
  const to = normalizeBaseUrl(TO_BASE);

  console.log(`[sync-templates] from=${from}`);
  console.log(`[sync-templates] to=${to}`);
  console.log(`[sync-templates] dryRun=${DRY_RUN} deleteExtra=${DELETE_EXTRA} concurrency=${CONCURRENCY}`);

  const [src, dst] = await Promise.all([fetchAllTemplates(from), fetchAllTemplates(to)]);

  const srcByKey = new Map();
  for (const t of src) srcByKey.set(templateKey(t), t);

  const dstByKey = new Map();
  for (const t of dst) dstByKey.set(templateKey(t), t);

  const toCreate = [];
  const toUpdate = [];
  const toDeactivate = [];
  const toDelete = [];

  // Create missing + update mismatched is_active
  for (const [key, t] of srcByKey.entries()) {
    const existing = dstByKey.get(key);
    if (!existing) {
      toCreate.push(t);
      continue;
    }

    // Keep flags in sync (and avoid breaking IDs)
    const desiredActive = t.is_active !== false;
    const existingActive = existing.is_active !== false;
    if (desiredActive !== existingActive) {
      toUpdate.push({ id: existing.id, patch: { is_active: desiredActive } });
    }
  }

  // Deactivate/delete extras
  for (const [key, t] of dstByKey.entries()) {
    if (srcByKey.has(key)) continue;
    if (DELETE_EXTRA) toDelete.push(t);
    else toDeactivate.push(t);
  }

  console.log(`[sync-templates] source templates: ${src.length}`);
  console.log(`[sync-templates] target templates: ${dst.length}`);
  console.log(`[sync-templates] toCreate: ${toCreate.length}`);
  console.log(`[sync-templates] toUpdate: ${toUpdate.length}`);
  console.log(`[sync-templates] to${DELETE_EXTRA ? "Delete" : "Deactivate"} extras: ${DELETE_EXTRA ? toDelete.length : toDeactivate.length}`);

  if (DRY_RUN) return;

  // Create
  let created = 0;
  await runPool(
    toCreate,
    async (t) => {
      await fetchJson(`${to}/api/templates`, {
        method: "POST",
        body: JSON.stringify({
          template_text: (t.template_text || "").trim(),
          language_code: (t.language_code || "ru").trim(),
          formal: t.formal === true,
          category: (t.category || "general").trim(),
          is_active: t.is_active !== false,
        }),
      });
      created += 1;
      if (created % 25 === 0) console.log(`[sync-templates] created ${created}/${toCreate.length}`);
    },
    CONCURRENCY,
  );

  // Update
  let updated = 0;
  await runPool(
    toUpdate,
    async (u) => {
      await fetchJson(`${to}/api/templates/${u.id}/update`, {
        method: "POST",
        body: JSON.stringify(u.patch),
      });
      updated += 1;
      if (updated % 50 === 0) console.log(`[sync-templates] updated ${updated}/${toUpdate.length}`);
    },
    CONCURRENCY,
  );

  // Deactivate extras
  let deactivated = 0;
  if (!DELETE_EXTRA) {
    await runPool(
      toDeactivate,
      async (t) => {
        await fetchJson(`${to}/api/templates/${t.id}/update`, {
          method: "POST",
          body: JSON.stringify({ is_active: false }),
        });
        deactivated += 1;
        if (deactivated % 50 === 0) console.log(`[sync-templates] deactivated ${deactivated}/${toDeactivate.length}`);
      },
      CONCURRENCY,
    );
  }

  // Delete extras (dangerous)
  let deleted = 0;
  if (DELETE_EXTRA) {
    await runPool(
      toDelete,
      async (t) => {
        await fetchJson(`${to}/api/templates/${t.id}/delete`, { method: "POST" });
        deleted += 1;
        if (deleted % 25 === 0) console.log(`[sync-templates] deleted ${deleted}/${toDelete.length}`);
      },
      CONCURRENCY,
    );
  }

  console.log(`[sync-templates] done: created=${created} updated=${updated} deactivated=${deactivated} deleted=${deleted}`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});


