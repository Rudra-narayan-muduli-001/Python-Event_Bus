from __future__ import annotations
import enum
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from app.core.exceptions import ScopeError
from app.logging import Logger

__all__ = [
    "Lifetime",
    "Scope",
    "ScopeManager",
]


class Lifetime(str, enum.Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class Scope:
    def __init__(self, name: str, *, parent: Optional["Scope"] = None) -> None:
        self.name = name
        self.parent = parent
        self._instances: Dict[Any, Any] = {}
        # (token, instance, disposer) preserved in creation order.
        self._disposables: List[Tuple[Any, Any, Callable[[Any], None]]] = []
        self._lock = threading.RLock()
        self._active = True
    @property
    def active(self) -> bool:
        return self._active

    def has(self, token: Any) -> bool:
        with self._lock:
            return token in self._instances

    def get(self, token: Any) -> Any:
        with self._lock:
            self._ensure_active(token)
            if token not in self._instances:
                raise ScopeError(
                    token,
                    self.name,
                    reason="instance not present in scope",
                )
            return self._instances[token]

    def set(
        self,
        token: Any,
        instance: Any,
        disposer: Optional[Callable[[Any], None]] = None,
    ) -> None:
        with self._lock:
            self._ensure_active(token)
            self._instances[token] = instance
            if disposer is not None:
                self._disposables.append((token, instance, disposer))

    def dispose(self) -> None:
        with self._lock:
            if not self._active:
                return
            self._active = False
            errors: List[str] = []
            for token, instance, disposer in reversed(self._disposables):
                try:
                    disposer(instance)
                except Exception as exc:  
                    errors.append(f"{token!r}: {exc}")
            self._disposables.clear()
            self._instances.clear()
            if errors:
                raise ScopeError(
                    self.name,
                    self.name,
                    reason=f"disposer failures: {'; '.join(errors)}",
                )
    def _ensure_active(self, token: Any) -> None:
        if not self._active:
            raise ScopeError(
                token,
                self.name,
                reason="scope has been disposed",
            )
    def __enter__(self) -> "Scope":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.dispose()

    def __repr__(self) -> str:  
        state = "active" if self._active else "disposed"
        return f"<Scope name={self.name!r} state={state} items={len(self._instances)}>"


class ScopeManager:
    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._logger = logger
        self._singletons: Dict[Any, Any] = {}
        self._singleton_disposers: List[Tuple[Any, Callable[[Any], None]]] = []
        self._lock = threading.RLock()
        self._local = threading.local()
    def has_singleton(self, token: Any) -> bool:
        with self._lock:
            return token in self._singletons

    def get_singleton(self, token: Any) -> Any:
        with self._lock:
            return self._singletons[token]

    def set_singleton(
        self,
        token: Any,
        instance: Any,
        disposer: Optional[Callable[[Any], None]] = None,
    ) -> None:
        with self._lock:
            self._singletons[token] = instance
            if disposer is not None:
                self._singleton_disposers.append((token, disposer))
    @property
    def _scope_stack(self) -> List[Scope]:
        stack = getattr(self._local, "stack", None)
        if stack is None:
            stack = []
            self._local.stack = stack
        return stack

    @property
    def current_scope(self) -> Optional[Scope]:
        stack = self._scope_stack
        return stack[-1] if stack else None

    def create_scope(self, name: str) -> Scope:
        return Scope(name, parent=self.current_scope)

    def push_scope(self, scope: Scope) -> None:
        self._scope_stack.append(scope)
        if self._logger:
            self._logger.debug("Scope pushed", extra={"scope": scope.name})

    def pop_scope(self) -> Scope:
        stack = self._scope_stack
        if not stack:
            raise ScopeError("<none>", "current", reason="no active scope to pop")
        scope = stack.pop()
        if self._logger:
            self._logger.debug("Scope popped", extra={"scope": scope.name})
        return scope

    def require_current_scope(self, token: Any) -> Scope:
        scope = self.current_scope
        if scope is None or not scope.active:
            raise ScopeError(
                token,
                "scoped",
                reason="no active scope; resolve a scoped service inside a Scope",
            )
        return scope
    def dispose_singletons(self) -> None:
        with self._lock:
            for token, disposer in reversed(self._singleton_disposers):
                try:
                    disposer(self._singletons.get(token))
                except Exception as exc:  
                    if self._logger:
                        self._logger.error(
                            "Singleton disposer failed",
                            extra={"token": repr(token), "error": str(exc)},
                        )
            self._singleton_disposers.clear()
            self._singletons.clear()

    def __repr__(self) -> str:  
        return (
            f"<ScopeManager singletons={len(self._singletons)} "
            f"active_scope={self.current_scope!r}>"
        )
