from __future__ import annotations
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping, FrozenSet


class BaseState(str, Enum):

    def __str__(self) -> str:  
        return self.value

class AppState(BaseState):
    CREATED = "created"
    BOOTSTRAPPING = "bootstrapping"
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"      
    PAUSING = "pausing"
    PAUSED = "paused"
    RESUMING = "resuming"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    SHUTDOWN = "shutdown"


APP_STATE_TRANSITIONS: Final[Mapping[AppState, FrozenSet[AppState]]] = MappingProxyType(
    {
        AppState.CREATED: frozenset({AppState.BOOTSTRAPPING, AppState.ERROR}),
        AppState.BOOTSTRAPPING: frozenset({AppState.INITIALIZING, AppState.ERROR}),
        AppState.INITIALIZING: frozenset({AppState.STARTING, AppState.ERROR}),
        AppState.STARTING: frozenset({AppState.RUNNING, AppState.ERROR}),
        AppState.RUNNING: frozenset(
            {AppState.DEGRADED, AppState.PAUSING, AppState.STOPPING, AppState.ERROR}
        ),
        AppState.DEGRADED: frozenset({AppState.RUNNING, AppState.STOPPING, AppState.ERROR}),
        AppState.PAUSING: frozenset({AppState.PAUSED, AppState.ERROR}),
        AppState.PAUSED: frozenset({AppState.RESUMING, AppState.STOPPING}),
        AppState.RESUMING: frozenset({AppState.RUNNING, AppState.ERROR}),
        AppState.STOPPING: frozenset({AppState.STOPPED, AppState.ERROR}),
        AppState.STOPPED: frozenset({AppState.SHUTDOWN}),
        AppState.ERROR: frozenset({AppState.STOPPING, AppState.SHUTDOWN}),
        AppState.SHUTDOWN: frozenset(),  # Terminal
    }
)

class VoiceState(BaseState):

    IDLE = "idle"
    WAITING_WAKE = "waiting_wake"
    VERIFYING = "verifying"
    AUTHORIZED = "authorized"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"
    DEAUTHORIZED = "deauthorized"
    SHUTDOWN = "shutdown"

class BrainState(BaseState):

    OFFLINE = "offline"
    STARTING = "starting"
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING_INPUT = "processing_input"
    VERIFYING_IDENTITY = "verifying_identity"
    CLASSIFYING_INTENT = "classifying_intent"
    BUILDING_CONTEXT = "building_context"
    PLANNING = "planning"
    SEARCHING = "searching"
    EXECUTING_TOOL = "executing_tool"
    WAITING_FOR_TOOL = "waiting_for_tool"
    GENERATING_RESPONSE = "generating_response"
    SPEAKING = "speaking"
    WAITING_FOR_USER = "waiting_for_user"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class SecurityState(BaseState):

    STARTING = "starting"
    VERIFYING_IDENTITY = "verifying_identity"
    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"
    CHECKING_PERMISSIONS = "checking_permissions"
    EVALUATING_RISK = "evaluating_risk"
    RUNNING_FIREWALL = "running_firewall"
    VALIDATING_TOOL = "validating_tool"
    EXECUTING_SANDBOX = "executing_sandbox"
    ACCESSING_STORAGE = "accessing_storage"
    LOGGING = "logging"
    RECOVERING = "recovering"
    SHUTDOWN = "shutdown"


class TaskState(BaseState):

    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING = "waiting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

TERMINAL_TASK_STATES: Final[FrozenSet[TaskState]] = frozenset(
    {TaskState.COMPLETED, TaskState.CANCELLED, TaskState.FAILED}
)


class ActionState(BaseState):

    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING_NATIVE = "executing_native"     
    EXECUTING_VISION = "executing_vision"     
    EXECUTING_VLM = "executing_vlm"           
    VERIFYING = "verifying"
    SUCCEEDED = "succeeded"
    RETRYING = "retrying"
    ROLLING_BACK = "rolling_back"
    FAILED = "failed"


class GuiMode(BaseState):

    DASHBOARD = "dashboard"
    COMPANION_2D = "companion_2d"
    COMPANION_3D = "companion_3d"
    SMART_CURSOR = "smart_cursor"


class CharacterState(BaseState):

    IDLE = "idle"
    PLAYING = "playing"
    WALKING = "walking"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ALERT = "alert"
    SLEEPING = "sleeping"


class ConnectivityState(BaseState):

    ONLINE = "online"
    OFFLINE = "offline"
    LIMITED = "limited"     
    UNKNOWN = "unknown"

INITIAL_STATES: Final[Mapping[str, BaseState]] = MappingProxyType(
    {
        "app": AppState.CREATED,
        "voice": VoiceState.IDLE,
        "brain": BrainState.OFFLINE,
        "security": SecurityState.STARTING,
        "task": TaskState.QUEUED,
        "action": ActionState.PENDING,
        "gui": GuiMode.DASHBOARD,
        "character": CharacterState.IDLE,
        "connectivity": ConnectivityState.UNKNOWN,
    }
)

def can_transition(current: AppState, target: AppState) -> bool:
    return target in APP_STATE_TRANSITIONS.get(current, frozenset())


def is_terminal_task_state(state: TaskState) -> bool:
    return state in TERMINAL_TASK_STATES

__all__ = [
    "BaseState",
    "AppState",
    "APP_STATE_TRANSITIONS",
    "VoiceState",
    "BrainState",
    "SecurityState",
    "TaskState",
    "TERMINAL_TASK_STATES",
    "ActionState",
    "GuiMode",
    "CharacterState",
    "ConnectivityState",
    "INITIAL_STATES",
    "can_transition",
    "is_terminal_task_state",
]
