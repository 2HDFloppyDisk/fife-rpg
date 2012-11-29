from fife_rpg.behaviours import behaviour_manager as BehaviourManager
from fife_rpg.helpers import Enum

AGENT_STATES = Enum(["NONE", 
                     "IDLE",
                     "APPROACH",
                     "RUN",
                     "WALK",
                     "TALK"
                     ])
