# Architecture

## Overview

EventBus (`aios-event-bus`) is a Python event-driven architecture framework built around a publish/subscribe pattern with dependency injection, configurable middleware pipelines, tamper-evident audit logging, and a multi-source configuration system.

## Project Structure

```
app/
├── core/
│   ├── configs/                # Configuration loading, validation, environment
│   ├── constants/              # Shared constants (events, paths, settings, limits, etc.)
│   ├── dependency_injection/   # DI container with provider types and lifetime scopes
│   ├── event_bus/              # Core pub/sub event system
│   ├── exceptions/             # Hierarchical exception system (10 categories)
│   └── utils/                  # dict_utils (deep_merge, clamp, within)
└── logging/                    # Full logging subsystem with audit trail
```

## Event Bus (app/core/event_bus/)

The heart of the system — a thread-safe pub/sub event dispatcher with middleware.

### Flow

```
EventBus.publish(event)
  └── EventBus._guard_publish()       # validates running state + strict-mode registry check
       └── Dispatcher.dispatch(event)
            ├── MiddlewareChain.run(event)    # pipeline of Middleware.process()
            ├── Dispatcher._select(event)     # filter subscribers by EventFilter
            ├── Subscriber.invoke(event)      # sync or async handler call
            └── Dispatcher._finalize(event)   # record to EventStore
```

### Key Types

| Type | Responsibility |
|------|---------------|
| `Event` | Data model: name, payload, category, priority, delivery_mode, context, event_id, timestamp, status |
| `EventContext` | Context propagation via `contextvars` (correlation_id, causation_id, source, actor, baggage) |
| `EventPriority` | IntEnum: LOW=10, NORMAL=20, HIGH=30, CRITICAL=40, EMERGENCY=50 |
| `EventFilter` | Composable filter tree (NameFilter, CategoryFilter, AndFilter, OrFilter, NotFilter, etc.) |
| `EventRegistry` | Thread-safe catalog of known event types |
| `EventStore` | In-memory deque + optional SQLite persistence (record, query, replay, prune) |
| `Middleware` | `process(event, next_call) -> Optional[Event]` — returning None drops the event |
| `Publisher` / `ScopedPublisher` | Wraps the publish callable; ScopedPublisher fixes `source` |
| `Subscriber` | Wraps a handler + EventFilter with error policies (ISOLATE/PROPAGATE/DISABLE) |
| `Dispatcher` | Central dispatch engine: middleware chain → subscriber selection → handler invocation → store |
| `EventBus` | Top-level facade: publish, subscribe, emit, register, start/stop lifecycle |

### Default Middleware Pipeline

1. `LoggingMiddleware` — logs every event publish/drop
2. `PriorityStampMiddleware` — resolves and stamps event priority
3. `ContextPropagationMiddleware` — sets `contextvars` context for dispatch duration

Optional middlewares (add via `EventBus.add_middleware()`):
- `DeduplicationMiddleware` — drops duplicate event_ids within a time window
- `RateLimitMiddleware` — per-event-name rate limiting (excludes EMERGENCY)
- `MetricsMiddleware` — counts processed/dropped events per name

## Dependency Injection (app/core/dependency_injection/)

Pattern: Service Locator with auto-wiring.

### Provider Types

| Provider | Behavior |
|----------|----------|
| `InstanceProvider` | Returns a pre-constructed instance |
| `FactoryProvider` | Calls a factory callable (optionally injecting `IContainer`) |
| `ClassProvider` | Inspects `__init__` signature and resolves annotated parameters from the container |

### Lifetime Scopes

| Scope | Behavior |
|-------|----------|
| `TRANSIENT` | New instance every resolution |
| `SINGLETON` | One instance per container |
| `SCOPED` | One instance per `container.scope()` context manager |

### Container

`Container(IContainer)` is thread-safe, detects circular dependencies via a resolution chain, and provides:
- `register(token, provider)`
- `resolve(token) -> T`
- `scope()` context manager
- `register_instance()`, `register_factory()`, `register_class()` helpers

`ContainerBuilder` provides a fluent API: `add_instance()`, `add_singleton()`, `add_transient()`, `add_scoped()`, `add_factory()`.

## Configuration (app/core/configs/)

Multi-source merge pipeline in `load_merged_config()`:

