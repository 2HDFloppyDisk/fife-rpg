import os
import yaml

from fife import fife
from fife.extensions.fife_settings import Setting

from fife_rpg import GameSceneView
from fife_rpg import GameSceneController
from fife_rpg.components import ComponentManager

from fife_rpg.behaviours.base import Base
from fife_rpg.actions import ActionManager
from fife_rpg.actions.unlock import UnlockAction
from fife_rpg.components.agent import Agent

from app import Application
from actions import PrintAction

print "Using the FIFE python module found here: ", os.path.dirname(fife.__file__)

TDS = Setting(app_name="rpg", settings_file="./settings.xml")
world = None

   
def create_entity_dictionary(entity):
    entity_dict = {}
    components_data = entity_dict["components"] = {}
    components = ComponentManager.get_components()
    for name, component in components.iteritems():
        component_values = getattr(entity, name)
        if component_values:
            component_data = None
            for field in component.saveable_fields:                
                if not component_data:
                    component_data = components_data[name] = {}                
                component_data[field] = getattr(component_values, field)
    
    return entity_dict
    
MET = []

def met(name):
    return name in MET

def meet(name):
    if not met(name):
        MET.append(name)


    
def main():
    global world
    Base.register()
    PrintAction.register()
    
    app = Application(TDS)
    app.load_components("combined.yaml")
    app.register_components()
    app.load_actions("combined.yaml")
    app.register_actions()
    app.load_systems("combined.yaml")
    app.register_systems()
    app.create_world()
    world = app.world
    view = GameSceneView(app)
    controller = GameSceneController(view, app)
    app.load_maps()
    world.read_object_db()
    world.import_agent_objects()
    world.load_and_create_entities()
    app.switch_map("Level1")

    script_system = getattr(world.systems, "scripting")
    actions = ActionManager.get_actions()
    commands = ComponentManager.get_script_commands()
    script_system.actions = actions
    script_system.commands = commands
    statistic_system = world.systems.character_statistics
    statistic_system.load_statistics_from_file("statistics.yaml")
    player = app.current_map["PlayerCharacter"]
    player.char_stats.gender = "male"
    player.char_stats.primary_stats["ST"] = 75
    player.char_stats.primary_stats["VT"] = 60
    script_system.load_scripts()
    app.push_mode(controller)
    app.run()

if __name__ == '__main__':
    if TDS.get("FIFE", "ProfilingOn"):
        import hotshot.stats
        print "Starting profiler"
        prof = hotshot.Profile("fife.prof")
        prof.runcall(main)
        prof.close()
        print "analysing profiling results"
        stats = hotshot.stats.load("fife.prof")
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)
    else:
        main()
        print "End"
