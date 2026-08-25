"""
Utils to simplify live communicating.
by qwiglydee@gmail.com

Best used with _static/otree-front-live.js

The utils imply all the live messages be dicts(python) / objects(javascript)
with field `type`

Messages are routed and handled according to their type.
"""

import inspect
from typing import Any
from collections.abc import AsyncIterator, Iterator

from otree.api import BaseGroup, BasePlayer, Page

LivePayload = dict[str, Any]
"""Format of messages sent between server and browser"""

LiveResponse = str | tuple[str, LivePayload] | tuple[BasePlayer | BaseGroup, str] | tuple[BasePlayer | BaseGroup, str, LivePayload]
"""Format of yields from a page live handler"""

LiveResponding = Iterator[LiveResponse]
"""Type of page live handler: It should yield one or more live responses"""

AsyncLiveResponding = AsyncIterator[LiveResponse]
"""Type of page live handler: It should yield one or more live responses"""

# internal data for otree core
otLiveData = dict[int, LivePayload]


class LivePage(Page):
    """Page with multiple live methods

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
        handler = getattr(page, method)

        assert inspect.isgeneratorfunction(handler) or inspect.isasyncgenfunction(handler), f"Invalid {pagename}.{method}: expected a generator with `yield`"

        try:
            responding = handle_payload(handler, player, payload)
            if inspect.isgenerator(responding):
                for response in responding:  # type: ignore
                    yield serialize_response(player, response)
            if inspect.isasyncgen(responding):
                async for response in responding:  # type: ignore
                    yield serialize_response(player, response)
        except Exception as e:
            raise RuntimeError(f"Failure at {pagename}.{method}") from e


def handle_payload(handler, player: BasePlayer, payload: dict) -> Iterator[LiveResponse] | AsyncIterator[LiveResponse]:
    annotations = handler.__annotations__
    for k, v in payload.items():
        if k not in annotations:
            raise ValueError(f"Invalid parameter `{k}`")
        if not isinstance(v, annotations[k]):
            raise ValueError(f"Invalid value of `{k}`")
    return handler(player, **payload)


def serialize_response(player: BasePlayer, response: LiveResponse) -> otLiveData:
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
            raise ValueError("Invalid yield format")