1. **Defaults** (`defaults.py` → `_BASE_DEFAULTS`)
2. **Environment overlay** (dev/test/staging/production specific overrides)
3. **app_config.yaml** (optional)
4. **Domain files** (logging.yaml, feature_flags.yaml, model_registry.yaml, permissions.yaml, etc.)
5. **Environment section** from environment.yaml
6. **Variable interpolation** (`${VAR}` / `${VAR:default}`)
7. **Env var overrides** (`AIOS_CFG__` prefix with `__` path separator)
8. **Validation** (Pydantic v2 if available, else manual)

`ConfigManager` is a thread-safe singleton with typed accessors and change listeners.

Path resolution (`resolve_project_root()`) checks: explicit path → `AIOS_ROOT` env var → walk up from `__file__` for marker files (`pyproject.toml`, `main.py`, `launcher.py`).

## Exceptions (app/core/exceptions/)

Root: `AIOSError` (with severity, category, context, cause, recoverable flag).

### Categories

| Category | File | Subclasses |
|----------|------|------------|
| CONFIGURATION | `configuration.py` | ConfigFileNotFoundError, ConfigParseError, ConfigValidationError, MissingConfigKeyError, InvalidConfigValueError, EnvironmentVariableError, ConfigMergeError |
| DEPENDENCY | `dependency.py` | DependencyNotFoundError, DependencyResolutionError, CircularDependencyError, DuplicateRegistrationError, ProviderError, ScopeError |
| DATABASE | `database.py` | DbConnectionError, TransactionError, MigrationError, QueryError, IntegrityError, BackupError, EncryptionKeyError, VectorStoreError, KnowledgeGraphError |
| STATE | `state.py` | InvalidStateTransitionError, InvalidStateError, StatePersistenceError, StateSnapshotError, StateValidationError, StateLockError |
| EVENT | `event.py` | EventPublishError, EventSubscriptionError, EventHandlerError, EventSerializationError, UnknownEventTypeError, EventDispatchError |
| QUEUE | `queue.py` | QueueFullError, QueueEmptyError, QueueTimeoutError, QueueClosedError, InvalidPriorityError, QueueInterruptedError, QueueOverflowError |
| SECURITY | `security.py` | AuthenticationError, AuthorizationError, PermissionDeniedError, SpeakerVerificationError, RiskThresholdExceededError, FirewallBlockedError, PromptInjectionError, SandboxViolationError, EncryptionError, AuditIntegrityError |
| VALIDATION | `validation.py` | SchemaValidationError, ParameterValidationError, TypeCoercionError, ConstraintViolationError, MissingFieldError, ToolValidationError |
| STARTUP | `startup.py` | InitializationError, BootstrapError, ServiceStartupError, FeatureGroupInitError, PhaseInitializationError, StartupTimeoutError, ShutdownError |
| RUNTIME | `runtime.py` | OperationError, TimeoutError_, RetryExhaustedError, ResourceExhaustedError, ToolExecutionError, ModelInferenceError, ExternalServiceError, NotSupportedError, RecoveryError |

## Logging (app/logging/)

### Subsystem

```
LoggerFactory (caches all loggers)
  ├── ConsoleHandler       # WARNING+ → stderr, INFO- → stdout, colorized
  ├── FileLogHandler       # Plain file output
  ├── RotatingFileLogHandler  # Delegates to size/time rotators with gzip
  ├── CompositeHandler     # Fans out to multiple sub-handlers
  └── AuditLogger          # Tamper-evident HMAC-SHA256 chain
```

### Formatters

- `ConsoleFormatter` — colorized terminal output with dimmed timestamps, bold level
- `JSONFormatter` — structured JSON with timestamp, level, logger, module, function, line, message, process/thread, extras, exception
- `DetailedFileFormatter` — bracketed verbose: `[timestamp] [LEVEL] [logger] [module.func:line] ...`

### Filters

- `LevelFilter` — minimum level gate
- `ModuleFilter` — regex include/exclude on logger name
- `RateLimitFilter` — sliding window + cooldown per message key
- `ContextFilter` — injects dynamic key-value pairs

### AuditLogger

Tamper-evident audit trail using HMAC-SHA256 chaining:

- `AuditEntry` fields: seq, timestamp, level, logger, event, user, action, result, risk_level, details, prev_hmac, hmac
- Each entry's `prev_hmac` links to the previous entry's HMAC
- `verify_log_file()` traverses the entire file and validates the chain
- Convenience methods: auth_success, auth_failure, permission_denied, risk_escalation, prompt_blocked, tool_execution, rollback
