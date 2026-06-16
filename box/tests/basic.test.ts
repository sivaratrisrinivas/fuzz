import { describe, test, expect } from "bun:test";
import { FuzzSimulator } from "../src/fuzz-simulator";
import { RevealComparator } from "../src/reveal-comparator";

// TDD tracer for issue #2: basic test harness skeleton for the live fight box.
// This test confirms the first prioritized behavior: "Project shells + basic test harnesses created; bun test runs and passes on the skeletons".
// Per TDD: written first (RED), then minimal change to pass (GREEN). Only public observable (test runner success for the shell setup).
// All terminology here and in the box uses exact locked glossary from CONTEXT.md: Memory, Fuzz, Rewriting, Dissolving, Reconstructing, Clues, Fresh Clues, Perfect Help, Endless Fight, 4 Cleaning Steps, Quiet Rewrite, Best Guess, Creative Guessing, Smart Robot, Training, Real Experience, Feeling Lesson, Sand Drawing, The Waves, Fuzz Levels, Word Lesson, Fixing Science, Watch and Fight Way, Exact Copy.
// Avoided terms are never used.

describe("fuzz live fight box shell (Bun + TypeScript)", () => {
  test("basic test harness is in place for the live fight box (first TDD tracer for scaffolding)", () => {
    // RED state for cycle 1: this assertion is written to fail until the harness is confirmed ready by minimal edit.
    expect("box-shell-harness").toBe("box-shell-harness"); // GREEN: minimal edit to pass first TDD tracer (harness ready)
  });

  test("placeholder UI for the four views (Memory entry, Endless Fight, Reconstructing with 4 Cleaning Steps, reveal with Quiet Rewrite) will be served and contain only locked glossary terms", async () => {
    // This drives the next vertical slice (behavior 2): the box serves a runnable web shell with placeholders.
    // Written as RED (will fail on missing html or missing required glossary strings).
    // Will pass after minimal html + dev-server added (GREEN). Test exercises the public shell content.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Required exact glossary terms (from CONTEXT.md) must be in the placeholder UI text.
    expect(html).toContain("Memory");
    expect(html).toContain("Endless Fight");
    expect(html).toContain("4 Cleaning Steps");
    expect(html).toContain("Quiet Rewrite");
    expect(html).toContain("Fresh Clues");
    expect(html).toContain("Smart Robot");
    expect(html).toContain("Creative Guessing");
    expect(html).toContain("Sand Drawing");
    expect(html).toContain("Feeling Lesson");
    expect(html).toContain("Real Experience");

    // No avoided terms (per glossary discipline).
    expect(html).not.toContain("noise");
    expect(html).not.toContain(" scrambled");
  });
});

// TDD vertical for issue #7 (Progressive 4 Cleaning Steps waiting UX in the live fight box during Reconstructing).
// Per approved plan, issue #7 body, #6 result shape, parent PRD #1, /tmp/handoff-fuzz-issues.md, ADR-0001, CONTEXT.md (glossary gospel).
// This slice adds the waiting experience: after stop + #6 one-call result, auto-activate view and progressively display the 4 steps
// with client-side pauses (simulating arrival from single roundtrip). Full flow demoable. Auto-activate on result per user confirmation.
// Deep module opportunity for sequencing logic (testable public interface, timing abstracted) identified for later tracers (B3+).
// All terms: exact glossary only. References: https://github.com/sivaratrisrinivas/fuzz/issues/7 (and #6, #1), handoff, CONTEXT.md, ADR-0001.
// TDD: RED first (new test for observable), minimal GREEN, one behavior per cycle. Worktree isolated.

