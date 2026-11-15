import { isoBase64URL, isoCBOR } from "@simplewebauthn/server/helpers";

const enc = new TextEncoder();
const bytes = (...values: number[]) => {
  const b = new Uint8Array(new ArrayBuffer(values.length));
  b.set(values);
  return b;
};
const sha256 = async (b: Uint8Array<ArrayBuffer>) =>
  new Uint8Array(await crypto.subtle.digest("SHA-256", b));
function cat(...parts: Uint8Array[]) {
  const b = new Uint8Array(new ArrayBuffer(parts.reduce((n, p) => n + p.length, 0)));
  let i = 0;
  for (const p of parts) {
    b.set(p, i);
    i += p.length;
  }
  return b;
}
function der(raw: Uint8Array) {
  const int = (b: Uint8Array) => {
    let i = 0;
    while (i < b.length - 1 && b[i] === 0) i++;
    let v = b.slice(i);
    if ((v[0] ?? 0) & 128) v = cat(bytes(0), v);
    return cat(bytes(2, v.length), v);
  };
  const body = cat(int(raw.slice(0, 32)), int(raw.slice(32)));
  return cat(bytes(48, body.length), body);
}
export class SoftAuthenticator {
  credId = crypto.getRandomValues(new Uint8Array(new ArrayBuffer(16)));
  keys: CryptoKeyPair | null = null;
  count = 0;
  uv = true;
  origin = "https://lodge.test";
  async create(challenge: string) {
    this.keys = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, [
      "sign",
      "verify",
    ]);
    const jwk = await crypto.subtle.exportKey("jwk", this.keys.publicKey);
    const cose = isoCBOR.encode(
      new Map<number, number | Uint8Array>([
        [1, 2],
        [3, -7],
        [-1, 1],
        [-2, isoBase64URL.toBuffer(jwk.x ?? "")],
        [-3, isoBase64URL.toBuffer(jwk.y ?? "")],
      ]),
    );
    const authData = cat(
      await sha256(enc.encode("lodge.test")),
      bytes(this.uv ? 69 : 65),
      new Uint8Array(new ArrayBuffer(4)),
      new Uint8Array(new ArrayBuffer(16)),
      bytes(0, 16),
      this.credId,
      cose,
    );
    const clientDataJSON = enc.encode(
      JSON.stringify({ type: "webauthn.create", challenge, origin: this.origin }),
    );
    const attestationObject = isoCBOR.encode(
      new Map<string, unknown>([
        ["fmt", "none"],
        ["attStmt", new Map()],
        ["authData", authData],
      ]) as never,
    );
    const id = isoBase64URL.fromBuffer(this.credId);
    return {
      id,
      rawId: id,
      type: "public-key" as const,
      clientExtensionResults: {},
      response: {
        clientDataJSON: isoBase64URL.fromBuffer(clientDataJSON),
        attestationObject: isoBase64URL.fromBuffer(attestationObject),
        transports: ["internal" as const],
      },
    };
  }
  async get(challenge: string) {
    if (!this.keys) throw new Error("register first");
    const counter = new Uint8Array(new ArrayBuffer(4));
    new DataView(counter.buffer).setUint32(0, ++this.count);
    const authData = cat(await sha256(enc.encode("lodge.test")), bytes(this.uv ? 5 : 1), counter);
    const clientDataJSON = enc.encode(
      JSON.stringify({ type: "webauthn.get", challenge, origin: this.origin }),
    );
    const sig = new Uint8Array(
      await crypto.subtle.sign(
        { name: "ECDSA", hash: "SHA-256" },
        this.keys.privateKey,
        cat(authData, await sha256(clientDataJSON)),
      ),
    );
    const id = isoBase64URL.fromBuffer(this.credId);
    return {
      id,
      rawId: id,
      type: "public-key" as const,
      clientExtensionResults: {},
      response: {
        clientDataJSON: isoBase64URL.fromBuffer(clientDataJSON),
        authenticatorData: isoBase64URL.fromBuffer(authData),
        signature: isoBase64URL.fromBuffer(der(sig)),
      },
    };
  }
}
