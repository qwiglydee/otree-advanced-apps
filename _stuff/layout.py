"""Some utils to manage button/choices layouts
by qwiglydee@gmail.com
"""

from textwrap import wrap


def layoutdict(layout: str, lng=1) -> dict:
    """Convert layout from string to dict indexed by on-screen position
    "ABC" -> { '1': "A", '2': "B", '3': "C" }
    Note: the keys are stringular digits 

    layoutdict("A1A2B1B2",2) => { '1': "A1", '2': "A2", ... }
    """
    return {str(i + 1): l for i, l in enumerate(wrap(layout, lng))}


def arrange(layout: str | dict, fields: dict[str, any]):
    """Arrange some fields by screen positions accoring to screen layout
    { "A": ..., "B": ...} -> { '1': ..., '2': ...}
    """
    if isinstance(layout, str):
        layout = layoutdict(layout)
    return {i: fields[a] for i, a in layout.items()}


def derange(layout: str | dict, fields: dict[int, any]):
    """Inverse of arrange: unmap buttons' screen positions to choice labels
    { '1': ..., '2': ...} -> { "A": ..., "B": ...}
    """
    if isinstance(layout, str):
        layout = layoutdict(layout)
    return {a: fields[i] for i, a in layout.items()}