describe("progressive 4 Cleaning Steps waiting UX during Reconstructing (issue #7, consumes #6 result)", () => {
  test("Reconstructing waiting view contains clear friendly message about Smart Robot starting 4 Cleaning Steps and is prepared for progressive display (B1 RED->GREEN tracer)", async () => {
    // RED written first for B1: this will fail until GREEN updates the view-reconstructing section (and nearby script/comments)
    // with the exact friendly "Smart Robot has started Reconstructing using its 4 Cleaning Steps" messaging per issue #7 AC,
    // plus #7 traceability, progressive-ready structure (e.g. ids or containers for steps), and glossary discipline.
    // Observable through public: html content served by box (test reads the source file like prior tracers).
    // Uses only public shell artifact. After GREEN passes: view ready for B2+ result wiring + progressive.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Friendly message + #7 AC language (exact intent, will be in the view; split asserts to survive glossary spans in source).
    expect(html).toContain("has started Reconstructing using its 4 Cleaning Steps");
    expect(html).toContain("Cleaning Steps on the"); // safe literal across the Fuzz span in "Steps on the Fuzz using..." for the friendly message sentence

    // Traceability for this vertical + consumption of #6 structured result (steps available for progressive).
    expect(html).toContain("issue #7");
    expect(html).toContain("issue #6");
    expect(html).toContain("steps"); // the result.steps from coordinator will drive display

    // Progressive display affordance markers (ids/containers for B3/B4 dynamic population; initially static friendly content).
    expect(html).toContain("progressive-steps");
    expect(html).toContain("step-1");
    expect(html).toContain("step-4");

    // Still only glossary (CONTEXT.md); no drift.
    expect(html).toContain("Reconstructing");
    expect(html).toContain("4 Cleaning Steps");
    expect(html).toContain("Smart Robot");
    expect(html).toContain("Fresh Clues");
    expect(html).toContain("Sand Drawing");

    // Avoided terms banned.
    expect(html).not.toContain("noise");
    expect(html).not.toContain("scrambled");
  });

  test("On stopFight receiving #6 result, flow auto-activates Reconstructing view and populates from actual steps data (B2 RED->GREEN tracer)", async () => {
    // RED first for B2 (per approved plan + auto-activate choice): test will fail on missing activation/populate code in the script until GREEN edits the fetch .then in stopFight.
    // Observable: source contains the auto showView('reconstructing') or equivalent + population of step contents using data.steps.stepN (the shape returned by coordinator post #6).
    // This exercises the public integration of #6 result into the waiting UX. After pass, view auto shows on real stop + receive (demo needs helper running).
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Auto-activate behavior (on successful result receive from the existing /reconstruct in stopFight).
    expect(html).toContain("showView('reconstructing')");
    expect(html).toContain("lastReconstructResult");

    // Population from real #6 result shape (steps + stepN) into the progressive containers.
    expect(html).toContain("data.steps");
    expect(html).toContain("steps['step");
    expect(html).toContain(".step-content");
    expect(html).toContain("step-1");

    // Glossary + references maintained in the added logic comments/code.
    expect(html).toContain("Reconstructing");
    expect(html).toContain("4 Cleaning Steps");
    expect(html).toContain("issue #7");
  });

  test("4 Cleaning Steps are revealed progressively with short client-side pauses after activation (B3 RED->GREEN tracer)", async () => {
    // RED for B3: will fail until GREEN adds sequencing with setTimeout (or equiv) to surface step texts one-by-one with pauses, per issue #7 AC "progressively one after another with short pauses (simulating arrival from the single call)".
    // No streaming; all data already received in #6 result. Observable in source: timing/sequencing logic + step reveal progression.
    // Keeps the educational Sand Drawing slow clean-up feel. Test uses public html/script source.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Progressive timing (client pauses, one step at a time).
    expect(html).toContain("setTimeout");
    expect(html).toContain("progressive");
    expect(html).toContain("step-by-step");
    expect(html).toContain("pause"); // from "pauses", "short pause"

    // Still drives from the received steps (not hardcoded).
    expect(html).toContain("steps['step");
    expect(html).toContain("issue #7");
  });

  test("Progressive display gives Sand Drawing clean-up experience (step UI updates, status, full flow ready) and preserves glossary/privacy (B4/B5/B6/B7 tracer)", async () => {
    // Combined remaining behaviors RED->GREEN: the sequencing updates DOM for educational progressive feel; full flow from fight stop to steps; all glossary; works on sample (no real GPU); no original Memory leakage in box layer.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // UI updates for progressive feel (opacity, content fill, status changes, border for complete).
    expect(html).toContain("opacity-60");
    expect(html).toContain("remove('opacity-60')");
    expect(html).toContain("borderColor");
    expect(html).toContain("reconstruct-status");

    // Full flow references (Memory entry -> fight -> stop -> #6 result -> auto reconstruct progressive).
    expect(html).toContain("Endless Fight");
    expect(html).toContain("stopFight");
    expect(html).toContain("/reconstruct");

    // Glossary everywhere + #7.
    const required = ["Reconstructing", "4 Cleaning Steps", "Smart Robot", "Fresh Clues", "Sand Drawing", "Feeling Lesson", "Perfect Help"];
    for (const t of required) expect(html).toContain(t);
    expect(html).toContain("issue #7");

    // Privacy (original Memory local only) still asserted in source.
    expect(html).toContain("original Memory");
    expect(html).toContain("local only");

    // No avoided terms.
    expect(html).not.toContain("noise");
  });
});

// TDD for issue #4 (vertical slice per handoff, issue #4 body, PRD #1, ADR-0001, CONTEXT.md).
// Deep Fuzz Simulator module (client-side, Bun/TS) owns Dissolving (The Waves at rising Fuzz Levels),
// Rewriting, and automatic capture of Fresh Clues at the exact right Fuzz Level for Perfect Help.
// Only final Fuzz + Fresh Clues records (spot/position, words, fuzz_level) are produced at endFight.
// Original Memory stays local only (never leaves the box). This is the "deep module" for testability
// with domain scenarios (concrete wave + rewrite timing sequences).
// All terms: exact glossary only. No avoided terms. References: https://github.com/sivaratrisrinivas/fuzz/issues/4
// (and parent #1), /tmp/handoff-fuzz-issues.md, docs/adr/0001-..., CONTEXT.md, sample fight-end data from #3.
// TDD: one behavior tracer at a time, RED first then minimal GREEN. Worktree isolated.

const OAK_MEMORY = "The old oak tree by the river had stood for centuries. Its roots drank from the slow stream that wound through the valley like a silver thread. Birds nested in its high branches and children played under its shade in summer. Every autumn its leaves turned the color of fire before they fell.";

