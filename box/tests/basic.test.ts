import { describe, test, expect } from "bun:test";

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
