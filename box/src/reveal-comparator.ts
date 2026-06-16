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
    // GREEN for priority 1 (structure tracer): minimal impl that satisfies public contract and first test.
    // Splits on whitespace runs to produce segments (order-preserving). All marked non-change for this slice.
    // Real Quiet Rewrite detection (only Creative Guessing diffs vs original, using sample evidence like "ancient"/"gentle"/"wide shade"/"drifting")
    // will be added in next RED->GREEN (priority 2) without changing this public iface.
    const segments: TextSegment[] = (reconstructedMemory || "")
      .split(/(\s+)/)
      .filter((part) => part.length > 0)
      .map((part) => ({
        text: part,
        isQuietRewriteChange: false,
      }));

    return {
      original: originalMemory || "",
      reconstructedSegments: segments,
    };
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
