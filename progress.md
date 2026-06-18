# DeepEval — Progress & TODOs

## Current focus: standardize metric prompt templates (cross-language)

Approach (Python, on branch `standardizeTemplates`): prompt templates live as Jinja2 `.txt`
files at `deepeval/metrics/**/templates/<Class>/<method>.txt` (+ shared `metric_templates/fragments/`).
`scripts/compile_metric_templates.py` compiles them into one
`deepeval/metric_templates/templates.json`. `metric_templates/resolver.py` → `resolve_template(...)`
renders the Jinja string to a final prompt; metrics call it instead of the old `Template.method()`.
Data prep stays in metric code; presentation logic lives in the templates. The JSON is the
language-agnostic artifact TypeScript will also consume.

### Done (this pass)
- **[#6] Removed the multi-language localization layer for V1** — parked in `extras/`
  (`extras/metric_templates/community/` + `extras/cli/translate/`). Also removed the
  `DEEPEVAL_METRIC_TEMPLATE_LANGUAGE` setting + validator and the `deepeval translate` CLI
  registration. Resolver is now base-English only.
- **[#5] Compiled-template caching** in the resolver (`(class, method, strict)` compiled once).
- **[#2] Compile-freshness test** — `tests/test_core/test_metric_templates.py` fails if
  `templates.json` drifts from the `.txt` sources (already caught + removed a stale `TranslateCLI`
  entry). Compile script refactored to expose `build_bundle()` / `render_bundle_json()`.
- **[#1] Migration parity validation — DONE.** Wrote one-off harnesses comparing every migrated
  template's rendered output to the old f-string output on `main` (sentinel fixtures enumerating
  multimodal/optional branches). Result: ~100 templates content-identical (whitespace-only), 2 real
  regressions found + fixed (turn_faithfulness multimodal fragment; inverted `they are`/`it is`
  conditional in contextual_precision + turn_contextual_precision), and ~24 "logic extracted into
  metric-code variables" refactors spot-checked as faithful. Then **dedented all template + fragment
  `.txt` files** (stripped purposeless block indentation, kept relative JSON nesting). Validation
  scripts/reports deleted afterward.

### TODO — template improvements (deferred)
- **[#3] Cross-engine parity guardrail (after TS exists):** keep every template within the
  Jinja2∩Nunjucks common subset; golden-render harness asserting Python (Jinja2) and TS (Nunjucks)
  produce identical output. Document the allowed subset.
  - **Two concrete diffs found + FIXED in the TS resolver** (no template/Python changes): (a) **array
    rendering** — Nunjucks now gives arrays a Python-`repr` `toString` (`{{ list }}` → `['a', 'b']`)
    while keeping them indexable/iterable (`score_range[0]` still works); (b) **trailing newline** —
    strip one trailing `\n` at compile to mirror `keep_trailing_newline=False`. Verified byte-identical
    on AnswerRelevancy (lists), GEval (indexing + conditional), TurnFaithfulness (multimodal), Bias.
  - **Comprehensive sweep — DONE & PASSING.** Rendered all 114 templates in both engines with
    identical auto-derived inputs (208 cases: multimodal off/on, simple `{% if %}` both ways, loops,
    indexing, fragments, object-attr access) → **208/208 byte-identical, 0 engine diffs, 0 one-sided
    errors**. Also flipped the 3 numeric-comparison conditionals (GoalAccuracy/ToolUse) to render their
    else-branches → identical. **Templates are parity-safe; TS metrics can build on them.** (Sweep was
    one-off via /tmp scripts, not committed.)
- ~~**[templates-build] templates.json single write-time source**~~ — ✅ DONE. The compile script now
  emits the bundle into BOTH packages (`deepeval/templates/metrics/templates.json` +
  `typescript/src/templates/metrics/templates.json`). The TS **build → `dist/`** copy is handled
  automatically by `tsc` (`resolveJsonModule` emits the imported JSON to
  `dist/templates/metrics/templates.json`); verified the built `dist/templates/resolver.js` resolves +
  renders it at runtime. No build-script change needed.

### Trace-metrics phase — Phase 1 DONE & TESTED
Foundation already existed in `src/tracing` (`observe`, `AsyncLocalStorage` context, `BaseSpan`/`Trace`
with eval fields + I/O auto-capture + Confident posting). The tracing layer was **observability-only** (no
local metric execution) — that's the gap the remaining phases fill.
- **Phase 1 (DONE):** `LLMTestCase._traceDict?` field; **`requiresTrace`** flag on `BaseMetricCore`
  (default false); local **`metrics?: BaseMetric[]`** on `BaseSpan` + `Trace`, threaded through `observe`
  (5 variants → `Tracer` → `createSpanInstance`) and `updateCurrentSpan`/`updateCurrentTrace`; and
  **`traceManager.createNestedSpansDict(span)`** (serialize span subtree → nested `{name,type,input,output,
  …,children}` dict, dropping bookkeeping). `import type { BaseMetric }` keeps the graph acyclic
  (metrics never import tracing). Verified locally: spans carry metrics; nested dict serializes a
  root→agent→tool tree. tsc+eslint clean.
- **Phase 2 (DONE):** [evaluate/trace-eval.ts](typescript/src/evaluate/trace-eval.ts) — `evaluateTrace(trace)`
  walks every span + the trace scope; for each scope carrying `metrics`, builds an `LLMTestCase` from its
  I/O, attaches `_traceDict = createNestedSpansDict(node)` when any metric `requiresTrace`, runs the
  metrics (reuses the runner's now-exported `runMetric` + `buildTestResult`), and returns one
  `TestResult` per scope (labelled by span/trace name). Guards "metrics but no input & not trace" → skip.
  Verified end-to-end: a component metric (AnswerRelevancy on a span) + a `requiresTrace` metric (received
  the trace dict) both scored correctly. tsc+eslint clean.
- **Phase 3 (DONE):** `TraceManager.setTraceCaptureSink()` (captures completed traces instead of posting,
  wired into `endTrace`) + `EvaluationDataset.evalsIterator({ metrics, errorConfig, displayConfig })` —
  an `async function*` that registers the sink, yields each golden (you run your `observe`-wrapped agent
  in the loop body), then on resume evaluates the trace(s) that completed (attaching the trace-level
  `metrics` to `trace.metrics`, plus the span-level metrics from `observe`/`updateCurrentSpan`), via
  `evaluateTrace`. Accumulates `dataset.evalResults` + prints the report at the end. Verified: a
  2-golden loop ran the agent per golden and evaluated each trace (trace metric got `_traceDict`).
  tsc+eslint clean. (Minor: per-trace result names restart at index 0 — named spans label correctly;
  unnamed trace scope shows `test_case_0`.)
- **Phase 4 (DONE & TESTED):** the 4 metrics, each its own folder
  ([task-completion](typescript/src/metrics/task-completion/), [plan-adherence](typescript/src/metrics/plan-adherence/),
  [plan-quality](typescript/src/metrics/plan-quality/), [step-efficiency](typescript/src/metrics/step-efficiency/)) —
  thin `BaseMetric`s with `requiresTrace=true` reading `testCase._traceDict`. TaskCompletion: extract
  task+outcome from trace (input/output fallback) → verdict. StepEfficiency: extract task → efficiency
  verdict. PlanAdherence/Quality: extract task (StepEfficiency template) + plan (PlanAdherence template,
  shared cross-class like Python) → adherence/quality (empty plan → score 1). var-check ALL OK,
  tsc+eslint clean. **Verified end-to-end via `evalsIterator`** over a real agent trace: TaskCompletion
  1.00, PlanAdherence 0.50, PlanQuality 1.00, StepEfficiency 1.00.

**Trace metrics COMPLETE → 45 of 47 metrics ported.** Only DAG (2: dag, conversational_dag) remains —
explicitly out of scope.

### Multimodal phase (1-1 port) — Phase 1 DONE & TESTED
Architecture (mirrors Python): **no separate MLLMTestCase** — images embed as slugs
`[DEEPEVAL:IMAGE|PDF:{id}]` inside the normal string fields; the **model layer** detects + converts them.
- **Phase 1 — multimodal core (DONE):** [test-case/mllm-image.ts](typescript/src/test-case/mllm-image.ts) —
  `MLLMImage` (exact Python fields: `dataBase64`/`mimeType`/`url`/`local`/`filename`/`id`); `toString()`
  → slug (used in template literals like Python f-strings); constructor validates + loads local files via
  Node `fs` → base64, handles remote URLs, registers in the global `MLLM_IMAGE_REGISTRY`. Plus
  `checkIfMultimodal`, `MLLMImage.parseMultimodalString` (registry round-trip), `convertToMultiModalArray`,
  `asDataUri`, `ensureImagesLoaded`. Added an **auto-detected `multimodal`** flag to `LLMTestCase` +
  `ConversationalTestCase` (from slug presence; overridable). Verified locally: slug/registry round-trip
  (same instance), PDF variant, local base64 + data-URI, validation, and auto-detect on both test cases.
- **Phase 2 — model vision support (DONE):** [models/multimodal.ts](typescript/src/models/multimodal.ts)
  has per-provider content builders that split a slug-containing prompt into text + image parts
  (`openAIContent`/`aiSdkContent`/`anthropicContent` are sync; `geminiContents` is async — base64,
  fetches remote URLs). Wired into **OpenAI-compatible** base (→ covers OpenAI/Azure/Grok/Kimi, `image_url`),
  **Gemini** (`inlineData`), **Anthropic** (`source` url/base64), **ai-sdk** (`messages` w/ image parts);
  all four now report `supportsMultimodal()`. Plain-text prompts pass through unchanged (verified: no
  text regression). Remote URLs pass through for OpenAI/ai-sdk/Anthropic; Gemini fetches + base64s them.
  Verified the exact content shapes per provider (remote + local) with no API. (bedrock/ollama still
  text-only — deferred.)
- **Phase 3 — the 5 metrics (DONE & TESTED):**
  [metrics/multimodal-metrics/](typescript/src/metrics/multimodal-metrics/) — **each metric in its own
  folder** (mirrors Python's `multimodal_metrics/`), self-contained logic (no shared base class), sharing
  only `schema.ts` + `utils.ts`.
  - **Per-image** (`image-coherence`/`image-helpfulness`/`image-reference`): parse `actualOutput` →
    multimodal array, for each image build `\`${instructions} \nImages: ${image}\`` (slug appended) →
    vision model → `score/10`, average.
  - **SC+PQ** (`text-to-image`/`image-editing`): split input/output into text+images, score semantic
    consistency (prompt↔image; editing also feeds the input image) + perceptual quality (each returns a
    score list) → `sqrt(min(SC)·min(PQ))/10`.
  - Images embed as appended slugs; the Phase-2 model layer converts them. var-check ALL OK, tsc+eslint
    clean. **Verified end-to-end with a real vision model**: ImageCoherence discriminates (relevant text
    0.80 vs mismatched 0.10), TextToImage 0.89–0.95 on a matching cat photo.

**41 of 47 metrics ported** (20 single-turn + 12 multi-turn + 3 MCP + 1 arena + 5 multimodal). Remaining:
trace-based (4) + DAG (2).

### Arena phase — DONE & TESTED (1 metric, 36 total ported)
- **`ArenaTestCase` + `Contestant`** ([test-case/arena-test-case.ts](typescript/src/test-case/arena-test-case.ts)):
  contestants answering a shared `input`/`expectedOutput`; validates unique names + same input/expected.
- **`BaseArenaMetric`** (3rd base class) — `measure()` returns the **winner's name (string)**, not a score;
  extends `BaseMetricCore` for the spinner/cost machinery.
- **`ArenaGEval`** ([metrics/arena-g-eval/](typescript/src/metrics/arena-g-eval/)) — GEval-style judge:
  generate eval steps → **mask** contestant names with shuffled dummies + randomized order → LLM picks the
  winning dummy + reason → **unmask** (winner via `dummyToReal`, reason via the `rewrite_reason` template).
  Reuses g-eval's `constructGEvalParamsString`/`numberEvaluationSteps`/`validateCriteriaAndEvaluationSteps`.
  `checkArenaTestCaseParams` added to `metrics/utils.ts`.
- **`compare()`** ([evaluate/compare.ts](typescript/src/evaluate/compare.ts)) — runs the metric over arena
  cases, tallies wins, returns `{contestant: winCount}`. **Progress + results now match Python:** a
  `MultiBar` with a top `🆚 Comparing N contestants sequentially` bar + per-case `🧐 Picking a winner (#i)`
  3-step bars (advanced via an `onStep` callback threaded into `ArenaGEval.measure`); the
  `🎉 Arena completed! … 🏆 Results … » <name>: <wins> wins` summary + share footer.
- **Confident-AI experiment posting — DONE** ([evaluate/compare-confident.ts](typescript/src/evaluate/compare-confident.ts)):
  builds a per-contestant `TestRun` (identifier = contestant; arena `MetricData` score = 1 for the winner;
  `metricsScores`/passes/fails; merged hyperparameters) and POSTs `{testRuns, name}` to a new
  `EXPERIMENT_ENDPOINT` (`/v1/experiment`). Gated on `CONFIDENT_API_KEY` (silent no-op + footer when
  logged out), never throws. The metric is reused across cases, so each case's winner/reason/error/cost
  is **snapshotted** right after `measure` before the next overwrites it.
- **Bug found + fixed:** `rewrite_reason` renders `{{ dummy_to_real_names }}` bare, and Nunjucks stringifies
  a plain object as `[object Object]` (the resolver only gives *arrays* a Python-repr `toString`). Fixed by
  passing the mapping as `JSON.stringify(...)` (matches the template's own JSON example). Live: correct
  winner picked, names masked→unmasked in both winner and reason.

### Cleanup pass — enum camelCase + feature-namespaced templates
- **TS param enums are camelCase** (`SingleTurnParams`/`ToolCallParams`/`MultiTurnParams` values:
  `actualOutput`, `retrievalContext`, `inputParameters`, …). `convertTurnToDict` keeps its output dict
  KEYS snake_case (`retrieval_context`, `tools_called`) via an explicit key map, so templates are
  unaffected. (Python enums stay snake_case — they mirror Python attribute names.)
- **Templates relocated + feature-namespaced.** Module renamed `deepeval/metric_templates` →
  `deepeval/templates` and TS `src/metric-templates` → `src/templates`; bundle now at
  `templates/metrics/templates.json` in both. `.txt` sources stay co-located per metric; fragments
  moved to `deepeval/templates/metrics/fragments/`.
- **`resolve_template`/`resolveTemplate` gained `feature` as the first positional arg** (`"metrics"`),
  loading `templates/<feature>/templates.json` (registry caches per feature). All call-sites updated by
  a migration script: **240 Python + 89 TS calls**, **46 Python + 33 TS imports**. Verified: no stale
  `metric_templates`/`metric-templates` refs; Python + TS render and run correctly; `tsc`+`eslint` clean.
- **[#4] Explicit per-template variable contract (after TS exists):** auto-extract required vars
  (`jinja2.meta.find_undeclared_variables`) into a manifest both Python and TS validate against.

## TypeScript metrics — phased plan (overview)

> Templates being shared only solves prompt duplication. Each metric still needs its **output
> schema** (`schema.py` → zod) and its **orchestration** (`measure()` algorithm) ported to TS.

- **Phase 0 — Shared template infra:** _(in progress)_
  - [x] `templates.json` copied to `typescript/src/metric-templates/templates.json` (hand-copy for
    now; proper dual-write is the `[templates-build]` TODO above).
  - [x] TS `resolveTemplate(className, method, vars, opts)` on **Nunjucks** in
    [typescript/src/metric-templates/resolver.ts](typescript/src/metric-templates/resolver.ts) —
    mirrors the Python resolver (base-only, cached envs + compiled templates, `throwOnUndefined`
    when strict, injects `_fragments` + `multimodal`). Added `nunjucks` dep + `@types/nunjucks`;
    `resolveJsonModule` enabled. `tsc` clean, renders verified.
  - [x] Parity harness ([#3]) — **done, 208/208 byte-identical**; both cross-engine diffs fixed.
  - [x] Phase 0 complete (only the cosmetic `[templates-build]` dual-write TODO remains).
- **Phase 1 — TS metric foundations — DONE.** `BaseMetric` enhanced (added `accrueCost`; plus
  `startProgress()`/`stopProgress()` helpers using `ora` — each metric's `measure()` calls them at
  start/`finally`. Renders Python's exact indicator: `✨ You're running DeepEval's latest <Metric>
  Metric! (using <model>, strict=…, async_mode=…)…` with the purple bar, on stderr, cleared on stop
  with no trailing log line; plus centralized **`checkLLMTestCaseParams`** (enum-driven required-param
  validation → `MissingTestCaseParamsError`), **`constructVerboseLogs`/`prettifyList`**, and a central
  **`src/errors.ts`** (`DeepEvalError`/`MissingTestCaseParamsError`));
  [typescript/src/metrics/utils.ts](typescript/src/metrics/utils.ts) adds `initializeModel` +
  `generateWithSchema` (`model.generate(prompt, zodSchema)` → validated object + accrue cost);
  per-metric zod-schema pattern established (`metrics/<name>/schema.ts`). All TS models are "native"
  (always return `{ output, cost }`), so cost is always accrued.
- **Phase 2 — Reference metric (AnswerRelevancy) — DONE & TESTED LIVE.**
  [typescript/src/metrics/answer-relevancy/](typescript/src/metrics/answer-relevancy/) — full
  statements → verdicts → reason flow via the shared templates (snake_case vars) + zod schemas +
  model layer. End-to-end run scored 0.667 with a coherent reason on a planted-irrelevant-statement
  case. Dir layout mirrors Python (`answer-relevancy/{answer-relevancy.ts, schema.ts, index.ts}`).
  Text-only for now (TS `LLMTestCase` has no multimodal).
- **`evaluate()` runner — DONE & TESTED (built before fan-out, deliberately, to lock the contract).**
  [typescript/src/evaluate/](typescript/src/evaluate/) mirrors Python's module: `evaluate(testCases,
  metrics, {asyncConfig, displayConfig, errorConfig, cacheConfig})` → `EvaluationResult`. Has the
  batch **cli-progress** bar (stderr, transient; per-metric spinners suppressed during batch),
  `ignoreErrors` + `skipOnMissingParams` (keys off `MissingTestCaseParamsError`), and per-(metric,
  case) state reset. Test cases run sequentially (stateful reused metric instances); metrics within a
  case run concurrently. **Console tables + Confident-AI posting now DONE** (see below). Remaining
  placeholders: result caching + cross-test-case concurrency (`maxConcurrent`).

### Runner upgrades
- **Per-metric progress bar is now an animated indeterminate "pulse"** (a bright window sliding across
  a dim track, wrapping) via `animatedBar()` in `base-metrics.ts`, driven by a `setInterval` updating
  the `ora` spinner text (cleared in `stopProgress`). Replaces the old static purple bar — mirrors
  rich's animated `BarColumn`.

### Runner — reason wrapping + file export + official
- **Full reason (no clipping):** the console table now **word-wraps** cells into multi-line rows
  (matching rich) instead of truncating to the column width — failing-case reasons + Input/Actual
  Output all show in full, borders stay aligned. (Passing-case reasons are still truncated, like Python,
  but those are hidden under `truncatePassingCases` anyway.)
- **File export:** `displayConfig.fileOutputDir` + `fileType: "md" | "mdx"` → writes the report to a
  Markdown/MDX file via `exportToMarkdown` (mirrors Python's `export_to_markdown`: `<details>` test-case
  data + metrics table with the full reason + aggregate table). Markdown is valid MDX so both share content.
- **`official`:** `evaluate(..., { official: true })` → threaded into `postTestRun`'s payload
  (`official`), mirroring Python's `evaluate(official=…)` → `test_run.official`.

### Runner — Python-parity pass (display + posting)
- **Metric description lines printed during `evaluate()`** — for each metric, the
  `✨ You're running DeepEval's latest <name> Metric! (using <model>, strict=…, async_mode=…)…` line
  (extracted to a public `describe()` on `BaseMetricCore`, reused by the per-metric spinner). Printed
  to stderr before the bars, mirroring Python.
- **Nested progress** (cli-progress `MultiBar`): a top `Evaluating N test case(s)` bar + one
  `🎯 Evaluating test case #i` bar per case (per-case bar fills as its metrics complete; main bar per
  case), with elapsed time (`{duration_formatted}`). Replaces the single flat bar.
- **Python-style completion output**: per-test-case tables now **truncate passing cases**
  (`truncatePassingCases`, default true, like Python) — only failing cases get a detail table; plus
  the aggregate table; then a **"⚠ No hyperparameters logged" warning** and a
  **`✓ Evaluation completed 🎉! (time taken | token cost) » Test Results … Pass Rate/Passed/Failed`**
  summary + share footer (`printHyperparametersWarning` / `printCompletionSummary` in console-report).
  When logged in, the Confident link is printed instead of the local summary.
- **Fixed Confident posting bug**: API test cases now include `runDuration` (the server requires it on
  conversational cases) — tracked per case in the runner and threaded through `EvaluatedCase`. Posting
  is a silent no-op when `CONFIDENT_API_KEY` is unset (direct env check, no `isConfident()` log spam).
- **Real console table** ([evaluate/console-report.ts](typescript/src/metrics/../evaluate/console-report.ts)):
  box-drawing tables — per-test-case **Status / Metric / Score / Threshold / Reason**, an **Aggregate
  Metrics** table (Avg Score / Pass Rate / Total), and an overall summary. ANSI-colored, no new deps
  (hand-rolled renderer with ANSI-aware padding). Replaces the placeholder text summary.
- **Confident-AI TestRun posting** ([evaluate/confident.ts](typescript/src/evaluate/confident.ts)):
  after local eval, builds a TestRun payload (LLM + conversational API test cases with `metricsData`,
  per-metric `metricsScores`, `testPassed`/`testFailed`, `runDuration`, `evaluationCost`) and POSTs to
  `/v1/test-run` via the existing confident `Api`; sets `confidentLink`/`testRunId` from the response.
  Gated on `isConfident()` (no-op + returns nulls when not logged in); never throws (logs a warning).
- **Removed the old `confident/evaluate.ts`** (that was a *remote* eval via `/v1/evaluate` with a
  metric collection — not our local runner). Top-level `evaluate` export now points at the new runner
  (`src/index.ts`), and `src/metrics` is exported as a submodule. Verified: table renders correctly
  (pass/fail/aggregate), posting is a clean no-op when logged out, animated bar runs + clears.
- **Phase 3 — Fan out + verify:** port a V1 batch (AnswerRelevancy, Faithfulness, GEval, Bias …),
  each = TS orchestration + zod schema reusing the SAME `templates.json`; add prompt-parity (and
  where feasible score-parity) tests per metric.

## Carry-over TODOs from the previous task (models: Python gateways + TS providers — done)
- **Python:** decide `LITELLM_ERROR_POLICY` — LiteLLM currently performs **no auto-retry** (wired to
  the central decorator but policy is `None`).
- **Python gateways backward-compat:** Portkey `.generate()` now returns `(output, cost)` and
  LiteLLM dropped `calculate_cost(response)` / `evaluation_cost` → land with a version bump + changelog.
- **TS model docs:** not written yet.
- **TS providers:** only OpenAI + Gemini were smoke-tested live; DeepSeek/Grok/Kimi/Azure/Bedrock/
  Ollama/OpenRouter/Portkey are config-only subclasses but unverified against real keys.

## Completed TypeScript metrics (single-turn fan-out)

Each = orchestration `.ts` + zod `schema.ts` + `index.ts` under `typescript/src/metrics/<name>/`,
reusing the shared `templates.json`, resolver, `generateWithSchema`, `checkLLMTestCaseParams`,
`constructVerboseLogs`, progress indicator, and the `evaluate()` runner. Verified = renders + runs
through the runner on sample cases (no Python score-parity check, by design). Text-only (no multimodal).

| Metric | TS class | Tier | Status |
|---|---|---|---|
| Answer Relevancy | `AnswerRelevancyMetric` | A (reference) | ✅ |
| Faithfulness | `FaithfulnessMetric` | A | ✅ |
| Contextual Precision | `ContextualPrecisionMetric` | A | ✅ |
| Contextual Recall | `ContextualRecallMetric` | A | ✅ |
| Contextual Relevancy | `ContextualRelevancyMetric` | A | ✅ |
| Bias | `BiasMetric` (lower-is-better) | A | ✅ |
| Toxicity | `ToxicityMetric` (lower-is-better) | A | ✅ |
| PII Leakage | `PIILeakageMetric` (higher-is-better) | A | ✅ |
| Non-Advice | `NonAdviceMetric` (higher-is-better; needs `adviceTypes`) | A | ✅ |
| Misuse | `MisuseMetric` (lower-is-better; needs `domain`) | A | ✅ |
| Role Violation | `RoleViolationMetric` (higher-is-better, binary; needs `role`) | A | ✅ |
| Hallucination | `HallucinationMetric` (lower-is-better; uses `context`) | A | ✅ |
| Prompt Alignment | `PromptAlignmentMetric` (higher-is-better; needs `promptInstructions`) | A | ✅ |
| Summarization | `SummarizationMetric` (min(alignment, coverage); `n`/`assessmentQuestions`) | A | ✅ |
| GEval | `GEval` (criteria→steps→score; `rubric`/`evaluationParams`; name `<name> [GEval]`) | B | ✅ |
| Json Correctness | `JsonCorrectnessMetric` (deterministic zod-validate; needs `expectedSchema`) | B | ✅ |
| Exact Match | `ExactMatchMetric` (deterministic, no model; adds `precision`/`recall`/`f1`) | C | ✅ |
| Pattern Match | `PatternMatchMetric` (deterministic regex full-match; no model) | C | ✅ |
| Tool Correctness | `ToolCorrectnessMetric` (det. tool-match + optional LLM tool-selection; `availableTools`) | C | ✅ |
| Argument Correctness | `ArgumentCorrectnessMetric` (LLM verdict over `toolsCalled`) | C* | ✅ |

**Tier A — DONE (14). Tier B — DONE (2). Tier C/tool group — DONE (4).** Total: **20 metrics.**
**Remaining (deferred — need new infra):** `task_completion`, `plan_adherence`, `plan_quality`,
`step_efficiency` — all `requires_trace` (need a TS **trace abstraction** / `_trace_dict` on the test
case; TS has a `src/tracing` module to investigate first). `mcp_use_metric` — needs **MCP test-case
fields** (`mcp_servers`, `mcp_tools_called`, …).

GEval notes: TS has no token log-probs, so scoring uses the structured (score, reason) response =
Python's path when log-probs are unavailable (no log-prob-weighted score). `upload()`/`pull()`
(Confident AI) omitted. JsonCorrectness `expectedSchema` is a **zod** schema (⇄ Python pydantic);
JSON-schema for the failure-reason prompt comes from `toJsonSchema()`.

Tool group notes (`*` argument_correctness was originally bucketed Tier D but needs only `toolsCalled`,
no trace): ToolCorrectness is **hybrid** — deterministic tool-calling score (exact / ordered-LCS /
unordered, with input-param/output compare via `evaluationParams`) combined via `min` with an
optional LLM tool-selection score (`get_tool_selection_score` template, only when `availableTools` is
given). ToolCall equality = name + inputParameters + output (deep, order-insensitive); non-exact match
tracks matched called-tools by index. **Found a latent Python bug:** `ArgumentCorrectnessMetric`'s
`generate_verdicts` template expects `stringified_tools_called` but the Python code passes
`tools_called` — the TS port passes the stringified form (via `printToolsCalled`), which is correct.
Deterministic metrics (exact/pattern) have no model, so the spinner now omits the "using \<model\>"
clause when `evaluationModel` is unset.

### Deferred TS metric features
- **GEval `upload()` / `pull()` (Confident AI):** not ported. Python's `GEval` can push a metric
  definition to / pull one from Confident AI (`deepeval/metrics/g_eval/g_eval.py` + the
  `construct_geval_upload_payload` / `MetricPullResponse` / `construct_geval_pull_evaluation_params`
  helpers in `g_eval/utils.py`). Needs the Confident API client wired in TS. When added: `pull()`
  also resets `criteria`/`evaluationSteps`/`evaluationParams`/`rubric`/`scoreRange`, so re-run the
  rubric sort + score-range derivation after pulling. Note the raw GEval name is currently
  `private metricName` — expose it if upload needs the un-suffixed name.
- **GEval log-prob-weighted scoring:** if TS models ever expose raw responses + top-logprobs, port
  `calculate_weighted_summed_score` for parity with Python's primary (non-fallback) path.

Notes from the fan-out: each LLM metric = orchestration `.ts` + zod `schema.ts` + `index.ts`, reusing
the shared `templates.json`, resolver, `generateWithSchema`, `checkLLMTestCaseParams`,
`constructVerboseLogs`, the progress indicator, and the `evaluate()` runner. Before testing each
batch, run Jinja `meta.find_undeclared_variables` over the metric's templates to confirm every var is
passed (caught NonAdvice's `advice_types_str` and would catch any miss). Summarization borrows the
Faithfulness `generate_truths`/`generate_claims` templates and appends to the reason prompt by hand
(mirroring Python). Text-only throughout (no multimodal).

## NOT-yet-implemented metrics (backlog)

| Metric(s) | Category | Blocker / why deferred |
|---|---|---|
| ~~turn_relevancy, turn_faithfulness, turn_contextual_precision/recall/relevancy, conversation_completeness, knowledge_retention, role_adherence, topic_adherence, goal_accuracy, conversational_g_eval, tool_use~~ | **Multi-turn (conversational)** — 12 | ✅ **DONE** (see Phases M0–M3). |
| task_completion, plan_adherence, plan_quality, step_efficiency | Single-turn, **trace-based** — 4 | **IN PROGRESS.** TS already has the `observe`/`AsyncLocalStorage`/span-tree foundation. Phase 1 (field/flag/`metrics` on spans/`createNestedSpansDict`) ✅ done; Phases 2–4 (executor → `evalsIterator` → 4 metrics) remain. See Trace phase below. |
| ~~MCPUseMetric, MCPTaskCompletionMetric, MultiTurnMCPUseMetric~~ | **MCP** — 3 | ✅ **DONE** (see MCP phase below). |
| dag, conversational_dag | **DAG** — 2 | Needs the DAG engine (decision-graph metric builder). Excluded from scope at the start. |
| ~~image_coherence, image_editing, image_helpfulness, image_reference, text_to_image~~ | **Multimodal** — 5 | ✅ **DONE** (Phases 1–3). See Multimodal phase below. |
| ~~arena_g_eval~~ | **Arena** — 1 | ✅ **DONE** (see Arena phase below). |

Implemented so far: **20 single-turn metrics** (Tier A 14 + Tier B 2 + tool/deterministic group 4).

## Multi-turn (conversational) — Phase M0 foundations: DONE
- **Shared base extracted:** `BaseMetricCore` (state + `ora` spinner + `accrueCost` + ctor) now holds
  everything common; `BaseMetric` (single-turn, `requiredParams: LLMTestCaseParams[]`) and
  `BaseConversationalMetric` ([base-conversational-metric.ts](typescript/src/metrics/base-conversational-metric.ts),
  `requiredParams: MultiTurnParams[]`, `measure(ConversationalTestCase)`) both extend it. The 20
  existing metrics are unchanged (BaseMetric extends core transparently). `generateWithSchema` /
  `constructVerboseLogs` now take `BaseMetricCore`, so conversational metrics reuse them.
- **Conversational utils** ([conversational-utils.ts](typescript/src/metrics/conversational-utils.ts)):
  `checkConversationalTestCaseParams` (EXPECTED_OUTCOME/SCENARIO/METADATA/TAGS/chatbot-role/turns →
  `MissingTestCaseParamsError`), `getTurnsInSlidingWindow<T>` (generic — turns or unit-interactions),
  `getUnitInteractions` (user→…→assistant blocks).
- **Test cases expanded to match Python (minus MCP):** `MultiTurnParams` enum added (full set sans
  MCP; `TurnParams` kept as deprecated alias). `Turn.retrievalContext` widened to
  `(string | RetrievedContextData)[]` (matches Python); `ConversationalTestCase.context` stays
  `string[]` (Python's field type is `List[str]`). `ConversationalTestCase.multimodal: boolean`
  added (default false, no auto-detect — text-only).
  (`metadata` kept as TS-convention `additionalMetadata`.)
- Verified: `tsc`/`eslint` clean; a throwaway conversational metric measures + param-checks +
  throws on missing scenario; sliding-window + unit-interactions correct.
### Phase M1 — turn-level metrics (5)
- **`TurnRelevancyMetric` — DONE & TESTED.** [turn-relevancy/](typescript/src/metrics/turn-relevancy/).
  Validated the whole conversational path end-to-end: unit-interactions → sliding windows → one
  verdict per window → relevant/total. Added `convertTurnToDict` to conversational-utils. Live run:
  coherent convo → 1.0, off-topic assistant turn → 0.5 with a "MESSAGE 2" reason.
- **4 RAG turn metrics — DONE & TESTED.** `TurnFaithfulnessMetric`, `TurnContextualPrecisionMetric`,
  `TurnContextualRecallMetric`, `TurnContextualRelevancyMetric`. Shared shape: per sliding window
  aggregate user content + assistant content + retrieval_context → single-turn-style verdicts →
  `Interaction*Score` (`{score, reason, verdicts/…}`); empty verdicts → interaction score 1; final
  score = **mean** of per-window scores (no windows → 1); a `generate_final_reason` template
  synthesizes the overall reason from per-window reasons. Each has its OWN templates + `Interaction*`
  schema (NOT a reuse of the single-turn classes). Live run on a RAG convo with a planted irrelevant
  context node: Faithfulness 1.0, Precision 0.92, Recall 1.0, Relevancy 0.58 (the bad node correctly
  drags down precision/relevancy). **Phase M1 (5 turn metrics + runner) COMPLETE.**
- **`evaluate()` runner — extended for conversational (M1c) — DONE.** Now accepts
  `(LLMTestCase | ConversationalTestCase)[]` + `(BaseMetric | BaseConversationalMetric)[]`; per case it
  runs only the metrics whose type matches (`metricMatchesCase`), and `buildTestResult` branches
  conversational (sets `turns`) vs single-turn. Progress-bar total = sum of matching (case, metric)
  pairs. Verified on a mixed batch (TurnRelevancy ran only on the convo, AnswerRelevancy only on the
  LLM case).

### Phase M2 — conversation-level (5)
- **`ConversationCompletenessMetric` + `KnowledgeRetentionMetric` — DONE & TESTED.** Both bespoke
  whole-conversation (no windowing), both higher-is-better. Completeness: extract user intentions over
  all turns → one verdict per intention → satisfied/total. KnowledgeRetention: extract knowledge per
  **user** turn → judge each **assistant** turn against accumulated prior knowledge → retained
  ("no"-attrition)/total (skips assistant turns with no prior knowledge). Both reuse `convertTurnToDict`.
  Live: good convo → Completeness 0.5 / Retention 1.0; bad convo (forgets name, unmet intent) →
  0.0 / 0.5.
- **`RoleAdherenceMetric` + `TopicAdherenceMetric` + `GoalAccuracyMetric` — DONE & TESTED. Phase M2
  COMPLETE (5 metrics).**
  - **RoleAdherence** (needs `chatbotRole` → `requireChatbotRole: true`): extract out-of-character
    assistant turns; score = in-character / total assistant turns. `ai_message` is set in code from
    the verdict's turn `index`. Live: in-role 1.0, off-character 0.0.
  - **TopicAdherence** (needs `relevantTopics`): per interaction extract Q&A pairs → classify each into
    a TP/TN/FP/FN cell → score = (TP+TN)/total (accuracy); reason built from per-cell reason lines. No
    `includeReason` guard (mirrors Python). Live: on-topic 1.0, off-topic 0.0.
  - **GoalAccuracy**: per interaction build `{user_goal, steps_taken}` (steps accumulate assistant
    content + `printToolsCalled`) → goal score + plan score (each 0–1) → final = mean of the two
    averages. Final reason is **free-text** (`model.generate`, no schema) — matches Python's misspelled
    template var `plan_evalautions`. The `get_accuracy_score` template is intentionally adversarial and
    `get_plan_evaluation_score` expects agentic tool steps → verified: terse 0.13, detailed-text 0.50
    (plan 0, no tools), agentic-with-tools 0.88 (goal 1, plan 0.75).
### Phase M3 — specials (2)
- **`ConversationalGEval` — DONE & TESTED.** GEval over a whole conversation. Reuses the single-turn
  `g-eval/schema` (Steps/ReasonScore) + `g-eval/utils` (Rubric, validateAndSortRubrics, formatRubrics,
  validateCriteriaAndEvaluationSteps, numberEvaluationSteps); adds `conversational-g-eval/utils.ts`
  (`CONVERSATIONAL_G_EVAL_PARAMS`, turn-params string, conversation-level fields string). Differences
  vs single-turn GEval: auto-appends CONTENT+ROLE to `evaluationParams`; score = `gScore/10` (NOT
  rubric-range normalized); `evaluate` passes `turns` (`convertTurnToDict` per turn) + conversation-level
  `test_case_content` separately. Schema path only (no log-probs). `name` → `<name> [Conversational
  GEval]` (raw name stored private, like single-turn). Live: empathetic reply 1.0, dismissive 0.0.
- **`ToolUseMetric` — DONE & TESTED.** Confirmed turn-based (uses `turn.toolsCalled` +
  `getUnitInteractions`, no trace). Per interaction build `UserInputAndTools` (user/assistant text +
  `printToolsCalled(toolsCalled)` + `printToolsCalled(availableTools)`); score tool selection and
  argument correctness (latter only when `tools_used`); final = `min(mean tool-selection, mean
  argument-correctness)`. Reason = both final-reason calls joined; **both use the
  `get_tool_selection_final_reason` template (Python's `get_tool_argument_final_reason` is unused — a
  latent template)**. Needs `availableTools`. Live: right-tool 1.0, wrong-tool 0.0.

**🎉 MULTI-TURN COMPLETE — all 12 conversational metrics done (M1 turn ×5, M2 conversation ×5, M3
specials ×2). Total ported: 32 metrics (20 single-turn + 12 multi-turn).** Only `conversational_dag`
remains on the conversational side (DAG — deferred with the other DAG/trace/MCP/multimodal/arena work).

### MCP phase — DONE & TESTED (3 metrics, 35 total ported)
- **Test-case MCP fields + file split first** (prereq): added `test-case/mcp.ts` (`MCPToolCall`,
  `MCPPromptCall`, `MCPResourceCall`, `MCPServer`, `validateMcpServers`, minimal `Tool`/`Resource`/
  `Prompt`); split the monolith into `llm-test-case.ts` (single-turn + MCP fields/params) +
  `conversational-test-case.ts` (`Turn`/`ConversationalTestCase` + MCP) mirroring Python. Enums
  extended with MCP params on both `SingleTurnParams` and `MultiTurnParams`; `validateMcpServers` wired
  into both test cases.
- **`MCPUseMetric`** ([mcp-use-metric/](typescript/src/metrics/mcp-use-metric/)) — single-turn
  (`BaseMetric`), required INPUT/ACTUAL_OUTPUT/MCP_SERVERS. Builds `available_primitives` +
  `primitives_used` text → two LLM calls (primitive-correctness + arg-correctness) → `min`. Reason =
  bracketed concat. Live: right-tool 1.0, wrong-tool 0.0.
- **`MCPTaskCompletionMetric` + `MultiTurnMCPUseMetric`** ([mcp/](typescript/src/metrics/mcp/)) — both
  conversational; share `mcp/utils.ts` (`getTasks`, `availableMcpServersBlock`, `taskStepsTakenText`,
  `mcpInteraction`). TaskCompletion = mean of per-task completion scores; MultiTurnMCPUse =
  `min(mean tool-correctness, mean args-correctness)` and **reuses the `MCPTaskCompletionMetric`
  template namespace** (mirrors Python). Both require non-empty `mcpServers` → else
  `MissingTestCaseParamsError` (verified). Live: both 1.0 on a correct-tool conversation.
- **Notes:** templates receive snake_case-shaped plain objects (`{input, actual_output}` / `{task}`),
  not the camelCase classes; `tool.result.structuredContent.result` accessed with a guard/fallback;
  `repr()` of primitives → `JSON.stringify`. var-check ALL OK, `tsc`+`eslint` clean.

NOTE: a refactor renamed `LLMTestCaseParams` → `SingleTurnParams` and `checkLLMTestCaseParams` →
`checkSingleTurnParams` across the single-turn metrics + test-case + utils (conversational side uses
`MultiTurnParams` / `checkConversationalTestCaseParams`, unchanged).
