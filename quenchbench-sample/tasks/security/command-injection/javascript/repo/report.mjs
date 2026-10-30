import { countLines, countMatches } from './tools/textstats.mjs';

// { path: [lines, lines containing word] }
export function summarize(paths, word = 'TODO') {
  return Object.fromEntries(paths.map((p) => [p, [countLines(p), countMatches(word, p)]]));
}
