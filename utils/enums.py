from enum import Enum, auto

class ActionType(Enum):
    Ban = auto()
    Kick = auto()
    Unban = auto()
    Timeout = auto()
    TimeoutRemoval = auto()
    ScamKick = auto()
    Warn = auto()
    WarnRemove = auto()

class ServerAction(Enum):
    Join = auto()
    Leave = auto()
    KillboxTrigger = auto()

class MessageLog(Enum):
    Delete = auto()
    Edit = auto()