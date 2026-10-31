"""Validate local forms and serialise checked viewer writes."""

import hmac as hmac
import sys
import threading
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from http import HTTPStatus
from urllib.parse import parse_qs, quote

from lodge.app import AddOutcome, CommitOutcome, Lodge, LodgeError, NotFound, StaleList, Written
from lodge.core import Raises, is_id

MAX_BODY = 65_536
NOTICES: Mapping[str, str] = {
    "committed": "Written and committed.",
    "published": "Written and published.",
    "staged": "Written and staged, not committed.",
    "staged-base": "Written and staged, not committed: this checkout is on the base branch.",
    "staged-detached": "Written and staged, not committed: HEAD is detached.",
    "staged-in-progress": (
        "Written and staged, not committed: a merge, rebase, cherry-pick, or revert is in progress."
    ),
    "staged-locked": "Written and staged, not committed: git's index is locked by another process.",
    "staged-failed": (
        "Written and staged, not committed: git could not commit; the "
        "terminal running lodge view says why."
    ),
    "stale": (
        "The list changed since the page was loaded, so nothing was written; check the new list."
    ),
}
_LOCK = threading.Lock()


@dataclass(frozen=True)
class Gatekeeper:
    token: str
    hosts: frozenset[str]

    def __post_init__(self) -> None:
        if len(self.token) < 32:
            raise ValueError("the viewer token needs at least 32 characters")


@dataclass(frozen=True)
class Reply:
    status: HTTPStatus
    text: str
    location: str | None = None
    back: str | None = None


def allowed_hosts(port: int, extra: Sequence[str]) -> frozenset[str]:
    return frozenset(h.lower() for h in (f"127.0.0.1:{port}", f"localhost:{port}", *extra))


def refuse_early(gate: Gatekeeper, headers: Mapping[str, str]) -> Reply | None:
    if headers.get("host", "").lower() not in gate.hosts:
        return Reply(HTTPStatus.FORBIDDEN, "this address is not served")
    origin = headers.get("origin", "").lower()
    if not origin:
        return Reply(HTTPStatus.FORBIDDEN, "a write needs an Origin header")
    if origin not in {f"{scheme}://{host}" for host in gate.hosts for scheme in ("http", "https")}:
        return Reply(HTTPStatus.FORBIDDEN, "this origin is not served")
    return None


def done_code(written: Written) -> str:
    if written.outcome is AddOutcome.PUBLISHED:
        return "published"
    if written.committed is None:
        return "staged"
    outcome = written.committed.outcome
    if outcome is CommitOutcome.FAILED:
        print(written.committed.detail, file=sys.stderr)
    return {
        CommitOutcome.COMMITTED: "committed",
        CommitOutcome.ON_BASE: "staged-base",
        CommitOutcome.DETACHED: "staged-detached",
        CommitOutcome.IN_PROGRESS: "staged-in-progress",
        CommitOutcome.LOCKED: "staged-locked",
        CommitOutcome.FAILED: "staged-failed",
    }[outcome]


def handle_post(
    make_lodge: Callable[[], Lodge],
    gate: Gatekeeper,
    path: str,
    headers: Mapping[str, str],
    body: bytes,
) -> Reply:
    refused = refuse_early(gate, headers)
    if refused is not None:
        return refused
    if (
        headers.get("content-type", "").split(";", 1)[0].strip().lower()
        != "application/x-www-form-urlencoded"
    ):
        return Reply(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "a write needs a form")
    if len(body) > MAX_BODY:
        return Reply(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "the form is too large")
    try:
        fields = parse_qs(
            body.decode("utf-8"), keep_blank_values=True, max_num_fields=200, errors="strict"
        )
    except (ValueError, UnicodeDecodeError):
        return Reply(HTTPStatus.BAD_REQUEST, "the form is not valid UTF-8")
    tokens = fields.get("token", [])
    if len(tokens) != 1 or not hmac.compare_digest(
        tokens[0].encode("utf-8"), gate.token.encode("ascii")
    ):
        return Reply(HTTPStatus.FORBIDDEN, "this form is stale or from elsewhere; reload the page")
    back = "/"
    try:

        def one(name: str) -> str:
            values = fields.get(name, [])
            if len(values) != 1:
                raise LodgeError(f"the form needs one {name} field")
            return values[0]

        lodge = make_lodge()
        with _LOCK:
            if path == "/confirm":
                ids = fields.get("id", [])
                if not ids or any(not is_id(i) or not i.startswith("d-") for i in ids):
                    raise LodgeError("id needs a decision ID")
                area = one("area") if "area" in fields else None
                back = (
                    f"/spec?area={quote(area, safe='')}"
                    if area is not None
                    else f"/r/{quote(ids[0], safe='')}"
                )
                try:
                    written = lodge.confirm(ids, one("words"), area, commit=True)
                except StaleList:
                    return Reply(
                        HTTPStatus.SEE_OTHER,
                        "",
                        back + ("&" if area is not None else "?") + "done=stale",
                    )
                location = back + ("&" if area is not None else "?") + f"done={done_code(written)}"
            else:
                if path == "/threads":
                    about = one("about")
                    back = f"/r/{quote(about, safe='')}"
                    try:
                        kind = Raises(one("kind"))
                    except ValueError:
                        raise LodgeError("kind needs doubt or question") from None
                    written = lodge.ask(
                        about, kind, "author", one("text"), where="lodge viewer", commit=True
                    )
                else:
                    parts = path.split("/")
                    if (
                        len(parts) != 4
                        or parts[1] != "threads"
                        or parts[3] not in {"reply", "close"}
                    ):
                        raise NotFound("there is nothing at this address")
                    ident = parts[2]
                    if not is_id(ident) or not ident.startswith("q-"):
                        raise LodgeError("thread needs a thread ID")
                    about = lodge.thread(ident).thread.about
                    back = f"/r/{quote(about, safe='')}"
                    action = lodge.reply if parts[3] == "reply" else lodge.close
                    written = action(
                        ident, "author", one("text"), where="lodge viewer", commit=True
                    )
                location = (
                    f"/r/{quote(written.about or about, safe='')}"
                    f"?done={done_code(written)}#{quote(written.ids[0], safe='')}"
                )
            if written.outcome is AddOutcome.CHECK_FAILED:
                raise LodgeError("; ".join(p.message for p in written.check.problems))
            return Reply(HTTPStatus.SEE_OTHER, "", location)
    except NotFound as error:
        return Reply(HTTPStatus.NOT_FOUND, str(error), back=back)
    except LodgeError as error:
        return Reply(
            HTTPStatus.BAD_REQUEST,
            str(error),
            back=back,
        )
    except Exception as error:
        print(f"lodge: viewer: {type(error).__name__}: {error}", file=sys.stderr)
        return Reply(HTTPStatus.INTERNAL_SERVER_ERROR, "lodge could not answer")
