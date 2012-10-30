from fife import fife
from fife.fife import InstanceRenderer

from fife_rpg import RPGApplication
from fife_rpg.rpg_application import ApplicationListener
from fife_rpg import GameSceneController
from fife_rpg.actions import ActionManager
from fife_rpg import DialogueController
from fife.extensions.pychan.internal import get_manager

class Listener(ApplicationListener, fife.IMouseListener, fife.PercentDoneListener):
    def __init__(self, engine, application):
        ApplicationListener.__init__(self, engine, application)
        fife.IMouseListener.__init__(self)
        self._eventmanager.addMouseListener(self)
        fife.PercentDoneListener.__init__(self)
        
    def mouseEntered(self, event):#pylint: disable=W0221
        pass
    
    def mouseExited(self, event):#pylint: disable=W0221
        pass

    def mousePressed(self, event):#pylint: disable=W0221
        player = self._application.world.get_or_create_entity("PlayerCharacter")
        if event.getButton() == fife.MouseEvent.LEFT:
            scr_point = self._application.getCoords(
                            fife.ScreenPoint(event.getX(), event.getY())
                            )
            coords = scr_point.getExactLayerCoordinates()
            player.fifeagent.behaviour.run(scr_point)
            print player.agent.position            
        elif event.getButton() == fife.MouseEvent.RIGHT:
            if self._application.language == "en":
                self._application.language = "de"
            else:
                self._application.language = "en"                
            controller = self._application.current_mode
            world = self._application.world
            if isinstance(controller, GameSceneController):
                game_map = self._application.current_map
                if game_map:
                    pt = fife.ScreenPoint(event.getX(), event.getY())
                    actor_instances = game_map.get_instances_at(
                                                        pt, 
                                                        game_map.actor_layer)
                    if actor_instances:
                        for actor in actor_instances:
                            identifier = actor.getId()
                            if identifier == "PlayerCharacter":
                                continue
                            entity = world.get_entity(identifier)
                            possible_actions = ActionManager.get_possible_actions(
                                                                         player, 
                                                                         entity) 
                            actions = {}
                            for name, action in possible_actions.iteritems():
                                actions[name] = action(self._application, player, entity)
                                print actions[name].menu_text
                            
                                if actions.has_key("Look"):
                                    actions["Look"].execute()
                                if actions.has_key("Read"):
                                    actions["Read"].execute()
                                                      
                    item_instances = game_map.get_instances_at(
                                                        pt, 
                                                        game_map.item_layer)
                    if item_instances:
                        for item in item_instances:
                            identifier = item.getId()
                            entity = world.get_entity(identifier)
                            possible_actions = ActionManager.get_possible_actions(
                                                                         player, 
                                                                         entity) 
                            actions = {}
                            for name, action in possible_actions.iteritems():
                                actions[name] = action(self._application, player, entity)
                                print actions[name].menu_text
                                if actions.has_key("Look"):
                                    actions["Look"].execute()

                    ground_instances = game_map.get_instances_at(
                                                        pt, 
                                                        game_map.ground_object_layer)
                    if ground_instances:
                        for ground_object in ground_instances:
                            identifier = ground_object.getId()
                            entity = world.get_entity(identifier)
                            possible_actions = ActionManager.get_possible_actions(
                                                                         player, 
                                                                         entity) 
                            actions = {}
                            for name, action in possible_actions.iteritems():
                                actions[name] = action(self._application, player, entity)
                                print actions[name].menu_text
                            if actions.has_key("ChangeMap"):
                                actions["ChangeMap"].execute()

    def mouseReleased(self, event):#pylint: disable=W0221
        pass

    def mouseClicked(self, event):#pylint: disable=W0221
        pass
    
    def mouseWheelMovedUp(self, event):#pylint: disable=W0221
        char_system = self._application.world.systems.character_statistics
        if char_system.can_increase_statistic("PlayerCharacter", "ST"):
            char_system.increase_statistic("PlayerCharacter", "ST")
            print char_system.get_statistic_value("PlayerCharacter", "ST")
            print char_system.get_statistic_value("PlayerCharacter", "MD")

    def mouseWheelMovedDown(self, event):#pylint: disable=W0221
        char_system = self._application.world.systems.character_statistics
        if char_system.can_decrease_statistic("PlayerCharacter", "ST"):
            char_system.decrease_statistic("PlayerCharacter", "ST")
            print char_system.get_statistic_value("PlayerCharacter", "ST")
            print char_system.get_statistic_value("PlayerCharacter", "MD")

    def mouseMoved(self, event):#pylint: disable=W0221
        controller = self._application.current_mode
        if isinstance(controller, GameSceneController):
            game_map = self._application.current_map
            if game_map:
                renderer = InstanceRenderer.getInstance(game_map.camera)
                
                renderer.removeAllOutlines()
    
                pt = fife.ScreenPoint(event.getX(), event.getY())
                actor_instances = game_map.get_instances_at(
                                                    pt, 
                                                    game_map.actor_layer)
                
                item_instances = game_map.get_instances_at(
                                                    pt, 
                                                    game_map.item_layer)
                ground_instances = game_map.get_instances_at(
                                                    pt, 
                                                    game_map.ground_object_layer)
                
                for i in actor_instances:
                    if i.getId() != "PlayerCharacter":
                        renderer.addOutlined(i, 173, 255, 47, 2)
                    
                for j in item_instances:
                    renderer.addOutlined(j, 255, 173, 47, 2)
            
                for k in ground_instances:
                    renderer.addOutlined(k, 100, 47, 255, 2)
                
    def mouseDragged(self, event):#pylint: disable=W0221
        pass
    
    def onEvent(self, percentage):
        raise Exception("")
        print percentage
    
