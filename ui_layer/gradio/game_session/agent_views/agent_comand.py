from enum import Enum, auto

class AgentCommand(Enum):
    PLAY = auto()
    PAUSE = auto()
    STEP = auto()