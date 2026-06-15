# Web frontend (Bun + TypeScript) + Python backend with Hugging Face dedicated Inference Endpoints (L4) for the Smart Robot

We decided on a web client-server architecture (TypeScript + Bun for the frontend, Python/FastAPI for the backend) where the live Dissolving, The Waves, Fuzz Levels, and Rewriting (including precise capture of Fresh Clues at exact Fuzz Levels for Perfect Help during the Endless Fight) execute client-side in the browser for immediacy, while the Smart Robot's Reconstructing (Best Guess using Creative Guessing, Clues + Fresh Clues, and visible Cleaning Steps) is performed remotely on a Hugging Face dedicated Inference Endpoint. The Pro subscription is used for development priority, ZeroGPU quota, and credits; the live Smart Robot path uses dedicated hourly-billed endpoints only. The lowest-cost suitable GPU tier (nvidia-l4) was selected for the endpoint.

This choice delivers rich Sand Drawing visuals and the Word Lesson/Feeling Science while meeting the hard constraint of no local GPUs and preserving the real-time fight feel required for Real Experience.

**Status**: accepted

**Considered Options**:
- Pure terminal/CLI prototype (as suggested in the initial handoff) — rejected for limiting visual metaphor strength and broader accessibility.
- Fully server-authoritative real-time loop (waves and input processed in Python) — rejected because round-trip latency would destroy the Endless Fight pressure and the "exact right time" value of Fresh Clues / Perfect Help.
- Browser-only or local ML (e.g. Transformers.js) for the Smart Robot — rejected due to the explicit no-local-GPU requirement and desire for the highest-quality Creative Guessing available via HF GPUs.

**Consequences**:
- The frontend must own a high-fidelity, deterministic client-side simulation of Dissolving and Rewriting (with accurate Fuzz Level tracking for clue timing). Clue data is batched and sent only at the end of the fight.
- The Python backend acts as thin orchestrator and clue aggregator; it calls the HF endpoint (via TGI or equivalent) only for Reconstructing rounds.
- Cost is hourly for the dedicated endpoint (kept minimal via scale-to-zero or activation only during active reconstructions) rather than burning limited monthly Pro credits on every inference.
- Visualization of progressive Cleaning Steps and the Quiet Rewrite in the Reconstructed Memory becomes a first-class UI concern.
- Future changes to the interaction surface or GPU provider will be expensive; the boundary between client fight mechanics and remote Creative Guessing is now explicit.

**GPU and inference choice rationale (credit burn minimization)**:
- Selected: Hugging Face Inference Endpoints dedicated on `nvidia-l4` (1x, 24 GB) — approximately $0.80/hour.
- This is the lowest-cost tier that comfortably runs well-quantized 7-13B text models (or diffusion LMs) with room for context and good speed. It burns far less than L40S ($1.80/hr), A100 ($2.50+/hr), or higher tiers.
- Dedicated endpoints provide consistent low latency and predictable billing without consuming the limited monthly Inference Providers credits or ZeroGPU time quota that Pro unlocks (those are reserved for rapid dev iteration, model testing, and prompt experimentation).
- For the actual player rounds, only the Reconstructing phase (post-fight) hits the endpoint, further minimizing runtime hours.