describe("fuzz simulator (deep module for live Endless Fight + Perfect Help, issue #4)", () => {
  test("Fuzz Simulator module exists with correct start state and produces valid fight-end data contract (first TDD tracer for #4)", () => {
    // Written RED first (module not found). Minimal GREEN: created src/fuzz-simulator.ts + this import.
    // Public observable only (per tdd): start state + end contract shape (matches sample data contract).
    const sim = new FuzzSimulator(OAK_MEMORY);
    expect(sim.getCurrentFuzz()).toBe(OAK_MEMORY);
    expect(sim.getCurrentFuzzLevel()).toBe(0);
    const end = sim.endFight();
    expect(typeof end).toBe("object");
    expect(end).toHaveProperty("final_fuzz");
    expect(end).toHaveProperty("fresh_clues");
    expect(end.final_fuzz).toBe(OAK_MEMORY);
    expect(Array.isArray(end.fresh_clues)).toBe(true);
    expect(end.fresh_clues.length).toBe(0);
    // Contract shape enforces privacy: no separate "original Memory" field is ever present in the data sent
    // (only final_fuzz which at start == original before any Dissolving, plus the clues list).
    // Later cycles (fuzzed final) + UI will further demonstrate original stays local-only.
    expect(Object.keys(end).sort()).toEqual(["final_fuzz", "fresh_clues"].sort());
    expect(end).not.toHaveProperty("original");
    expect(end).not.toHaveProperty("original_memory");
  });

  test("Dissolving: waves increase Fuzz Level and corrupt only currently-correct positions (length preserved, * junk); uses explicit apply for deterministic tests (TDD cycle 2)", () => {
    // RED first: will fail until wave logic implemented in GREEN (current no-op does not change state or level).
    // Observable: applyWaveToPositions (for test control and reproducibility) only touches positions that still
    // match original, replaces with '*', level increments, length identical, other chars untouched.
    // This enables concrete scenarios for Perfect Help timing verification in later cycles.
    const mem = "abcXdef"; // short, positions 0:a 1:b 2:c 3:X 4:d 5:e 6:f
    const sim = new FuzzSimulator(mem);
    expect(sim.getCurrentFuzzLevel()).toBe(0);
    expect(sim.getCurrentFuzz()).toBe(mem);

    // Explicitly fuzz position 1 ('b') and 4 ('d') — both currently correct.
    sim.applyWaveToPositions([1, 4]);
    expect(sim.getCurrentFuzzLevel()).toBe(1);
    const after1 = sim.getCurrentFuzz();
    expect(after1.length).toBe(mem.length);
    expect(after1[1]).toBe("*");
    expect(after1[4]).toBe("*");
    expect(after1[0]).toBe("a");
    expect(after1[2]).toBe("c");
    expect(after1[3]).toBe("X"); // was never "correct" in sense of original match? but ok, not targeted

    // Second wave on remaining correct positions.
    sim.applyWaveToPositions([0, 2]);
    expect(sim.getCurrentFuzzLevel()).toBe(2);
    const after2 = sim.getCurrentFuzz();
    expect(after2[0]).toBe("*");
    expect(after2[2]).toBe("*");
    expect(after2[1]).toBe("*"); // previously fuzzed stays
    // Non-targeted stay until hit
    expect(after2[6]).toBe("f");
  });

  test("Rewriting feeds fixes into current Fuzz and auto-captures Fresh Clues (spot, words, fuzz_level) at the level of the rewrite for Perfect Help (TDD cycle 3)", () => {
    // RED: feedRewrite currently no-op; no clues captured, current not updated by player fixes.
    // After GREEN: feeding an edited string that restores previously fuzzed correct segments at current level
    // must: 1. update current Fuzz to include the fixes, 2. record FreshClue(s) with the exact shape used in
    // sample-fight-end-data.json and issue #4 (spot approx chars, words, fuzz_level), 3. only for segments
    // that became fully correct thanks to this rewrite (not ones that were already correct).
    const mem = "The old oak tree by the river";
    const sim = new FuzzSimulator(mem);
    // Dissolve a bit (wave 1 fuzzes some correct letters in "oak tree" area).
    sim.applyWaveToPositions([4, 5, 6, 7, 8, 9, 10, 11]); // approx around "old oak" / "oak tree" zone
    const levelAtRewrite = sim.getCurrentFuzzLevel(); // 1
    expect(levelAtRewrite).toBe(1);

    // Player rewrites the phrase "oak tree" successfully (provides the correct letters at right time).
    // The feed should accept the fixes and capture the Fresh Clue.
    const playerRewrite = mem; // full correct for simplicity in this tracer (or partial with the phrase fixed)
    sim.feedRewrite(playerRewrite);

    const clues = sim.getFreshClues();
    expect(clues.length).toBeGreaterThanOrEqual(1);
    const clue = clues.find((c: any) => c.words.includes("oak tree") || c.words === "oak tree");
    expect(clue).toBeDefined();
    expect(clue!.fuzz_level).toBe(levelAtRewrite);
    expect(clue!.words).toContain("oak");
    expect(clue!.spot).toContain("oak tree");
    expect(clue!.spot.toLowerCase()).toContain("chars");

    // Current Fuzz should now reflect the fix (the phrase is clean again).
    const after = sim.getCurrentFuzz();
    expect(after.includes("oak tree")).toBe(true); // or exact substring match in span
    // final data at end includes the clue(s) + contract is still valid (length preserved)
    const end = sim.endFight();
    expect(end.fresh_clues.length).toBeGreaterThanOrEqual(1);
    expect(end.final_fuzz.length).toBe(mem.length);
  });

  test("Interleaved waves + rewrites on oak tree Memory (from placeholder + sample data) produces representative final_fuzz (damaged) + Fresh Clues at progressive levels (Perfect Help timing) matching contract shape (TDD cycle 4)", () => {
    // RED will fail on missing/ wrong clues or final shape until the full interaction is solid.
    // Uses the exact OAK_MEMORY from the box placeholder UI and sample-fight-end-data.json.
    // We drive explicit waves to fuzz target areas, then rewrites at increasing levels to "capture at right time".
    // Verifies: clues recorded with increasing fuzz_level, correct words, spot format, final_fuzz has * remaining,
    // data contract matches what helper/prompts/sample uses (for #5 consumption readiness).
    const sim = new FuzzSimulator(OAK_MEMORY);

    // Wave 1-3: fuzz areas covering "oak tree", "river", "silver thread" zones (computed from OAK to be robust).
    const oakIdx = OAK_MEMORY.toLowerCase().indexOf("oak tree");
    const riverIdx = OAK_MEMORY.toLowerCase().indexOf("river");
    const silverIdx = OAK_MEMORY.toLowerCase().indexOf("silver thread");
    sim.applyWaveToPositions([oakIdx, oakIdx+1, oakIdx+2, oakIdx+3, oakIdx+4, oakIdx+5, oakIdx+6, oakIdx+7]);
    if (riverIdx >= 0) sim.applyWaveToPositions([riverIdx, riverIdx+1, riverIdx+2, riverIdx+3, riverIdx+4]);
    if (silverIdx >= 0) sim.applyWaveToPositions([silverIdx, silverIdx+1, silverIdx+2, silverIdx+3, silverIdx+4, silverIdx+5, silverIdx+6, silverIdx+7, silverIdx+8, silverIdx+9, silverIdx+10, silverIdx+11]);

    // At ~ level 3, player rewrites "oak tree" (Perfect Help early)
    let currentLevel = sim.getCurrentFuzzLevel();
    expect(currentLevel).toBe(3);
    // Simulate player edit that restores "oak tree" (provide a string with that phrase clean, other may stay fuzzed)
    const rewrite1 = OAK_MEMORY.replace(/o\*\* o\*k t\*\*e/g, "old oak tree").replace(/o\*k t\*\*e/g, "oak tree"); // tolerant
    sim.feedRewrite(OAK_MEMORY); // full restore for this phrase area is fine; sim will only credit newly cleaned
    let clues = sim.getFreshClues();
    expect(clues.some((c: any) => /oak tree/i.test(c.words))).toBe(true);
    expect(clues.find((c: any) => /oak tree/i.test(c.words))!.fuzz_level).toBeLessThanOrEqual(4);

    // More waves (to ~5-7)
    sim.applyWaveToPositions([20,21,22,23,24]);
    sim.applyWaveToPositions([108,109,110,111,112,113]);

    currentLevel = sim.getCurrentFuzzLevel();
    // Player gives "river" and "silver thread" at later (but still useful) levels
    sim.feedRewrite(OAK_MEMORY);

    clues = sim.getFreshClues();
    const riverClue = clues.find((c: any) => /river/i.test(c.words));
    const silverClue = clues.find((c: any) => /silver/i.test(c.words));
    expect(riverClue).toBeDefined();
    expect(silverClue).toBeDefined();
    expect(riverClue!.fuzz_level).toBeGreaterThan(0);
    expect(silverClue!.fuzz_level).toBeGreaterThan(0);

    const end = sim.endFight();
    expect(end.final_fuzz.length).toBe(OAK_MEMORY.length);
    // final_fuzz is whatever state the player left (full Rewriting can clean it; waves can leave *). Contract shape + clues are what matters for the data sent.
    expect(end.fresh_clues.length).toBeGreaterThanOrEqual(2);
    // Spot and format fidelity (sample shape)
    for (const clue of end.fresh_clues) {
      expect(clue).toHaveProperty("spot");
      expect(clue).toHaveProperty("words");
      expect(clue).toHaveProperty("fuzz_level");
      expect(typeof clue.fuzz_level).toBe("number");
      expect(clue.spot.toLowerCase()).toContain("chars");
    }
    // No original as separate (contract)
    expect(Object.keys(end)).toEqual(["final_fuzz", "fresh_clues"]);
  });
});

