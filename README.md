```
███████╗██╗   ██╗███████╗███╗   ██╗████████╗██████╗ ██╗   ██╗███████╗
██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝██╔══██╗██║   ██║██╔════╝
█████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║   ██████╔╝██║   ██║███████╗
██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║   ██╔══██╗██║   ██║╚════██║
███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║   ██████╔╝╚██████╔╝███████║
╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═════╝  ╚═════╝ ╚══════╝

# Event Bus

The Event Bus is the communication backbone of AIOS. It enables asynchronous, event-driven communication between all modules without direct dependencies, making the system modular, scalable, and maintainable.

## Features

- Asynchronous event publishing and subscription
- Priority-based event dispatching
- Sync and async handlers
- Middleware support
- Event validation and filtering
- Event persistence and replay
- Dead Letter Queue (DLQ)
- Retry policies
- Event scheduling
- Lifecycle management
- Monitoring and metrics
- Thread-safe architecture

## Architecture

```
Publisher
    │
    ▼
Event Factory
    │
    ▼
Validation
    │
    ▼
Middleware
    │
    ▼
Dispatcher
    │
    ▼
Subscribers
    │
    ▼
Event Store
```

## Dependencies

The Event Bus depends on the following core modules:

- **Configuration** – Loads queue, retry, storage, and worker settings.
- **Constants** – Provides shared event names, priorities, and delivery modes.
- **Exceptions** – Standardized error handling for dispatching and validation.
- **Logging** – Records publishing, dispatching, retries, failures, and performance metrics.

## Event Lifecycle

```
Create Event
      │
Validate
      │
Middleware
      │
Queue
      │
Dispatch
      │
Subscribers
      │
Storage & Metrics
```

## Integrations

The Event Bus is used by:

- Bootstrap
- Dependency Injection
- State Manager
- Database
- Logging
- Security
- Plugin System

## Design Principles

- Event-driven architecture
- Loose coupling
- Thread safety
- Fault tolerance
- High performance
- Extensibility
- Observability
- Offline-first support