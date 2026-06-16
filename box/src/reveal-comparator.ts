/**
 * Reveal Comparator (deep module) - client-side only (Bun + TypeScript).
 *
 * Per issue #8 (Side-by-side reveal with Quiet Rewrite highlights via Reveal Comparator plus short Feeling Lesson message),
 * approved plan, parent PRD #1 (esp. user story 14), #7 (progressive 4 Cleaning Steps after stop) + #6 (reconstructed_memory in result),
 * handoff /tmp/handoff-fuzz-hf-mcp-wiring-verified.md, ADR-0001, CONTEXT.md (glossary gospel).
 *
 * The live fight box retains the original Memory locally (client-only, round duration) and uses the Reveal Comparator
 * (after the 4 Cleaning Steps) to identify only the differences introduced by the Quiet Rewrite (Creative Guessing
 * changes from the Smart Robot's Best Guess, not an Exact Copy) in the Reconstructed Memory. Simple visual highlights
 * are applied to those portions on the Reconstructed Memory side of the side-by-side. One short explanatory message
 * (glossary terms only) completes the Feeling Lesson / Real Experience.
 *
 * This is a deep module: small stable public interface (compare + toHighlightedHtml per approved iface), complex
 * internal logic for detecting Quiet Rewrite creative diffs (word/phrase alignment against original, focused on
 * step-4 quiet pass changes). Fully testable in isolation with domain examples (oak tree sample from
 * sample-reconstruction-01.md showing visible Quiet Rewrite: "ancient", "gentle river", "wide shade", "drifting down").
 *
 * The .ts + bun tests are source of truth. A browser-portable copy (pure, no imports) will live in index.html
 * <script> to keep the single-file playable demo working (consistent with FuzzSimulator pattern).
 *
 * All code, identifiers, comments, and tests use ONLY the exact locked glossary terms from CONTEXT.md:
 * Memory, Fuzz, Rewriting, Dissolving, Reconstructing, Clues, Fresh Clues, Perfect Help, Endless Fight,
 * 4 Cleaning Steps, Quiet Rewrite, Best Guess, Creative Guessing, Smart Robot, Training, Real Experience,
 * Feeling Lesson, Sand Drawing, The Waves, Fuzz Levels, Word Lesson, Fixing Science, Watch and Fight Way,
 * Exact Copy. No avoided terms anywhere.
 *
 * Vertical TDD (approved order): this file created in GREEN for first RED tracer (module + basic structure on oak sample).
 * Subsequent tracers add real Quiet Rewrite creative change detection, highlight HTML, then UI consumption.
 */

export interface TextSegment {
  text: string;
  isQuietRewriteChange: boolean;  // true only for portions changed by Creative Guessing in the Quiet Rewrite (final Best Guess, not Exact Copy)
}

export interface RevealComparison {
  original: string;
  reconstructedSegments: TextSegment[];
}

export class RevealComparator {
  /**
   * compare: given client-local original Memory and the Reconstructed Memory (from thin helper / Smart Robot one-call result),
   * return structured segments for the recon side so caller can render side-by-side and highlight only the Quiet Rewrite.
   * Original returned verbatim for left column. Deep impl (diff strategy) is private.
   */
  compare(originalMemory: string, reconstructedMemory: string): RevealComparison {
    // Now with Quiet Rewrite detection (GREEN for priority 2): uses private helper to mark only creative diffs
    // (new word tokens from Training/Creative Guessing in the Quiet Rewrite / final Best Guess).
    // Exact-matching words (incl. those restored by Fresh Clues / Perfect Help) stay unmarked (isQuietRewriteChange=false).
    // This is the core behavior for side-by-side highlight of "not an Exact Copy".
    const segments = this.computeQuietRewriteSegments(originalMemory || "", reconstructedMemory || "");
    return {
      original: originalMemory || "",
      reconstructedSegments: segments,
    };
  }

  /**
   * Deep private: word-token heuristic to surface Quiet Rewrite (Creative Guessing) changes only.
   * Collects base words present in original Memory. Any non-whitespace token in recon whose lowercased
   * form is absent from original is treated as a Quiet Rewrite creative edit (flag true). This correctly
   * highlights the sample's visible changes while leaving clue-restored exact spans unmarked.
   * (Simple, no external diff lib, sufficient and demo-friendly for the Feeling Lesson.)
   */
  private computeQuietRewriteSegments(original: string, reconstructed: string): TextSegment[] {
    const origWords = new Set(
      (original.match(/\b[\w']+\b/g) || []).map((w) => w.toLowerCase())
    );
    return reconstructed.split(/(\s+)/).filter((part) => part.length > 0).map((part) => {
      const trimmed = part.trim().toLowerCase();
      // Flag only alphabetic-ish tokens that are inventions vs the original (the Quiet Rewrite / Creative Guessing)
      const isCreativeChange = trimmed.length > 0 && /[a-z]/.test(trimmed) && !origWords.has(trimmed);
      return {
        text: part,
        isQuietRewriteChange: isCreativeChange,
      };
    });
  }

  /**
   * toHighlightedHtml: convenience for direct use in browser reveal render (innerHTML on recon column).
   * Wraps segments where isQuietRewriteChange with <mark class="quiet-rewrite"> (simple visual per AC).
   * Non-changed segments rendered as text. (Escaping minimal for now; content is controlled.)
   */
  toHighlightedHtml(segments: TextSegment[]): string {
    return segments
      .map((seg) => {
        if (seg.isQuietRewriteChange) {
          // class chosen for glossary tie-in; CSS can style later if needed (current index.html has no extra yet)
          return `<mark class="quiet-rewrite">${seg.text}</mark>`;
        }
        return seg.text;
      })
      .join("");
  }
}
