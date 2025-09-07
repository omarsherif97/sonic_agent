# src/Agents/runtime.py
import os, importlib
from pymongo import MongoClient

from langgraph.checkpoint.mongodb import MongoDBSaver

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DB_NAME      = os.getenv("MONGODB_DB_NAME", os.getenv("MONGODB_DB", "seq_sonic"))

_client       = MongoClient(MONGODB_URI)
_checkpointer = None
_apps         = {}

async def get_app(key: str, module_path: str):
    """Return a compiled app (memoized). Compiles with MongoDBSaver once."""
    global _checkpointer
    if key in _apps:
        return _apps[key]

    # lazy create the checkpointer inside a running loop
    if _checkpointer is None:
        _checkpointer = MongoDBSaver(_client, db_name=DB_NAME)

    mod      = importlib.import_module(module_path)
    builder  = getattr(mod, "builder", None)
    compiled = getattr(mod, "compiled_graph", None)

    if builder is not None:
        app = builder.compile(checkpointer=_checkpointer)
    elif compiled is not None:
        app = compiled
    else:
        raise ImportError(f"No 'builder' or 'compiled_graph' in {module_path}")

    _apps[key] = app
    return app

# convenience wrappers
async def get_sonic_app():
    return await get_app("sonic", "src.Agents.sonic.graph")

async def get_wso2_app():
    return await get_app("wso2", "src.Agents.smart_wso2_assistant.graph")

async def get_mw_migration_app():
    return await get_app("mw_migration", "src.Agents.mw_migration.graph")
    
async def get_checkpointer():
    return _checkpointer