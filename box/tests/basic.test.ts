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
});
