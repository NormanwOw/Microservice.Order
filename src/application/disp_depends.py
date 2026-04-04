import inspect
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

P = ParamSpec('P')
R = TypeVar('R')


class DispDepends:
    def __init__(self, provider: Callable[..., Any] | Callable[..., Awaitable[Any]]) -> None:
        self.provider = provider


async def resolve_dependencies(
    func: Callable[P, Awaitable[R]],
    provided_kwargs: dict[Any, Any],
) -> dict[str, Any]:
    signature = inspect.signature(func)
    resolved_kwargs = dict(provided_kwargs)

    type_hints = get_type_hints(func, include_extras=True)

    for name, param in signature.parameters.items():
        if name in resolved_kwargs:
            continue

        annotation = type_hints.get(name)

        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            metadata = args[1:]

            for meta in metadata:
                if isinstance(meta, DispDepends):
                    provider = meta.provider

                    if inspect.iscoroutinefunction(provider):
                        value = await provider()
                    else:
                        value = provider()

                    resolved_kwargs[name] = value
                    break

        elif isinstance(param.default, DispDepends):
            provider = param.default.provider

            if inspect.iscoroutinefunction(provider):
                value = await provider()
            else:
                value = provider()

            resolved_kwargs[name] = value

    return resolved_kwargs
