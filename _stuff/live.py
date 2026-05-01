"""
Utils to simplify live communicating.
by qwiglydee@gmail.com

Best used with _static/otree-front-live.js

Usage:
    @live_page
    class SomePage(Page):

        @staticmethod
        def live_foo1(player: Player, payload):
            # handle live message of type 'foo1' from browser

            yield 'bar' # send message of type 'bar' back to the player
            yield 'baz', data # send message of type 'baz' with some payload to the player

        @staticmethod
        def live_foo2(player: Player, payload):
            # handle live message of type 'foo2' from browser

            yield player.group, 'qux', data # send a message to all players in the group
            yield another_player, 'qux', data # send a message to another player
"""

import inspect
from typing import Any

from otree.models import BasePlayer, BaseGroup

LiveMessage = dict[str, Any]
LiveResponse = (
    str |
    tuple[str, LiveMessage] |
    tuple[BasePlayer, str] |
    tuple[BasePlayer, str, LiveMessage] |
    tuple[BaseGroup, str] |
    tuple[BaseGroup, str, LiveMessage]
)


def parse_response(player: BasePlayer, response: LiveResponse) -> dict:
    match response:
        case (BaseGroup(), str() as t):
            return {0: {'type': t}}
        case (BaseGroup(), str() as t, dict() as d):
            return {0: {'type': t, **d}}
        case (BasePlayer() as p, str() as t):
            return {p.id_in_group: {'type': t}}
        case (BasePlayer() as p, str() as t, dict() as d):
            return {p.id_in_group: {'type': t, **d}}
        case str() as t:
            return {player.id_in_group: {'type': t}}
        case (str() as t, dict() as d):
            return {player.id_in_group: {'type': t, **d}}
        case _:
            raise ValueError("Some `live_` handler yielded invalid construction")


def live_page(cls):
    """Wraps a live page

    Expects the page to already have `live_` methods (or inherit it from classes).

    The methods should be either generators (with `yield`) or async generators (with `async def`)
    """
    # grab all live_ methods including inherited
    methods = inspect.getmembers(cls, predicate=lambda m: inspect.ismethod(m) and m.__name__.startswith('live_'))

    assert all(inspect.isgeneratorfunction(m) or inspect.isasyncgenfunction(m) for (n, m) in methods), "Some `live_` method invalid"

    handlers = {name[5:]: method for name, method in methods}

    async def generic_live_method(player: BasePlayer, payload: LiveMessage):
        assert isinstance(payload, dict) and isinstance(payload.get('type'), str), "Invalid incoming live message: missing `type`"
        assert payload['type'] in handlers, f"Invalid incoming live message: missing `{cls.__name__}.live_{payload['type']}`"
        handler = handlers[payload['type']]

        if inspect.isasyncgenfunction(handler):
            async for responding in handler(player, payload):
                yield parse_response(player, responding)
        else:
            for responding in handler(player, payload):
                yield parse_response(player, responding)

    cls.live_method = staticmethod(generic_live_method)

    return cls
