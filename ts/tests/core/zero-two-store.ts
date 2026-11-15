// The made-up lodge 0.2 store of docs/superpowers/plans/2026-11-02-lodge-server-import/probes/zero-two-store/, written by lodge 0.2 (probe 6).
export const ZERO_TWO_STORE: ReadonlyMap<string, string> = new Map([
  [".lodge.toml", '[import]\nsources = ["docs/choices.md"]\n'],
  ["lodge/attachments/d-q59cdf/sizes.csv", "size,count\nsmall,3\n"],
  ["lodge/decisions/.gitkeep", ""],
  [
    "lodge/decisions/d-40q44p-keep-old-transcripts.md",
    '---\nid: d-40q44p\nkind: decision\ntitle: "Keep old transcripts"\nscope: product\ndecided_by: author\ndate: 2026-01-05T00:00:00+00:00\nimported_from: {file: "docs/choices.md", heading: "ITEM-9"}\n---\n\nOld transcripts are kept.\n',
  ],
  [
    "lodge/decisions/d-q59cdf-keep-logs.md",
    '---\nid: d-q59cdf\nkind: decision\ntitle: "Keep logs"\nscope: product\ndecided_by: coordinator\ndate: 2026-11-02T18:56:29+01:00\nattachments: ["sizes.csv"]\n---\n\nLogs are kept.\n',
  ],
  [
    "lodge/decisions/d-qqrf9k-keep-transcripts.md",
    '---\nid: d-qqrf9k\nkind: decision\ncode: ITEM-1\ntitle: "Keep transcripts"\nscope: product\ndecided_by: author\ndate: 2026-11-02T18:56:28+01:00\nchanges:\n  - {entry: s-cjhfb7, action: create}\nquote: {text: "Keep them.", where: "chat", when: "2026-10-29 10:00"}\n---\n\nTranscripts are kept.\n\n## Reasoning\n\nKeep them.\n',
  ],
  [
    "lodge/decisions/d-t46j05-confirm-logs.md",
    '---\nid: d-t46j05\nkind: decision\ntitle: "Confirm logs"\nscope: product\ndecided_by: author\ndate: 2026-11-02T18:56:30+01:00\nconfirms: [d-q59cdf]\nquote: {text: "Yes.", where: "chat", when: "2026-10-29 11:00"}\n---\n\nThe author confirms d-q59cdf.\n',
  ],
  ["lodge/spec/.gitkeep", ""],
  [
    "lodge/spec/storage/_area.md",
    '---\nkind: area\ntitle: "Storage"\norder: [s-cjhfb7]\n---\n\nHow data is kept.\n',
  ],
  [
    "lodge/spec/storage/s-cjhfb7-transcripts-are-kept.md",
    '---\nid: s-cjhfb7\nkind: spec\ntitle: "Transcripts are kept"\n---\n\nTranscripts are kept whole.\n',
  ],
  [
    "lodge/threads/q-j2dsgk.md",
    '---\nid: q-j2dsgk\nkind: thread\nabout: s-cjhfb7\nraises: question\nstate: open\nopened: 2026-11-02T18:56:30+01:00\n---\n\n## Message 1\n\nby: coordinator\nwhen: 2026-11-02T18:56:30+01:00\n\nAre transcripts kept whole, or trimmed?\n\n## Message 2\n\nby: author\nwhen: "2026-10-29 12:00"\nwhere: "chat"\n\nWhole.\n',
  ],
]);