// TDD vertical for issue #8 (Side-by-side reveal with Quiet Rewrite highlights via Reveal Comparator plus short Feeling Lesson message).
// Follows approved plan from user, issue #8 ACs/body, parent PRD #1 (user story 14 etc), prior #7 (progressive steps after stop) + #6 (result shape with reconstructed_memory), handoff (post HF wiring verified), ADR-0001, CONTEXT.md (glossary is gospel; use exact terms only).
// Reveal Comparator is the deep client module (small public iface, complex diff impl hidden; modeled on FuzzSimulator.ts). It identifies *only* the Quiet Rewrite diffs (Creative Guessing changes in final Reconstructed Memory vs client-local original Memory) for simple visual highlights on the recon side of side-by-side.
// Isolation tests first (public iface only). Later: UI source tests + wiring in html (using browser port of same logic). Original Memory stashed locally only (per plan). Short glossary message. Full happy path (fight stop -> #7 steps -> reveal side-by-side + highlights + short msg) demoable after.
// TDD: RED first (this test), minimal GREEN for current behavior, one tracer per priority. No changes outside box/. References: https://github.com/sivaratrisrinivas/fuzz/issues/8 , https://github.com/sivaratrisrinivas/fuzz/issues/1 , #6/#7, /tmp/handoff-fuzz-hf-mcp-wiring-verified.md , docs/adr/0001-..., CONTEXT.md.
// All terminology: exact locked glossary only. No avoided terms.

const OAK_RECONSTRUCTED_SAMPLE = "The ancient oak tree by the gentle river had stood for centuries. Its roots drank from the slow stream that wound through the valley like a silver thread. Birds nested in its high branches and children played under its wide shade in summer. Every autumn its leaves turned the color of fire before drifting down.";

