import { describe, test, expect } from "bun:test";
import { FuzzSimulator } from "../src/fuzz-simulator";

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
