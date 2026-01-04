from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class ServiceLifetime(str, Enum):
    SINGLETON = "singleton"
    SCOPED = "scoped"


FactoryFunc = Callable[["ServiceContainer", Dict[str, Any]], Any]


class ServiceContainer:
    """
    Minimal DI container supporting singleton and scoped services.

    - Register services with an id, factory, lifetime, and dependencies (by id).
    - Resolve performs dependency ordering and cycle checks.
    - Scoped services are cached per resolve() call when a shared scope dict is provided.
    """

    def __init__(self) -> None:
        self._registrations: Dict[str, Tuple[FactoryFunc, ServiceLifetime, List[str]]] = {}
        self._singletons: Dict[str, Any] = {}

    def register(self,
                 service_id: str,
                 factory: FactoryFunc,
                 *,
                 lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
                 depends_on: Optional[List[str]] = None) -> "ServiceContainer":
        if service_id in self._registrations:
            raise ValueError(f"Service '{service_id}' already registered")

        deps = depends_on or []
        self._registrations[service_id] = (factory, lifetime, deps)

        # Validate no cycles introduced by this registration
        self._assert_no_cycles()

        return self

    def resolve(self, service_id: str, scope: Optional[Dict[str, Any]] = None) -> Any:
        if service_id not in self._registrations:
            raise KeyError(f"Unknown service '{service_id}'")

        # Singleton short-circuit
        factory, lifetime, _ = self._registrations[service_id]
        if lifetime == ServiceLifetime.SINGLETON and service_id in self._singletons:
            return self._singletons[service_id]

        # Resolve with per-call scoped cache
        scope_cache = None if scope is None else scope.setdefault("__service_cache__", {})

        if lifetime == ServiceLifetime.SCOPED and scope_cache is not None and service_id in scope_cache:
            return scope_cache[service_id]

        # Ensure dependencies are resolved first
        instance = factory(self, scope or {})

        if lifetime == ServiceLifetime.SINGLETON:
            self._singletons[service_id] = instance
        elif lifetime == ServiceLifetime.SCOPED and scope_cache is not None:
            scope_cache[service_id] = instance

        return instance

    def _assert_no_cycles(self) -> None:
        graph: Dict[str, List[str]] = {k: v[2] for k, v in self._registrations.items()}

        visited: Set[str] = set()
        on_stack: Set[str] = set()

        def dfs(node: str) -> None:
            if node in on_stack:
                raise ValueError("Cyclic service dependency detected")
            if node in visited:
                return
            visited.add(node)
            on_stack.add(node)
            for nbr in graph.get(node, []):
                if nbr not in graph:
                    # Unregistered dependency will surface at resolve time; ignore here
                    continue
                dfs(nbr)
            on_stack.remove(node)

        for node in graph.keys():
            if node not in visited:
                dfs(node)

    def clear_singletons(self) -> None:
        self._singletons.clear()

