import inspect


class DispDepends:
    def __init__(self, provider):
        self.provider = provider


async def resolve_dependencies(func, provided_kwargs: dict) -> dict:
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