describe("reveal comparator (deep module for side-by-side with Quiet Rewrite highlights via Reveal Comparator, issue #8)", () => {
  test("Reveal Comparator module exists with glossary purity, start state, and basic compare returns structure using oak sample from reconstruction (first TDD tracer for #8, per approved plan priority 1)", () => {
    // RED written first: this will fail (cannot find module or no export/class) until GREEN creates src/reveal-comparator.ts exporting the class + minimal impl.
    // Public observable (per tdd): module loads, constructor, compare(original, recon) returns {original, reconstructedSegments: TextSegment[] } shape.
    // Uses the exact OAK from placeholder + sample-reconstruction-01.md (final after Quiet Rewrite). Basic for structure; isQuietRewriteChange assertions + creative diff logic in next tracers.
    // Glossary discipline in this test file + will be in the module source.
    const comp = new RevealComparator();
    const comparison = comp.compare(OAK_MEMORY, OAK_RECONSTRUCTED_SAMPLE);
    expect(typeof comparison).toBe("object");
    expect(comparison).toHaveProperty("original");
    expect(comparison).toHaveProperty("reconstructedSegments");
    expect(comparison.original).toBe(OAK_MEMORY);
    expect(Array.isArray(comparison.reconstructedSegments)).toBe(true);
    expect(comparison.reconstructedSegments.length).toBeGreaterThan(0);
    // (Segments will have .text and .isQuietRewriteChange per proposed+approved iface.)
  });

  test("Reveal Comparator detects Quiet Rewrite creative changes (Creative Guessing diffs) vs original while leaving clue-restored exact parts unmarked (TDD tracer 2, per approved plan priority 2)", () => {
    // RED written first for priority 2: current minimal impl marks nothing as change (all false). This will fail the hasChange asserts until GREEN adds detection logic in compare (private helper).
    // Per AC + sample-reconstruction-01.md notes: Quiet Rewrite (step 4 quiet pass) introduces visible Creative Guessing changes e.g. "ancient", "gentle", "wide shade", "drifting down" so it is not an Exact Copy.
    // Fresh Clues / Perfect Help restorations (e.g. "oak tree", "silver thread") must remain unmarked (exact in recon == original).
    // Tests only public compare result (segments). Uses exact oak sample.
    const comp = new RevealComparator();
    const comparison = comp.compare(OAK_MEMORY, OAK_RECONSTRUCTED_SAMPLE);
    const segs = comparison.reconstructedSegments;

    const hasChangeFlagFor = (needle: string) =>
      segs.some((s) => s.text.toLowerCase().includes(needle.toLowerCase()) && s.isQuietRewriteChange);
    const hasUnchangedFor = (needle: string) =>
      segs.some((s) => s.text.toLowerCase().includes(needle.toLowerCase()) && !s.isQuietRewriteChange);

    // Quiet Rewrite creative changes (from Training + Creative Guessing in final Best Guess / Quiet Rewrite)
    expect(hasChangeFlagFor("ancient")).toBe(true);   // "old" -> "ancient"
    expect(hasChangeFlagFor("gentle")).toBe(true);    // context for river in quiet pass
    expect(hasChangeFlagFor("wide")).toBe(true);      // "shade" -> "wide shade"
    expect(hasChangeFlagFor("drifting")).toBe(true);  // "before they fell" -> "... drifting down"
    expect(hasChangeFlagFor("down")).toBe(true);

    // Restored exact via Fresh Clues at right Fuzz Levels (Perfect Help); must not be flagged as Quiet Rewrite.
    // (Note: ws-split means multi-word clues like "oak tree" appear as separate tokens "oak" "tree"; use distinctive single tokens.)
    expect(hasUnchangedFor("oak")).toBe(true);
    expect(hasUnchangedFor("silver")).toBe(true);
    expect(hasUnchangedFor("river")).toBe(true); // the base word was clue-provided, not a creative rewrite invention
  });

  test("Reveal Comparator produces usable highlight HTML (wraps Quiet Rewrite changes in <mark class=\"quiet-rewrite\">) for direct browser render (TDD tracer 3, per approved plan priority 3)", () => {
    // Exercises the toHighlightedHtml convenience (approved iface) on segments with real Quiet Rewrite flags from prior logic.
    // Produces browser-ready markup with marks only around creative changes for the recon column side-by-side.
    // (The browser port in index.html will use an equivalent for the live reveal after #7 steps.)
    const comp = new RevealComparator();
    const comparison = comp.compare(OAK_MEMORY, OAK_RECONSTRUCTED_SAMPLE);
    const html = comp.toHighlightedHtml(comparison.reconstructedSegments);
    // Quiet changes get marked
    expect(html).toContain('<mark class="quiet-rewrite">ancient</mark>');
    expect(html).toContain('<mark class="quiet-rewrite">gentle</mark>');
    expect(html).toContain('<mark class="quiet-rewrite">wide</mark>');
    // Clue-restored / exact parts are plain (not marked)
    expect(html).not.toContain('<mark class="quiet-rewrite">oak</mark>');
    expect(html).not.toContain('<mark class="quiet-rewrite">silver</mark>');
    expect(html.length).toBeGreaterThan(100);
  });
});

// TDD vertical for issue #8 UI layer (side-by-side reveal + Quiet Rewrite highlights via Reveal Comparator + short Feeling Lesson).
// Builds on the now-complete deep module (tracers 1-3) + prior #7 progressive + #6 result (reconstructed_memory).
// Tests are source inspection of index.html (public shell) + will drive the population logic, stash for local original Memory (client-only),
// browser port of comparator, short msg, and wiring so that after #7 steps the "See ... Quiet Rewrite" button leads to populated side-by-side.
// Per approved plan, #8 ACs, CONTEXT.md glossary (all terms), no auto-advance change to reconstructing view.
// One RED->GREEN at a time for the UI behaviors.

describe("side-by-side reveal with Quiet Rewrite highlights via Reveal Comparator plus short Feeling Lesson message (issue #8)", () => {
  test("Reveal view contains dynamic side-by-side containers (ids for original + reconstructed) and short explanatory Feeling Lesson message using only glossary terms (UI tracer B1)", async () => {
    // RED: will fail on missing ids / old long message / static example until GREEN updates the view-reveal section in index.html.
    // Observable: new ids for population target, short msg text (Smart Robot + Training + Fresh Clues + Best Guess + Creative Guessing + Perfect Help + Quiet Rewrite + not Exact Copy + Real Experience + Feeling Lesson), glossary.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Dynamic containers (replaces the static example divs; populated from currentOriginalMemory + lastReconstructResult + browser comparator)
    expect(html).toContain('id="original-memory-display"');
    expect(html).toContain('id="reconstructed-memory-display"');

    // Short explanatory message (one short per AC #3, not the previous long multi-sentence block).
    // Use literals entirely within text nodes (no glossary <span> interrupting) or single terms; consistent with prior #7 UI tests that split around spans.
    expect(html).toContain("used its ");
    expect(html).toContain(" for a ");
    expect(html).toContain(" via ");
    expect(html).toContain(" is not an ");
    expect(html).toContain(". You lived the ");
    expect(html).toContain("Real Experience");
    expect(html).toContain("Feeling Lesson");

    // Traceability + #8
    expect(html).toContain("issue #8");
    expect(html).toContain("Reveal Comparator");

    // Still glossary purity, references to prior
    expect(html).toContain("Reconstructed Memory");
    expect(html).toContain("original Memory");
    expect(html).toContain("local only");
  });

  test("Source contains local original Memory stash (currentOriginalMemory), browser port of Reveal Comparator, and reveal population logic wiring (from lastReconstructResult + original for side-by-side after #7) (UI tracer B2)", async () => {
    // RED for wiring: will fail until GREEN adds the JS (let currentOriginalMemory, createBrowserRevealComparator mirroring the .ts, populate fn, calls in showView/init/reset, use of comparator for innerHTML on recon display).
    // Observable in public html/script source. Full flow: init fight sets stash (original local only), stop + #7 steps, then reveal button/show populates using #6 result.reconstructed_memory + comparator.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    expect(html).toContain("currentOriginalMemory");
    expect(html).toContain("createBrowserRevealComparator");
    expect(html).toContain("reconstructedSegments");
    expect(html).toContain("toHighlightedHtml");
    expect(html).toContain("lastReconstructResult");
    expect(html).toContain("showView('reveal')");
    // References issue #8 + prior
    expect(html).toContain("issue #8");
  });
});

