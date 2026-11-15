const byId = (id) => document.getElementById(id);
const json = (body = {}) => ({
  method: "POST",
  credentials: "same-origin",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});
const api = {
  me: () => fetch("/api/v1/me", json()),
  registerOptions: (body) => fetch("/api/v1/register-options", json(body)),
  register: (body) => fetch("/api/v1/register", json(body)),
  signInOptions: () => fetch("/api/v1/sign-in-options", json()),
  signIn: (body) => fetch("/api/v1/sign-in", json(body)),
  signOut: () => fetch("/api/v1/sign-out", json()),
  tokens: () => fetch("/api/v1/tokens", json()),
  issue: (body) => fetch("/api/v1/token-issue", json(body)),
  revoke: (body) => fetch("/api/v1/token-revoke", json(body)),
  projects: () => fetch("/api/v1/projects", json()),
  held: (body) => fetch("/api/v1/held", json(body)),
  approve: (body) => fetch("/api/v1/approve", json(body)),
  decline: (body) => fetch("/api/v1/decline", json(body)),
};
async function result(pending) {
  const response = await pending;
  const body = await response.json();
  if (!response.ok || body.error) throw new Error(body.error?.message ?? "The request failed.");
  return body.result;
}
function element(tag, text, parent) {
  const node = document.createElement(tag);
  node.textContent = text ?? "";
  parent.append(node);
  return node;
}
function action(task) {
  return async (event) => {
    event.preventDefault();
    byId("status").textContent = "";
    const control = event.currentTarget;
    control.disabled = true;
    try {
      await task();
    } catch (error) {
      byId("status").textContent = error.message;
    } finally {
      control.disabled = false;
    }
  };
}
function button(parent, label, task) {
  const node = element("button", label, parent);
  node.type = "button";
  node.addEventListener("click", action(task));
}
function decode(text) {
  const base64 = text.replace(/-/gu, "+").replace(/_/gu, "/");
  return Uint8Array.from(atob(base64), (letter) => letter.charCodeAt(0));
}
function encode(buffer) {
  return btoa(String.fromCharCode(...new Uint8Array(buffer)))
    .replace(/\+/gu, "-")
    .replace(/\//gu, "_")
    .replace(/=+$/u, "");
}
function credentialJSON(credential) {
  const response = credential.response;
  const fields = {};
  for (const name of [
    "clientDataJSON",
    "attestationObject",
    "authenticatorData",
    "signature",
    "userHandle",
  ]) {
    if (name in response) fields[name] = response[name] === null ? null : encode(response[name]);
  }
  if (response.getTransports) fields.transports = response.getTransports();
  return {
    id: credential.id,
    rawId: encode(credential.rawId),
    type: credential.type,
    response: fields,
    clientExtensionResults: credential.getClientExtensionResults(),
    authenticatorAttachment: credential.authenticatorAttachment,
  };
}
async function register(setupCode) {
  const options = await result(api.registerOptions({ setupCode }));
  options.challenge = decode(options.challenge);
  options.user.id = decode(options.user.id);
  options.excludeCredentials = (options.excludeCredentials ?? []).map((entry) => ({
    ...entry,
    id: decode(entry.id),
  }));
  const credential = await navigator.credentials.create({ publicKey: options });
  if (!credential) throw new Error("No passkey was created.");
  await result(api.register({ setupCode, response: credentialJSON(credential) }));
  byId("setup-code").value = "";
  await refresh();
}
async function signIn() {
  const options = await result(api.signInOptions());
  options.challenge = decode(options.challenge);
  options.allowCredentials = (options.allowCredentials ?? []).map((entry) => ({
    ...entry,
    id: decode(entry.id),
  }));
  const credential = await navigator.credentials.get({ publicKey: options });
  if (!credential) throw new Error("No passkey was supplied.");
  await result(api.signIn({ response: credentialJSON(credential) }));
  await refresh();
}
function detail(parent, label, value) {
  if (value !== null && value !== undefined) element("p", `${label}: ${value}`, parent);
}
function draft(parent, item) {
  element("h4", item.title ?? item.name, parent);
  if (item.problem) {
    detail(parent, "Problem", item.problem);
    element("pre", item.text, parent);
    return;
  }
  detail(parent, "Kind", item.kind);
  detail(parent, "Statement", item.statement);
  detail(parent, "Introduction", item.intro);
  if (item.quote) {
    detail(parent, "Quote", item.quote.text);
    detail(parent, "Where", item.quote.where);
    detail(parent, "When", item.quote.when);
  }
}
function hold(parent, project, item) {
  const entry = element("article", "", parent);
  element("h3", `${item.kind} ${item.seq}`, entry);
  detail(entry, "By", item.by);
  detail(entry, "At", item.at);
  if (item.kind === "add") {
    for (const itemDraft of item.drafts) draft(entry, itemDraft);
  } else if (item.kind === "message") {
    for (const key of ["operation", "ref", "raises", "text", "where", "when"]) {
      detail(entry, key, item[key]);
    }
  }
  const controls = element("div", "", entry);
  button(controls, "Approve", async () => {
    const approved = await result(api.approve({ project, seq: item.seq }));
    const outcome = approved.kind === "add" ? approved.added : approved.written;
    element("p", `Published: ${outcome.ids.join(", ")}`, entry);
    controls.remove();
  });
  const form = element("form", "", controls);
  const label = element("label", "Reason for declining ", form);
  const reason = element("input", "", label);
  reason.required = true;
  const decline = element("button", "Decline", form);
  decline.type = "submit";
  form.addEventListener(
    "submit",
    action(async () => {
      await result(api.decline({ project, seq: item.seq, reason: reason.value }));
      element("p", "Declined", entry);
      controls.remove();
    }),
  );
}
async function tokens() {
  const list = byId("tokens");
  list.replaceChildren();
  for (const token of await result(api.tokens())) {
    const item = element("li", `${token.project}: ${token.label} (${token.id})`, list);
    if (token.revoked) {
      detail(item, "Revoked", token.revoked);
    } else {
      button(item, "Revoke", async () => {
        await result(api.revoke({ id: token.id }));
        await tokens();
      });
    }
  }
}
async function refresh() {
  byId("secret").textContent = "";
  const me = await result(api.me());
  byId("signing-in").hidden = me.signedIn;
  byId("signed-in").hidden = !me.signedIn;
  byId("tokens").replaceChildren();
  byId("held").replaceChildren();
  if (!me.signedIn) return;
  byId("person").textContent = `Signed in as ${me.person}`;
  await tokens();
  for (const project of await result(api.projects())) {
    const section = element("section", "", byId("held"));
    element("h3", project, section);
    const held = await result(api.held({ project }));
    if (!held.length) element("p", "Nothing held for approval.", section);
    for (const item of held) hold(section, project, item);
  }
}
byId("register").addEventListener(
  "submit",
  action(() => register(byId("setup-code").value)),
);
byId("sign-in").addEventListener("click", action(signIn));
byId("add-passkey").addEventListener(
  "click",
  action(() => register(null)),
);
byId("sign-out").addEventListener(
  "click",
  action(async () => {
    await result(api.signOut());
    await refresh();
  }),
);
byId("issue-token").addEventListener(
  "submit",
  action(async () => {
    byId("secret").textContent = "";
    const issued = await result(
      api.issue({
        project: byId("project").value,
        label: byId("label").value,
        role: null,
      }),
    );
    byId("secret").textContent = issued.secret;
    await tokens();
  }),
);
refresh().catch((error) => {
  byId("status").textContent = error.message;
});
