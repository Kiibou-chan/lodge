export interface ExportTarget {
  readonly repository: string;
  readonly branch: string;
  readonly remote: string | null;
}
export type ExportOutcome =
  | { readonly kind: "committed"; readonly commit: string }
  | { readonly kind: "unchanged" }
  | { readonly kind: "moved" };

export function exportTargetProblem(target: ExportTarget): string | null {
  if (
    [target.repository, target.branch, target.remote ?? ""].some((value) => /\p{Cc}/u.test(value))
  )
    return "export-target: repository, branch, and remote must not contain control characters";
  if (!target.repository.startsWith("/"))
    return "export-target: repository must be an absolute path";
  if (
    !/^[A-Za-z0-9]/.test(target.branch) ||
    /[^A-Za-z0-9._/-]/.test(target.branch) ||
    target.branch.includes("..")
  )
    return "export-target: branch must be a name of letters, digits, and . _ / -, not starting with a symbol";
  if (target.remote?.startsWith("-")) return "export-target: remote must not start with -";
  return null;
}

export function lodgePathProblem(path: string): string | null {
  const parts = path.split("/");
  if (
    parts[0] !== "lodge" ||
    parts.length < 2 ||
    path.includes("\\") ||
    path.includes("\0") ||
    parts.some((part) => ["", ".", "..", ".git"].includes(part))
  )
    return `${path} is outside lodge/, which is all the store writes`;
  return null;
}