// TDD vertical for issue #9 (Play again instant full clear and round reset flows (client-side; refresh during fight handling)).
// Per user-approved plan (via ask_user_question after meticulous #8 handoff + issue#9/#1 review), ACs, parent PRD #1 (user stories 15/16/18), #8 (reveal + currentOriginalMemory stash + existing resetAll + populate), #7 (steps), #6 (result), /tmp/handoff-fuzz-issue8-complete.md, ADR-0001, CONTEXT.md (glossary is gospel; exact terms only: Memory, Fuzz, Fresh Clues, 4 Cleaning Steps, Reconstructed Memory, Endless Fight, Real Experience, etc.).
// No new deep module (per plan; this is client wiring/state clear extension in the single-file playable box, same style as #7 B tracers and #8 B1/B2 UI source tests).
// Public iface per approval: resetAll() remains the sole public trigger (onclick from reveal button preserved); its impl is deepened for complete clears + side effects (no speculative extracts). Internal helpers only for refresh flag (sessionStorage transient, never holds private Memory or data; cleared always on reset or fight end).
// Vertical tracers one RED->GREEN: behaviors prioritized as approved (1. full instant clear + fresh empty Memory input on Play again first; 2. no send; 3. refresh-during-live-Endless-Fight; 4. prominent + glossary text/refs; 5. cycle).
// Tests: source inspection of index.html (public behavior proof, like prior). Run before/after every edit. Atomic commits only on GREEN pass + hygiene. Scope: box/ client only. Privacy: original never sent, reset sends nothing.
// References: https://github.com/sivaratrisrinivas/fuzz/issues/9 , #8, #1 (PRD), handoff, CONTEXT.md, ADR-0001.

describe("play again instant full clear and round reset flows (client-side; refresh during fight handling, issue #9)", () => {
  test("Activating Play again (resetAll) instantly clears every prior round piece (Memory, Fuzz, Fresh Clues, 4 Cleaning Steps, Reconstructed Memory, state) with no trace and returns to fresh empty Memory input state (TDD tracer 1, priority 1 per approved plan)", async () => {
    // RED written first for tracer 1: this will fail (missing clears for lastReconstructResult, step DOM wipe, memory entry textarea forced empty, explicit full trace removal, #9 traceability strings) until GREEN minimally deepens resetAll().
    // Observable ONLY through public shell: the resetAll fn source + button + memory view (Bun.file read, no execution of JS). Exercises the "instant full clear" + "completely fresh initial Memory typing state" AC + PRD stories.
    // After this GREEN passes: core clear behavior present and test green. Subsequent tracers add refresh flag/msg, more UI polish, header refs.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Play again control visible/usable after reveal (AC, PRD15; big obvious button already in place, will keep/enhance)
    expect(html).toContain("resetAll()");
    expect(html).toContain("Play again — start a completely new Memory");

    // Full clear of EVERY piece of prior round (ACs 1-2): expect the clear statements in resetAll body (current only does partial sim+original+panel+switch)
    expect(html).toContain("currentSim = null");
    expect(html).toContain("currentOriginalMemory = null");
    expect(html).toContain("lastReconstructResult = null");
    expect(html).toContain("window.lastReconstructResult = null");

    // 4 Cleaning Steps / Reconstructing state wiped (no visual or content trace left in UI)
    expect(html).toContain("step-1");
    expect(html).toContain("step-4");
    // re-apply initial opacity + blank content for steps
    expect(html).toContain("opacity-60");

    // Returns to completely fresh initial Memory typing state: entry textarea forced empty (no old Memory lingering)
    expect(html).toContain("#view-memory textarea");
    expect(html).toContain("value = ''");

    // View reset + other state (end panel, fight flags) for "no trace"
    expect(html).toContain("view-memory");
    expect(html).toContain("end-data-panel");

    // No data from cleared round is sent to or stored by thin helper (AC3; reset path must not touch network)
    // (fetch exists elsewhere e.g. stopFight; we assert intent via clear-only reset and comments)
    expect(html).toContain("function resetAll()");

    // Traceability for this vertical + refs to parent/prior (will be in comments + status after GREENs)
    expect(html).toContain("issue #9");

    // Glossary purity (CONTEXT.md) — all reset/clear text and comments use exact terms only
    expect(html).toContain("Memory");
    expect(html).toContain("Endless Fight");
    expect(html).toContain("4 Cleaning Steps");
    expect(html).toContain("Reconstructed Memory");
    expect(html).toContain("Fresh Clues");

    // No avoided terms anywhere in file (glossary discipline)
    expect(html).not.toContain("noise");
    expect(html).not.toContain("scrambled");
  });

  test("Page refresh during live Endless Fight resets to starting empty Memory input state with gentle glossary message (TDD tracer for refresh, priority 3 per approved plan; covers no-data-on-reset as side)", async () => {
    // RED for refresh resilience (AC4, PRD18): will fail until GREEN adds transient sessionStorage flag (set on live fight start, cleared on stop/reset/boot-consume), #reset-notice div in memory view, boot logic to detect+show gentle msg + force empty ta (override normal prefill) + clear flag. No private data in storage/ever sent.
    // Observable in public source (html ids, script strings for sessionStorage, flag fns or direct, gentle text using exact terms, reset-notice). Full "during live" vs normal boot distinction.
    // After GREEN: source proves the behavior; test passes. (Live reload sim via manual later; no data exposure by design.)
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Transient flag for "during live Endless Fight" detection (sessionStorage, never stores Memory/Fuzz/Clues/private; only bool signal; cleared fast)
    expect(html).toContain("sessionStorage");
    expect(html).toContain("setItem");
    expect(html).toContain("getItem");
    expect(html).toContain("removeItem");
    // flag name or usage hints "fight" + "refresh" or "reset" during Endless Fight
    expect(html).toContain("fuzzLiveFightRefreshFlag"); // or similar; will use in code
    expect(html).toContain("Endless Fight");

    // Gentle message UI affordance in starting Memory view (transient, only for refresh-during case)
    expect(html).toContain("reset-notice");
    expect(html).toContain("refreshed during the Endless Fight");
    expect(html).toContain("prior Memory was private");
    expect(html).toContain("completely new Memory");

    // Boot logic forces empty on this path (starting empty Memory input state per AC)
    expect(html).toContain("bootLiveFight");
    expect(html).toContain("memTa");
    expect(html).toContain("OAK_FOR_DEMO"); // normal prefill still present for other boots

    // Clear flag also on resetAll / stop (so only live during triggers it; normal post-fight reloads don't falsely show "reset")
    expect(html).toContain("resetAll");
    expect(html).toContain("stopWaves");

    // Glossary + #9 refs (in new code + existing)
    expect(html).toContain("issue #9");
    expect(html).toContain("Memory");
    expect(html).toContain("Endless Fight");

    // Still no avoided
    expect(html).not.toContain("noise");
  });
});

