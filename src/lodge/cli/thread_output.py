"""Readable thread heads, messages, and waiting groups."""

from lodge.app import Listed, ThreadShown, ThreadsWaiting
from lodge.cli.output import read_lines
from lodge.core import Thread, ThreadState, format_level1


def thread_head(t: Thread, title: str) -> str:
    return (
        f"{t.id} · {t.state.value} · {t.raises.value} · about {t.about} · "
        f"{len(t.messages)} messages · last by {t.messages[-1].by}\n{title}"
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
    return "\n".join(
        [
            *read_lines(shown.read),
            thread_head(t, shown.about.title) + "\n\n" + "\n\n".join(messages),
        ]
    )


def waiting_text(listed: Listed, waiting: ThreadsWaiting) -> str:
    agents = [thread_head(t, waiting.titles.get(t.about, "")) for t in waiting.for_agent]
    author = [format_level1(item) for item in listed.items]
    author += [thread_head(t, waiting.titles.get(t.about, "")) for t in waiting.for_author]
    reads = list(dict.fromkeys([*read_lines(listed.read), *read_lines(waiting.read)]))
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
