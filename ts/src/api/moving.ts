import {
  coreSettings,
  type ExportTarget,
  exportFailedLine,
  exportTargetProblem,
  importStore,
  LodgeError,
  person,
} from "#app";
import { Args, isObject } from "./args.ts";
import { ApiError } from "./errors.ts";
import type { ApiOptions, Moving } from "./options.ts";

function movingOf(options: ApiOptions): Moving {
  if (!options.moving) throw new LodgeError("this server was started without import and export");
  return options.moving;
}
async function projectSettings(options: ApiOptions, project: string) {
  const settings = await options.projects.settings(project);
  if (settings === null) throw new ApiError("no-project", `no project named ${project}`);
  return settings;
}
export async function importOperation(
  options: ApiOptions,
  signedIn: string,
  body: Readonly<Record<string, unknown>>,
): Promise<{ readonly checkFailed: boolean; readonly result: unknown }> {
  const moving = movingOf(options);
  const args = new Args("import", body);
  const project = args.string("project");
  const settings = await projectSettings(options, project);
  const repository = args.string("repository");
  if (!repository.startsWith("/"))
    throw new ApiError("usage", "import: repository must be an absolute path");
  const rev = args.string("rev");
  const copy = await moving.read(repository, rev, args.string("settingsRev", rev));
  const result = await importStore(
    copy,
    project,
    signedIn,
    options.projects,
    coreSettings(settings),
    options.clock,
  );
  return { result, checkFailed: result.kind === "check-failed" };
}
export async function exportTargetOperation(
  options: ApiOptions,
  signedIn: string,
  body: Readonly<Record<string, unknown>>,
): Promise<{
  readonly checkFailed: false;
  readonly result: { readonly target: ExportTarget | null };
}> {
  const moving = movingOf(options);
  const args = new Args("export-target", body);
  const project = args.string("project");
  await projectSettings(options, project);
  const value = body["target"];
  let target: ExportTarget | null = null;
  if (value !== null) {
    if (!isObject(value)) return args.fail("target", "an object or null");
    const fields = new Args(
      "export-target",
      Object.fromEntries(Object.entries(value).map(([key, v]) => [`target.${key}`, v])),
    );
    fields.known(["target.repository", "target.branch", "target.remote"]);
    target = {
      repository: fields.string("target.repository"),
      branch: fields.string("target.branch"),
      remote: fields.nullable("target.remote"),
    };
    const problem = exportTargetProblem(target);
    if (problem !== null) throw new ApiError("usage", problem);
  }
  await moving.targets.setTarget(project, target, person(signedIn));
  if (target !== null)
    void moving.exporters
      .written(project)
      .catch((error: unknown) => options.log(exportFailedLine(project, error)));
  return { checkFailed: false, result: { target } };
}
