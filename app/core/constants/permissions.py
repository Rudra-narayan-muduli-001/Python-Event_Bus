from __future__ import annotations
from enum import Enum, IntEnum
from types import MappingProxyType
from typing import Final, FrozenSet, Mapping

class Role(str, Enum):
    """Authorization roles. Ranked via ROLE_RANK below."""

    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SYSTEM = "system"  
ROLE_RANK: Final[Mapping[Role, int]] = MappingProxyType(
    {
        Role.GUEST: 0,
        Role.USER: 10,
        Role.ADMIN: 20,
        Role.SUPER_ADMIN: 30,
        Role.SYSTEM: 40,
    }
)

DEFAULT_ROLE: Final[Role] = Role.GUEST

class Capability(str, Enum):
    CONVERSE = "conversation:converse"
    KNOWLEDGE_QUERY = "knowledge:query"
    REALTIME_SEARCH = "search:realtime"
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    PERSONAL_MEMORY_READ = "memory:personal_read"    
    PERSONAL_MEMORY_WRITE = "memory:personal_write"
    SYSTEM_CONTROL = "system:control"
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_DELETE = "file:delete"
    PROCESS_MANAGE = "process:manage"
    REGISTRY_EDIT = "registry:edit"
    POWER_MANAGE = "power:manage"                    
    AUTOMATION_RUN = "automation:run"
    SCHEDULE_TASK = "schedule:task"
    MANAGE_USERS = "security:manage_users"
    MANAGE_PERMISSIONS = "security:manage_permissions"
    VIEW_AUDIT_LOG = "security:view_audit"
    SECURITY_COMMAND = "security:command"
    PLUGIN_INSTALL = "plugin:install"
    PLUGIN_UNINSTALL = "plugin:uninstall"
    PLUGIN_NETWORK = "plugin:network"          
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
HIGH_RISK_CAPABILITIES: Final[FrozenSet[Capability]] = frozenset(
    {
        Capability.FILE_DELETE,
        Capability.REGISTRY_EDIT,
        Capability.PROCESS_MANAGE,
        Capability.POWER_MANAGE,
        Capability.MANAGE_USERS,
        Capability.MANAGE_PERMISSIONS,
        Capability.PLUGIN_INSTALL,
        Capability.PLUGIN_UNINSTALL,
        Capability.SECURITY_COMMAND,
    }
)

_GUEST_CAPS: Final[FrozenSet[Capability]] = frozenset(
    {
        Capability.CONVERSE,
        Capability.KNOWLEDGE_QUERY,
        Capability.SETTINGS_READ,
    }
)

_USER_CAPS: Final[FrozenSet[Capability]] = frozenset(
    {
        Capability.REALTIME_SEARCH,
        Capability.MEMORY_READ,
        Capability.MEMORY_WRITE,
        Capability.PERSONAL_MEMORY_READ,
        Capability.PERSONAL_MEMORY_WRITE,
        Capability.FILE_READ,
        Capability.AUTOMATION_RUN,
        Capability.SCHEDULE_TASK,
    }
)

_ADMIN_CAPS: Final[FrozenSet[Capability]] = frozenset(
    {
        Capability.SYSTEM_CONTROL,
        Capability.FILE_WRITE,
        Capability.FILE_DELETE,
        Capability.PROCESS_MANAGE,
        Capability.POWER_MANAGE,
        Capability.PLUGIN_INSTALL,
        Capability.PLUGIN_UNINSTALL,
        Capability.PLUGIN_NETWORK,
        Capability.VIEW_AUDIT_LOG,
        Capability.SETTINGS_WRITE,
    }
)

_SUPER_ADMIN_CAPS: Final[FrozenSet[Capability]] = frozenset(
    {
        Capability.REGISTRY_EDIT,
        Capability.MANAGE_USERS,
        Capability.MANAGE_PERMISSIONS,
        Capability.SECURITY_COMMAND,
    }
)

_SYSTEM_CAPS: Final[FrozenSet[Capability]] = frozenset(Capability)

ROLE_CAPABILITIES: Final[Mapping[Role, FrozenSet[Capability]]] = MappingProxyType(
    {
        Role.GUEST: _GUEST_CAPS,
        Role.USER: _USER_CAPS,
        Role.ADMIN: _ADMIN_CAPS,
        Role.SUPER_ADMIN: _SUPER_ADMIN_CAPS,
        Role.SYSTEM: _SYSTEM_CAPS,
    }
)


class RiskLevel(IntEnum):

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

CONFIDENCE_AUTO_EXECUTE: Final[float] = 0.90
CONFIDENCE_ASK_USER: Final[float] = 0.60


class PermissionDecision(str, Enum):

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"
    REQUIRE_ELEVATION = "require_elevation"     

def resolve_capabilities(role: Role) -> FrozenSet[Capability]:
    rank = ROLE_RANK[role]
    resolved: set[Capability] = set()
    for candidate, caps in ROLE_CAPABILITIES.items():
        if ROLE_RANK[candidate] <= rank:
            resolved |= caps
    return frozenset(resolved)


def role_has_capability(role: Role, capability: Capability) -> bool:
    return capability in resolve_capabilities(role)


def is_high_risk(capability: Capability) -> bool:
    return capability in HIGH_RISK_CAPABILITIES


def role_at_least(role: Role, minimum: Role) -> bool:
    return ROLE_RANK[role] >= ROLE_RANK[minimum]

__all__ = [
    "Role",
    "ROLE_RANK",
    "DEFAULT_ROLE",
    "Capability",
    "HIGH_RISK_CAPABILITIES",
    "ROLE_CAPABILITIES",
    "RiskLevel",
    "CONFIDENCE_AUTO_EXECUTE",
    "CONFIDENCE_ASK_USER",
    "PermissionDecision",
    "resolve_capabilities",
    "role_has_capability",
    "is_high_risk",
    "role_at_least",
]
