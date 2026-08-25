#!/usr/bin/env bun
/**
 * GS-T6 starring helper. Drives box/src/fuzz-simulator.ts (FuzzSimulator.applyWaveToPositions).
 * Reads JSON from stdin: { original, fuzz_level, seed, memory_id }
 * Writes JSON to stdout: { final_fuzz, fuzz_simulator_level, replaced_chars }
 */
import { FuzzSimulator } from "../box/src/fuzz-simulator.ts";

type Input = {
  original: string;
  fuzz_level: number;
  seed: number;
  memory_id: string;
};

function hashSeed(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function mulberry32(a: number): () => number {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffle(arr: number[], rng: () => number): number[] {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    const tmp = a[i];
    a[i] = a[j] as number;
    a[j] = tmp as number;
  }
  return a;
}

const input = JSON.parse(await Bun.stdin.text()) as Input;
const original = input.original ?? "";
const fuzzLevel = Number(input.fuzz_level);
const sim = new FuzzSimulator(original);

if (fuzzLevel > 0 && original.length > 0) {
  const n = original.length;
  const k = Math.min(n, Math.round(fuzzLevel * n));
  const rng = mulberry32(hashSeed(`${input.seed}:${input.memory_id}:${fuzzLevel}`));
  const indices = shuffle([...Array(n).keys()], rng).slice(0, k);
  for (const i of indices) {
    sim.applyWaveToPositions([i]);
  }
}

const fuzz = sim.getCurrentFuzz();
let replaced = Math.abs(original.length - fuzz.length);
const n = Math.min(original.length, fuzz.length);
for (let i = 0; i < n; i++) {
  if (original[i] !== fuzz[i]) replaced += 1;
}

process.stdout.write(
  JSON.stringify({
    final_fuzz: fuzz,
    fuzz_simulator_level: sim.getCurrentFuzzLevel(),
    replaced_chars: replaced,
  }) + "\n"
);
