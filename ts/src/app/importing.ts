import {
  ATTACHMENTS,
  type CoreSettings,
  checkChange,
  load,
  type Problem,
  problem,
  tree,
  ValueError,
  writeRecord,
  writeThread,
} from "#core";
import { Conflict, coreSettings, Forbidden, LodgeError } from "./errors.ts";
import { type Clock, type Projects, PublishOutcome, person, Role } from "./ports.ts";
import { stampOf } from "./time.ts";

export interface ZeroTwoCopy {
  readonly rev: string;
  readonly files: ReadonlyMap<string, string>;
  readonly settings: Readonly<Record<string, unknown>>;
}
interface PreparedImport {
  readonly problems: readonly Problem[];
  readonly stage: "lodge 0.2" | "server" | null;
  readonly files: ReadonlyMap<string, string>;
  readonly mapped: readonly string[];
}
type Imported =
  | {
      readonly kind: "imported";
      readonly rev: string;
      readonly decisions: number;
      readonly entries: number;
      readonly areas: number;
      readonly threads: number;
      readonly attachments: number;
      readonly mapped: readonly string[];
    }
  | {
      readonly kind: "check-failed";
      readonly stage: "lodge 0.2" | "server";
      readonly problems: readonly Problem[];
    };
const WRITER_REFUSAL =
  "lodge 0.2 did not write this file as lodge writes it, so the importer cannot change who wrote it alone";

function snapshot(files: ReadonlyMap<string, string>, people?: ReadonlySet<string>) {
  const records = new Map<string, string>();
  const attachments = new Set<string>();
  for (const [path, text] of files) {
    if (path.startsWith(ATTACHMENTS)) attachments.add(path);
    else records.set(path, text);
  }
  return load(tree({ rev: null, files: records, attachments, ...(people ? { people } : {}) }));
}
function failed(stage: "lodge 0.2" | "server", problems: readonly Problem[]): PreparedImport {
  return { stage, problems, files: new Map(), mapped: [] };
}
export function prepareImport(
  copy: ZeroTwoCopy,
  owner: string,
  people: ReadonlySet<string>,
  settings: CoreSettings,
  now: string,
): PreparedImport {
  const empty = snapshot(new Map());
  const original = snapshot(copy.files);
  const sourceProblems = checkChange(empty, original, coreSettings(copy.settings), now).problems;
  if (sourceProblems.length) return failed("lodge 0.2", sourceProblems);
  const files = new Map([...copy.files].filter(([path]) => !path.endsWith("/.gitkeep")));
  const mapped: string[] = [];
  const writerProblems: Problem[] = [];
  for (const record of [...original.decisions.values(), ...original.threads.values()]) {
    const changes =
      record.kind === "decision"
        ? record.decidedBy === "author"
        : record.messages.some((message) => message.by === "author");
    if (!changes) continue;
    const path = original.paths.get(record.id) as string;
    try {
      const unchanged =
        record.kind === "decision" ? writeRecord(record) : writeThread(record, original.people);
      if (unchanged !== copy.files.get(path)) {
        writerProblems.push(problem({ path, check: 1, message: WRITER_REFUSAL }));
        continue;
      }
      const text =
        record.kind === "decision"
          ? writeRecord({ ...record, decidedBy: owner })
          : writeThread(
              {
                ...record,
                messages: record.messages.map((message) => ({
                  ...message,
                  by: message.by === "author" ? owner : message.by,
                })),
              },
              people,
            );
      files.set(path, text);
      mapped.push(record.id);
    } catch (error) {
      if (!(error instanceof ValueError)) throw error;
      writerProblems.push(problem({ path, check: 1, message: WRITER_REFUSAL }));
    }
  }
  if (writerProblems.length) return failed("lodge 0.2", writerProblems);
  const pathProblems = [...files.keys()]
    .filter((path) => /[\uDC80-\uDCFF]/u.test(path))
    .map((path) =>
      problem({
        path,
        check: 1,
        message:
          "this file's name is not UTF-8, which the server cannot store; rename it in the lodge 0.2 store and import again",
      }),
    );
  const serverProblems = [
    ...pathProblems,
    ...checkChange(empty, snapshot(files, people), settings, now).problems,
  ];
  if (serverProblems.length) return failed("server", serverProblems);
  return { problems: [], stage: null, files, mapped };
}

export async function importStore(
  copy: ZeroTwoCopy,
  project: string,
  requester: string,
  projects: Pick<Projects, "members" | "storeFor">,
  settings: CoreSettings,
  clock: Clock,
): Promise<Imported> {
  const owners = [...(await projects.members(project))]
    .filter(([, role]) => role === Role.OWNER)
    .map(([name]) => name);
  const owner = owners[0];
  if (owners.length !== 1 || owner === undefined)
    throw new LodgeError(
      `project ${project} has ${owners.length} owners; lodge imports into a project with one owner`,
    );
  if (requester !== owner)
    throw new Forbidden(`only ${owner}, the owner of project ${project}, may import into it`);
  const store = projects.storeFor(project, person(owner));
  const [current] = await store.trees();
  if (current.files.size || current.attachments.size)
    throw new Conflict(
      `project ${project} already holds records; lodge imports a store into an empty project only`,
    );
  const prepared = prepareImport(copy, owner, current.people, settings, stampOf(clock.now()));
  if (prepared.stage !== null)
    return { kind: "check-failed", stage: prepared.stage, problems: prepared.problems };
  const outcome = await store.publish(
    current,
    prepared.files,
    `Import the lodge 0.2 store at ${copy.rev}`,
  );
  if (outcome === PublishOutcome.REJECTED)
    throw new Conflict(`project ${project} changed during the import; nothing was imported`);
  const paths = [...prepared.files.keys()];
  return {
    kind: "imported",
    rev: copy.rev,
    decisions: paths.filter((path) => path.startsWith("lodge/decisions/")).length,
    entries: paths.filter((path) => path.startsWith("lodge/spec/") && !path.endsWith("/_area.md"))
      .length,
    areas: paths.filter((path) => path.endsWith("/_area.md")).length,
    threads: paths.filter((path) => path.startsWith("lodge/threads/")).length,
    attachments: paths.filter((path) => path.startsWith(ATTACHMENTS)).length,
    mapped: prepared.mapped,
  };
}
