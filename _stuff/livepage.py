"""
Utils to simplify live communicating.
by qwiglydee@gmail.com

Best used with _static/otree-front-live.js

The utils imply all the live messages be dicts(python) / objects(javascript)
with field `type`

Messages are routed and handled according to their type.
"""

import inspect
from typing import Any, AsyncIterator, Iterator

from otree.api import BaseGroup, BasePlayer, Page

LivePayload = dict[str, Any]
"""Format of messages sent between server and browser"""

LiveResponse = str | tuple[str, LivePayload] | tuple[BasePlayer | BaseGroup, str] | tuple[BasePlayer | BaseGroup, str, LivePayload]
"""Format of yields from a page live handler"""

LiveResponding = Iterator[LiveResponse] | AsyncIterator[LiveResponse]
"""Type of page live handler: It should yield one or more live responses"""

# internal data for otree core
otLiveData = dict[int, LivePayload]


class LivePage(Page):
    """Page with live methods

    The page routes all received messages to corresponding page methods according to their type.
    Received data from payload is converted to arguments of the methods.
    Yielded data is send back to browser.

    The payloads are validated and error with explanation is raised
    when fields in the data does not match arguments or types.

    The live methods could be @classmethods (with `page` arg) or @staticmethods as usual
    The page class supports inheritance, mixins and method composition.

    Usage:
        class SomePage(LivePage):
            @classmethod
            def live_foo(page, player: Playe, **kwargs):
                # recieving message of type 'foo'
                # payload is provided in kwargs

                # send a message of type 'bar' back to the player
                yield 'bar'  # just a signal
                yield 'bar', {...}  # with soma data

                # send a message to all players in the group
                yield group, 'baz'
                yield group, 'baz', {...}

                # send a message to a particular player
                yield another_player, 'baz
                yield another_player, 'baz', {...}


            def live_foo1(page, player: Player, *, foo1, foo2 = None):
                # received payload is validated:
                # field foo1 is required
                # field foo2 is optional
                yield something

            def live_foo2(page, player: Player, *, foo1: int, foo2: str = None):
                # received payload is validated by type:
                # field foo1 should be integer
                # field foo2 should be string
                yield something

            @classmethod
            async def live_bar(page, player: Player, **kwargs):
                # works the same
                # can perform async calls to some remote API
                ai_response = await call_chatbot(...)
                yields "answer", {...}

    """

    @classmethod
    async def live_method(page, player: BasePlayer, payload) -> AsyncIterator[otLiveData]:
        pagename = page.__name__

        assert isinstance(payload, dict) and "type" in payload, f"Invalid live payload from {pagename} html: expected object with `type`"

        type = payload.pop("type")
        method = f"live_{type}"

        # handler = inspect.getattr_static(page, method, None) # doesn't work with classmethods/staticmethods
        handler = getattr(page, method, None)

        if handler is None:
            raise TypeError(f"Missing {pagename}.{method}()")
        elif inspect.isgeneratorfunction(handler):
            try:
                validate_payload(handler.__annotations__, payload)
                handling = handler(player, **payload)
            except (TypeError, AssertionError) as e:
                raise ValueError(f"Invalid payload for {pagename}.{method}(): fields/parameters mismatch") from e
            try:
                for response in handling:
                    yield parse_response(player, response)
            except Exception as e:
                raise RuntimeError(f"Failure at {pagename}.{method}") from e
        elif inspect.isasyncgenfunction(handler):
            try:
                validate_payload(handler.__annotations__, payload)
                handling = handler(player, **payload)
            except (TypeError, AssertionError) as e:
                raise ValueError(f"Invalid payload for {pagename}.{method}(): fields/parameters mismatch") from e
            try:
                async for response in handling:
                    yield parse_response(player, response)
            except Exception as e:
                raise RuntimeError(f"Failure at {pagename}.{method}") from e
        else:
            raise TypeError(f"Invalid {pagename}.{method}: expected a generator with `yield`")


def validate_payload(annotations: dict[str, type], payload: dict):
    for k, v in payload.items():
        assert k not in annotations or isinstance(v, annotations[k]), f"Improper value of `{k}`"


def parse_response(player: BasePlayer, response: Any) -> otLiveData:
    match response:
        case (BaseGroup(), str() as t):
            return {0: {"type": t}}
        case (BaseGroup(), str() as t, dict() as d):
            return {0: {"type": t, **d}}
        case (BasePlayer() as p, str() as t):
            return {p.id_in_group: {"type": t}}
        case (BasePlayer() as p, str() as t, dict() as d):
            return {p.id_in_group: {"type": t, **d}}
        case str() as t:
            return {player.id_in_group: {"type": t}}
        case (str() as t, dict() as d):
            return {player.id_in_group: {"type": t, **d}}
        case _:
            raise ValueError("Invalid yield structure")
