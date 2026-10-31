"""Readable thread heads, messages, and waiting groups."""

from lodge.app import Listed, ThreadShown, ThreadsWaiting
from lodge.cli.output import read_lines
from lodge.core import Thread, ThreadState, format_level1


def thread_head(t: Thread, title: str | None) -> str:
    n = len(t.messages)
    subject = f"about {t.about}"
    return (
        f"{t.id} · {t.state.value} · {t.raises.value} · {subject} · "
        f"{n} message{'s' if n != 1 else ''} · last by {t.messages[-1].by}"
        + f"\n{title if title is not None else f'about {t.about}, not found'}"
    )


def thread_text(shown: ThreadShown) -> str:
    t = shown.thread
    messages = []
    for index, message in enumerate(t.messages):
        prefix = (
            "closed by " if t.state is ThreadState.CLOSED and index == len(t.messages) - 1 else ""
        )
        head = f"{prefix}{message.by} · {message.when}"
        if message.where is not None:
            head += f" · {message.where}"
        messages.append(head + (f"\n{message.text}" if message.text else ""))
    head = thread_head(t, shown.about.title if shown.about is not None else None)
    body = "\n\n".join(messages)
    return "\n".join([*read_lines(shown.read), f"{head}\n\n{body}"])


def waiting_text(listed: Listed, waiting: ThreadsWaiting) -> str:
    agents = [thread_head(t, waiting.titles.get(t.about)) for t in waiting.for_agent]
    author = [format_level1(item) for item in listed.items]
    author += [thread_head(t, waiting.titles.get(t.about)) for t in waiting.for_author]
    reads = read_lines(listed.read)
    return "\n".join(
        [
            *reads,
            "waiting for an agent",
            "\n\n".join(agents) or "nothing",
            "",
            "waiting for the author",
            "\n\n".join(author) or "nothing",
        ]
    )
