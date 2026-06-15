/**
 * Live fight box dev server (Bun + TypeScript shell).
 *
 * Per ADR-0001 + issue #2: this is the runnable shell for the live fight box.
 * The box owns live Dissolving (The Waves at increasing Fuzz Levels), Rewriting,
 * capture of Fresh Clues at exact Fuzz Levels for Perfect Help, and local state for
 * original Memory (never sent). The thin helper is only the coordinator for one
 * Smart Robot Reconstructing call using the 4 Cleaning Steps.
 *
 * This server serves the placeholder UI for the four views:
 * - Memory entry (start of Sand Drawing)
 * - Endless Fight (Dissolving + Rewriting view)
 * - Waiting during Reconstructing (progressive 4 Cleaning Steps)
 * - Reveal (side-by-side with Quiet Rewrite + Feeling Lesson note)
 *
 * NO actual Dissolving simulation, no Rewriting logic, no Fuzz computation,
 * no clue timing, no Smart Robot call, no data contract yet.
 * Those are future vertical slices (#4 etc).
 *
 * All text, labels, comments use ONLY the exact glossary from CONTEXT.md.
 * See PRD #1, handoff, ADR-0001, CONTEXT.md.
 */

const PORT = 3000;

const server = Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);
    const pathname = url.pathname;

    if (pathname === "/" || pathname === "/index.html") {
      const html = await Bun.file("./src/index.html").text();
      return new Response(html, {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }

    // Future: static assets or API stubs for the box (client-only for now).
    if (pathname === "/health") {
      return Response.json({
        status: "ok",
        component: "live fight box shell",
        note: "Uses exact terms: Memory, Fuzz, Endless Fight, 4 Cleaning Steps, Quiet Rewrite, Fresh Clues, Smart Robot, Creative Guessing, Real Experience, Feeling Lesson, Sand Drawing.",
      });
    }

    return new Response(
      "Fuzz live fight box - see index.html. Per issue #4: the deep Fuzz Simulator + playable Endless Fight (Dissolving, Rewriting, Fresh Clues for Perfect Help) are now live in the browser (client only). Other views remain progressive placeholders.",
      { status: 404, headers: { "Content-Type": "text/plain" } }
    );
  },
});

console.log(`\n=== Fuzz Live Fight Box Shell ===`);
console.log(`Running at http://localhost:${server.port}`);
console.log(`Views: Memory entry | Endless Fight (The Waves) | Reconstructing (4 Cleaning Steps) | Reveal (Quiet Rewrite)`);
console.log(`All language from CONTEXT.md glossary.`);
console.log(`Press Ctrl-C to stop.\n`);

// Keep alive for dev.
process.on("SIGINT", () => {
  console.log("\nLive fight box shell stopped.");
  server.stop();
  process.exit(0);
});
