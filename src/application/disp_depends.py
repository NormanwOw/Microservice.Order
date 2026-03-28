import inspect
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


class DispDepends:
    def __init__(self, provider: Callable[..., Any] | Callable[..., Awaitable[Any]]) -> None:
        self.provider = provider


async def resolve_dependencies(
    func: Callable[P, R], provided_kwargs: dict[Any, Any]
) -> dict[str, Any]:
    signature = inspect.signature(func)
    resolved_kwargs = dict(provided_kwargs)

    for name, param in signature.parameters.items():
        if name in resolved_kwargs:
            continue

        default = param.default

        if isinstance(default, DispDepends):
            provider = default.provider

            if inspect.iscoroutinefunction(provider):
                value = await provider()
            else:
                value = provider()

            resolved_kwargs[name] = value

    return resolved_kwargs
