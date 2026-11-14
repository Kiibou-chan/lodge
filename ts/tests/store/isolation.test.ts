import { expect, test } from "bun:test";
import { person, Role } from "#app";
import { decision, filesOf } from "../core/builders.ts";
import { setup } from "./support.ts";

test("trees_members_and_attachments_are_confined_to_the_project", async () => {
  const { store, projects } = await setup();
  await projects.create("other", "ada");
  const other = projects.storeFor("other", person("ada"));
  const attachment = "lodge/attachments/d-aaaaaa/run.log";
  await other.publish(
    (await other.trees())[0],
    new Map([
      ...filesOf(decision({ id: "d-aaaaaa" })),
      ["lodge/other", "other file"],
      [attachment, "other attachment"],
    ]),
    "other",
  );
  await store.publish(
    (await store.trees())[0],
    new Map([
      ["lodge/a", "own file"],
      ["lodge/decisions/d-bbbbbb.md", "own decision"],
      ["lodge/attachments0", "upper boundary"],
    ]),
    "own",
  );
  for (const current of await store.trees()) {
    expect(current.files).toEqual(
      new Map([
        ["lodge/a", "own file"],
        ["lodge/decisions/d-bbbbbb.md", "own decision"],
        ["lodge/attachments0", "upper boundary"],
      ]),
    );
    expect(current.people).toEqual(new Set(["author"]));
    expect(current.attachments).toEqual(new Set());
  }
  expect(await projects.members("storage")).toEqual(new Map([["author", Role.OWNER]]));
  expect(await store.attachmentTexts()).toEqual(new Map());
});