class Application(RPGApplication):
    
    def __init__(self, TDS):
        RPGApplication.__init__(self, TDS)
        self.map_region_nodes = {} 
        
    def createListener(self):
        self._listener = Listener(self.engine,  self)
        return self._listener
    
    def switch_map(self, name):
        RPGApplication.switch_map(self, name)
        if not self.map_region_nodes.has_key(name):
            self.map_region_nodes[name] = {}
        map_dict = self.map_region_nodes[name]        
        renderer = fife.GenericRenderer.getInstance(self.current_map.camera)
        renderer.addActiveLayer(self.current_map.ground_object_layer)
        renderer.setEnabled(True)
        renderer.removeAll("region")
        for name, region in self.current_map.regions.iteritems():
            if not map_dict.has_key(name):
                region_dict = map_dict[name] = []
                point1 = fife.ExactModelCoordinate(region.x, region.y)
                loc1 = fife.Location(self.current_map.ground_object_layer) 
                loc1.setExactLayerCoordinates(point1)
                node1 = fife.RendererNode(loc1)
                region_dict.append(node1)
                
                point2 = fife.ExactModelCoordinate(region.x, 
                                                   region.y + region.h)
                loc2 = fife.Location(self.current_map.ground_object_layer) 
                loc2.setExactLayerCoordinates(point2)
                node2 = fife.RendererNode(loc2)
                region_dict.append(node2)
                
                point3 = fife.ExactModelCoordinate(region.x + region.w, 
                                                   region.y + region.h)
                loc3 = fife.Location(self.current_map.ground_object_layer) 
                loc3.setExactLayerCoordinates(point3)
                node3 = fife.RendererNode(loc3)
                region_dict.append(node3)
                
                point4 = fife.ExactModelCoordinate(region.x + region.w, 
                                                   region.y)
                loc4 = fife.Location(self.current_map.ground_object_layer) 
                loc4.setExactLayerCoordinates(point4)
                node4 = fife.RendererNode(loc4)
                region_dict.append(node4)
            else:
                region_dict = map_dict[name]
            renderer.addQuad("region", region_dict[0], region_dict[1],
                             region_dict[2], region_dict[3],
                             255, 0, 0, 127)
              
    def getCoords(self, click):
        """Get the map location x, y coordinates from the screen coordinates
           @type click: fife.ScreenPoint
           @param click: Screen coordinates
           @rtype: fife.Location
           @return: The map coordinates
        """
        active_map = self.current_map
        coord = active_map.camera.toMapCoordinates(click, False)
        coord.z = 0
        location = fife.Location(active_map.actor_layer)
        location.setMapCoordinates(coord)
        return location
    
    def pump(self, dt):
        """Performs actions every frame.        
        
        Args:
            dt: Time elapsed since last call to pump
        """
        RPGApplication.pump(self, dt)