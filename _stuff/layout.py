"""Some utils to manage button/choices layouts
by qwiglydee@gmail.com
"""

from textwrap import wrap

def layoutdict(layout: str, l=1) -> dict:
    """Convert layout from string to dict indexed by on-screen position
    "ABC" -> { 1: "A", 2: "B", 3: "C" }

    layoutdict("A1A2B1B2",2) => { 1: "A1", 2: "A2", ... }
    """
    return {i + 1: l for i, l in enumerate(wrap(layout, l))}


def arrange(layout: str | dict, fields: dict[str, any]):
    """Arrange some fields by screen positions accoring to screen layout
    fields: { "A": ..., "B": ...}
    returns: { 1: ..., 2: ...}
    """
    if isinstance(layout, str):
        layout = layoutdict(layout)
    return {i: fields[a] for i, a in layout.items()}


def derange(layout: str | dict, fields: dict[int, any]):
    """Inverse of arrange
    fields: { 1: ..., 2: ...}
    returns: { "A": ..., "B": ...}
    """
    if isinstance(layout, str):
        layout = layoutdict(layout)
    return {a: fields[i] for i, a in layout.items()}
