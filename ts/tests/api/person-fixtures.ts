export const doc = (h: string, b: string) => `---\n${h}\n---\n\n${b}\n`;
export const draft = (by = "ada") =>
  doc(
    `kind: decision\ntitle: Keep transcripts\nscope: process\ndecided_by: ${by}\nquote:\n  text: Keep them.\n  where: chat\n  when: "2026-10-29 10:00"`,
    "Transcripts are kept.\n\n## Reasoning\n\nThey help.",
  );
