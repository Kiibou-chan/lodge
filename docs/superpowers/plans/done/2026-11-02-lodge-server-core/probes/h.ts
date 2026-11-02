import { sha256 } from "@noble/hashes/sha2.js"; import { bytesToHex } from "@noble/hashes/utils.js"; console.log(bytesToHex(sha256(new TextEncoder().encode("a\n"))).slice(0,12))
