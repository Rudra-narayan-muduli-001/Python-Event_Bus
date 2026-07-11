from __future__ import annotations
from app.core.constants import app as app
from app.core.constants import states as states
from app.core.constants import events as events
from app.core.constants import permissions as permissions
from app.core.constants import models as models
from app.core.constants import languages as languages
from app.core.constants import paths as paths
from app.core.constants import settings as settings
from app.core.constants import limits as limits
from app.core.constants import errors as errors
from app.core.constants.app import *          
from app.core.constants.states import *       
from app.core.constants.events import *       
from app.core.constants.permissions import *  
from app.core.constants.models import *      
from app.core.constants.languages import *    
from app.core.constants.paths import *        
from app.core.constants.settings import *    
from app.core.constants.limits import *       
from app.core.constants.errors import *      
from app.core.constants.app import APP_VERSION as __version__


def _build_all() -> list[str]:
    names: list[str] = [
        "app",
        "states",
        "events",
        "permissions",
        "models",
        "languages",
        "paths",
        "settings",
        "limits",
        "errors",
        "__version__",
    ]
    for module in (
        app,
        states,
        events,
        permissions,
        models,
        languages,
        paths,
        settings,
        limits,
        errors,
    ):
        names.extend(getattr(module, "__all__", ()))
    seen: set[str] = set()
    unique: list[str] = []
    for name in names:
        if name not in seen:
            seen.add(name)
            unique.append(name)
    return unique


__all__ = _build_all()