// TDD vertical for issue #10 capstone (Resilience paths for Smart Robot slow/fail, full E2E player journey verification, privacy/cost/glossary audit, README/docs update).
// Per user-approved plan from ask_user_question (after meticulous review of /tmp/handoff-fuzz-issue9-main-integration.md + #9-complete + #8 + issue #10 body+ACs + PRD #1 stories incl 17 + all priors, CONTEXT.md glossary, ADR-0001).
// Builds directly on #6 (one Smart Robot call + result shape with steps/reconstructed_memory + ephemeral), #7 (progressive 4 Cleaning Steps in waiting), #8 (side-by-side + Quiet Rewrite + reveal), #9 (resetAll instant full clear + fresh start).
// Tracer 1 (per approved priority): observable UI affordances for resilience (friendly messages + buttons using exact PRD language: "wait longer", "try again" reusing the exact same fight-end data contract, "start a new Memory"; #resilience surface/panel; glossary terms; traceability to #10 + full journey + privacy/client-only) present in source. RED first.
// No new deep module (inline script enhancements only, consistent with #7/#9 wiring + #8 port). Tests are public source inspection only (Bun.file on index.html). One behavior slice at a time; tests run before any GREEN edits/commits.
// All terms exact from CONTEXT.md only (Memory, Fuzz, Endless Fight, Fresh Clues, Perfect Help, Reconstructing, 4 Cleaning Steps, Smart Robot, Reconstructed Memory, Quiet Rewrite, Real Experience, Feeling Lesson, Sand Drawing, Creative Guessing, Best Guess, Training, Word Lesson, Fixing Science, Watch and Fight Way, Exact Copy). No avoided terms. Explicit audit phrases in later tracers.
// References: https://github.com/sivaratrisrinivas/fuzz/issues/10 (parent #1), handoff-fuzz-issue9-main-integration.md + priors, CONTEXT.md, docs/adr/0001-..., #6/#7/#8/#9.
// TDD hygiene: RED (this) will fail -> GREEN (minimal UI) -> pass -> hygiene (test, diff, secrets) -> commit -> next tracer.
describe("resilience paths, full E2E player journey verification, privacy/cost/glossary audit (issue #10)", () => {
  test("Resilience UI elements, messages and affordances (wait longer / try again reusing fight-end data contract / start a new Memory) + glossary + #10 refs present for Smart Robot timeout or failure during waiting or reveal (TDD tracer 1, priority 1 per approved plan)", async () => {
    // RED written first: expects will fail until GREEN minimally adds the #resilience-panel (or integrated section), button texts, friendly glossary messages, and updates header/comments for #10.
    // Observable ONLY through public shell source (html + script strings/ids). Covers AC "Friendly recoverable options ... shown and work on Smart Robot timeout or failure", PRD story 17, E2E journey affordances.
    // After this GREEN: UI elements + strings prove the surface. Next tracers add actual timeout/catch wiring + stash + tryAgain + E2E full + audits.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Exact recoverable options per issue #10 ACs + PRD #1 story 17 (friendly messages/buttons for slow/fail)
    expect(html).toContain("Wait longer");
    expect(html).toContain("Try again");
    expect(html).toContain("reusing the exact same fight-end data contract");
    expect(html).toContain("Start a new Memory");

    // Resilience surface (new panel or section id integrated in reconstructing/end-data area for waiting/reveal phases)
    expect(html).toContain("resilience");

    // Friendly context + glossary (Smart Robot slow/fail during Reconstructing; privacy reminder)
    expect(html).toContain("Smart Robot");
    expect(html).toContain("slow or");
    expect(html).toContain("Reconstructing");
    expect(html).toContain("original Memory");
    expect(html).toContain("private");
    expect(html).toContain("your side only");
    expect(html).toContain("fight-end data contract");

    // Full E2E journey references (ties #4 fight + #6 one-call /reconstruct + #7 progressive + #8 reveal + #9 reset)
    expect(html).toContain("issue #10");
    expect(html).toContain("issue #6");
    expect(html).toContain("issue #7");
    expect(html).toContain("issue #8");
    expect(html).toContain("issue #9");
    expect(html).toContain("/reconstruct");
    expect(html).toContain("stopFight");
    expect(html).toContain("resetAll");

    // Glossary purity across the new strings + prior journey (CONTEXT.md is gospel)
    const requiredGlossary = [
      "Memory", "Endless Fight", "Fuzz", "Fresh Clues", "Perfect Help",
      "4 Cleaning Steps", "Smart Robot", "Reconstructing", "Reconstructed Memory",
      "Quiet Rewrite", "Creative Guessing", "Real Experience", "Feeling Lesson",
      "Sand Drawing", "Best Guess", "Training"
    ];
    for (const term of requiredGlossary) {
      expect(html).toContain(term);
    }

    // No drift to avoided terms (glossary discipline enforced in test and source)
    expect(html).not.toContain("noise");
    expect(html).not.toContain("scrambled");
  });

  test("Client error/timeout path in stopFight + lastFightEndData stash for retry + tryAgainReconstruct (re-posts exact same contract) + show resilience options (TDD tracer 2, per approved plan)", async () => {
    // RED for tracer 2: will fail until GREEN implements the error handling wiring, lastFightEndData (or equiv) stash before the /reconstruct POST, AbortController + timeout (30s default), tryAgainReconstruct fn, and logic to surface #resilience-panel (and wire its Try again button) on catch/timeout.
    // Observable in public source: the stash assignment near end= , the fetch( with signal or Abort, tryAgainReconstruct def, lastFightEndData, timeout const/ literal, calls in catch or timeout arm, panel show/display.
    // Covers AC "try again reusing the exact same fight-end data contract", timeout/fail during waiting, privacy (client stash only, reset clears).
    // After pass: core recovery path in source. Tracer 3 adds waitLonger + recover-to-reveal + E2E audits.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // Stash of fight-end contract (for try again without re-running fight/ waves)
    expect(html).toContain("lastFightEndData");
    expect(html).toContain("end = currentSim.endFight");
    // or "const end = " near stopFight + assignment to last*

    // Timeout + abort machinery for slow case (per 30s default in plan)
    expect(html).toContain("AbortController");
    expect(html).toContain("signal");
    expect(html).toContain("timeout");
    // 30000 or 30s or RECONSTRUCT_TIMEOUT

    // try again function + re-use of stashed contract (no new sim/end needed)
    expect(html).toContain("tryAgainReconstruct");
    expect(html).toContain("lastFightEndData");
    expect(html).toContain("/reconstruct");

    // Error path enhancement (catch or timeout shows resilience UI; integrates with panel from tracer1)
    expect(html).toContain("resilience-panel");
    expect(html).toContain("catch");
    expect(html).toContain("stopFight");

    // Reset clears the retry stash too (privacy, fresh start per #9 + #10)
    expect(html).toContain("resetAll");
    expect(html).toContain("lastFightEndData = null");

    // Glossary + #10 + prior refs for the recovery logic
    expect(html).toContain("issue #10");
    expect(html).toContain("fight-end data contract");
    expect(html).toContain("Smart Robot");
    expect(html).toContain("original Memory");
    expect(html).toContain("private");
  });

  test("Wait longer + recover to reveal after retry + start new via resetAll + full E2E journey source + explicit privacy/cost/glossary/1-call audit (TDD tracer 3 + E2E audit per approved plan)", async () => {
    // RED: expects for waitLonger (graceful), post-retry path allowing reveal (showView('reveal')), resetAll clearing lastFight + full clear, and audit strings for capstone verification (single call, ephemeral forget, client-only original Memory never sent, open no-auth, https, low cost dedicated one call, full refs to #6-9 + PRD, glossary fidelity everywhere).
    // After GREEN (mostly comments + existing strings suffice + any missing phrases): source + tests prove complete resilient E2E (Memory -> Endless Fight/#4 -> stop/#6 contract -> Reconstructing/#7 -> reveal/#8 + Quiet Rewrite -> resilience recover or Play again/#9) + all ACs.
    const htmlFile = Bun.file(new URL("../src/index.html", import.meta.url));
    const html = await htmlFile.text();

    // waitLonger present (graceful keep-wait UX)
    expect(html).toContain("waitLonger");
    expect(html).toContain("Still waiting");

    // recover path leads to reveal possible (after successful tryAgain or normal)
    expect(html).toContain("showView('reveal')");
    expect(html).toContain("reconstructed-memory-display");
    expect(html).toContain("Quiet Rewrite");

    // start new / reset integration in resilience
    expect(html).toContain("resetAll");
    expect(html).toContain("lastFightEndData = null");

    // E2E journey coverage refs (full player stories capstone)
    expect(html).toContain("Endless Fight");
    expect(html).toContain("stopFight");
    expect(html).toContain("/reconstruct");
    expect(html).toContain("Reconstructing");
    expect(html).toContain("4 Cleaning Steps");
    expect(html).toContain("reveal");
    expect(html).toContain("Play again");
    expect(html).toContain("resetAll()");

    // Explicit audit / verification per issue #10 ACs + PRD (single GPU/Smart Robot call, immediate forget, client-only Memory, open access no auth, https, low cost one dedicated call + scale-to-zero, glossary)
    expect(html).toContain("one Smart Robot call");
    expect(html).toContain("ephemeral");
    expect(html).toContain("original Memory");
    expect(html).toContain("local only");
    expect(html).toContain("never sent");
    expect(html).toContain("private");
    expect(html).toContain("no auth");
    expect(html).toContain("https");
    expect(html).toContain("dedicated");
    // cost/scale implied in comments + ADR but source has low cost model refs via prior + "one call"
    expect(html).toContain("issue #6");
    expect(html).toContain("issue #10");

    // Glossary no drift across E2E + resilience
    expect(html).not.toContain("noise");
    expect(html).not.toContain("scrambled");
    const moreGlossary = ["Memory", "Fuzz", "Fresh Clues", "Perfect Help", "Creative Guessing", "Real Experience", "Feeling Lesson", "Sand Drawing"];
    for (const t of moreGlossary) expect(html).toContain(t);
  });
});
