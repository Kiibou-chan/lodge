"""The viewer's forms and append-only conversations."""

from lodge.core import Thread, ThreadState, newest_last
from lodge.viewer.html import e, paragraphs

_NOTE = (
    "The decision stays the agent's, and your words are kept exactly as written, "
    'so a caveat such as "read, not fully understood" belongs here.'
)


def hidden(name: str, value: str) -> str:
    return f'<input type="hidden" name="{e(name)}" value="{e(value)}">'


def _form(action: str, token: str, fields: str, button: str) -> str:
    return (
        f'<form method="post" action="{e(action)}">{hidden("token", token)}'
        f"{fields}<button>{e(button)}</button></form>"
    )


def confirm_form(ids: tuple[str, ...], token: str, area: str | None = None) -> str:
    fields = "".join(hidden("id", ident) for ident in ids)
    if area is not None:
        fields += hidden("area", area)
    fields += '<label>Your words<textarea name="words" required></textarea></label>'
    fields += f'<p class="notice">{e(_NOTE)}</p>'
    return _form("/confirm", token, fields, "Confirm")


def _text(label: str, required: bool = True) -> str:
    need = " required" if required else ""
    return f'<label>{e(label)}<textarea name="text"{need}></textarea></label>'


def record_forms(about: str, token: str) -> str:
    return "".join(
        _form(
            "/threads",
            token,
            hidden("about", about) + hidden("kind", kind) + _text(label),
            label,
        )
        for kind, label in (("doubt", "Raise a doubt"), ("question", "Ask a question"))
    )


def threads_body(threads: tuple[Thread, ...], token: str) -> str:
    result = ""
    for thread in newest_last(threads):
        head = "Doubt" if thread.raises == "doubt" else "Question"
        result += (
            f'<section class="thread" id="{e(thread.id)}">'
            f"<h2>{head} {e(thread.id)}</h2><p>{e(thread.state.value)}</p>"
        )
        for n, message in enumerate(thread.messages):
            closing = thread.state is ThreadState.CLOSED and n == len(thread.messages) - 1
            by = f"Closed by {message.by}" if closing else message.by
            result += f'<h3>{e(by)}</h3><div class="meta">{e(message.when)}'
            if message.where is not None:
                result += f" &middot; {e(message.where)}"
            result += f"</div>{paragraphs(message.text)}"
        if thread.state is ThreadState.OPEN:
            base = f"/threads/{thread.id}"
            result += _form(base + "/reply", token, _text("Reply"), "Reply")
            result += _form(
                base + "/close", token, _text("Closing words (optional)", False), "Close"
            )
        result += "</section>"
    return result
