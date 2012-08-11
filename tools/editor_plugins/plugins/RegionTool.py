# -*- coding: utf-8 -*-

# ####################################################################
#  Copyright (C) 2005-2009 by the FIFE team
#  http://www.fifengine.de
#  This file is part of FIFE.
#
#  FIFE is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the
#  Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# ####################################################################

""" A region tool for FIFedit """
import os

import yaml

from fife import fife
from fife.extensions import pychan
from fife.extensions.pychan.tools import callbackWithArguments as cbwa
from fife.extensions.pychan.internal import get_manager

import scripts.plugin as plugin
import scripts.editor

from scripts.events import postMapShown, preMapClosed, postSave
from scripts.gui.action import Action

from scripts.gui.regiondialog import RegionDialog, Region

# plugin default settings
_PLUGIN_SETTINGS = {
    'module' : "RegionToolSettings",
    'items' : {
        'dockarea' : 'left',
        'docked' : True,
        
    },
}

class RegionTool(plugin.Plugin):
    """ The B{RegionTool} allows to select and show / hide regions of a loaded
        map as well as creating new regions or edit region properties
    """
    
    # default should be pychan default, highlight can be choosen (format: r,g,b)
    DEFAULT_BACKGROUND_COLOR = pychan.internal.DEFAULT_STYLE['default']['base_color']
    HIGHLIGHT_BACKGROUND_COLOR = pychan.internal.DEFAULT_STYLE['default']['selection_color']

    # the dynamicly created widgets have the name scheme prefix + regionid
    LABEL_NAME_PREFIX = "select_"

    def __init__(self):    
        super(RegionTool, self).__init__()
        # Editor instance
        self._editor = scripts.editor.getEditor()
        self.regions = {}
        self.selected_region = None
        
        # Plugin variables
        self._enabled = False
        
        # Current mapview
        self._mapview = None
        
        # Toolbar button to display RegionTool
        self._action_show = None
        
        # GUI
        self._region_wizard = None
        self.container = None
        self.wrapper = None
        self.remove_region_button = None
        self.create_region_button = None
        self.edit_region_button = None
        
        self.default_settings = _PLUGIN_SETTINGS
        self.eds = self._editor._settings
        self.update_settings()
        self.renderer = None
        self.region_layer = None
            
    #--- Plugin functions ---#
    def enable(self):
        """ Enable plugin """
        if self._enabled: return
            
        # Fifedit plugin data
        self._action_show = Action(u"RegionTool", checkable=True)
        scripts.gui.action.activated.connect(self.toggle, sender=self._action_show)
        self._editor._tools_menu.addAction(self._action_show)

        self.create()
        self.toggle()
        
        postMapShown.connect(self.onNewMap)
        preMapClosed.connect(self._mapClosed)
        postSave.connect(self.save)
        
        if self.settings['docked']:
            self._editor.dockWidgetTo(self.container, self.settings['dockarea'])

    def disable(self):
        """ Disable plugin """
        if not self._enabled: return
        
        self.container.setDocked(False)
        self.container.hide()
        
        postMapShown.disconnect(self.update)
        preMapClosed.disconnect(self._mapClosed)
        
        self._editor._tools_menu.removeAction(self._action_show)

    def isEnabled(self):
        """ Returns True if plugin is enabled """
        return self._enabled;

    def getName(self):
        """ Return plugin name """
        return u"Regiontool"
    
    #--- End plugin functions ---#
    def _mapClosed(self):
        self.onNewMap(mapview=None)
        
    
    def showRegionWizard(self):
        """ Show region wizard """
        if not self._mapview: return
        
        if self._region_wizard: self._region_wizard._widget.hide()
        self._region_wizard = RegionDialog(self._editor.getEngine(), self.regions, 
                                           callback=self._regionCreated)
        
    def showEditDialog(self):
        """ Show regiondialog for active region """
        if not self._mapview: return
        if not self.selected_region: return
        
        if self._region_wizard: self._region_wizard._widget.hide()
        callback = lambda region: self._regionEdited(self.selected_region, region)
        self._region_wizard = RegionDialog(self._editor.getEngine(), 
                                           self.regions, region=self.selected_region, 
                                           callback=callback
                                           )
        
    def clear_region_list(self):
        """ Remove all subwrappers """
        self.wrapper.removeAllChildren()
   
    def onNewMap(self, mapview):
        """ Update regiontool with information from mapview
               
        @type    event:    scripts.MapView
        @param    event:    the view of the new map
        """
        self._mapview = mapview
        self.regions = {}        
        layer_list = []
        if not mapview is None:
            self.renderer = fife.GenericRenderer.getInstance(
                                                    self._mapview.getCamera())
            self.renderer.setEnabled(True)
            layers = self._mapview.getMap().getLayers()
            for layer in reversed(layers):
                layer_list.append(layer.getId())
            try:
                filename = mapview.getMap().getFilename()
                filename = "%s_regions.yaml" % os.path.splitext(filename)[0]
                regions_file = file(filename, "r")
                for name, region_data in yaml.load(regions_file).iteritems():
                    x_pos = region_data[0]
                    y_pos = region_data[1]
                    width = region_data[2]
                    height = region_data[3]
                    rect = fife.DoubleRect(x_pos, y_pos, width, height)
                    region = Region(name, rect)                    
                    self.regions[name] = region
            except (RuntimeError, IOError):                     
                pass
        self.select_layer_drop_down.setInitialData(layer_list)
        size = [self.container.size[0], 15]
        self.select_layer_drop_down.min_size = size
        self.select_layer_drop_down.size = size
        self.select_layer_drop_down.selected = 0
        self.update_region_layer()                    
        self.update()
   
    def update_region_layer(self):
        """Updates the layer the regions are drawn on"""
        if self._mapview is None:
            return
        layer_id = self.select_layer_drop_down.selected_item
        self.region_layer = self._mapview.getMap().getLayer(layer_id)
        self.renderer.addActiveLayer(self.region_layer)
        self.update()
               
    def update(self):
        """ Update regiontool
        
        We group one ToggleButton and one Label into a HBox, the main wrapper
        itself is a VBox and we also capture both the Button and the Label to listen
        for mouse actions
        """
        self.clear_region_list()
        if len(self.regions) <= 0:
            if not self._mapview:
                regionid = "No map is open"
            else:
                regionid = "No regions"
            subwrapper = pychan.widgets.HBox()

            regionLabel = pychan.widgets.Label()
            regionLabel.text = unicode(regionid)
            regionLabel.name = RegionTool.LABEL_NAME_PREFIX + regionid
            subwrapper.addChild(regionLabel)
            
            self.wrapper.addChild(subwrapper)
        if self._mapview:
            self.renderer.removeAll("region")
            for name, region in self.regions.iteritems():
                rect = region.rect
                region_dict = []
                point1 = fife.ExactModelCoordinate(rect.x, rect.y)
                loc1 = fife.Location(self.region_layer) 
                loc1.setExactLayerCoordinates(point1)
                node1 = fife.RendererNode(loc1)
                region_dict.append(node1)
                
                point2 = fife.ExactModelCoordinate(rect.x, 
                                                   rect.y + rect.h)
                loc2 = fife.Location(self.region_layer) 
                loc2.setExactLayerCoordinates(point2)
                node2 = fife.RendererNode(loc2)
                region_dict.append(node2)
                
                point3 = fife.ExactModelCoordinate(rect.x + rect.w, 
                                                   rect.y + rect.h)
                loc3 = fife.Location(self.region_layer) 
                loc3.setExactLayerCoordinates(point3)
                node3 = fife.RendererNode(loc3)
                region_dict.append(node3)
                
                point4 = fife.ExactModelCoordinate(rect.x + rect.w, 
                                                   rect.y)
                loc4 = fife.Location(self.region_layer) 
                loc4.setExactLayerCoordinates(point4)
                node4 = fife.RendererNode(loc4)
                region_dict.append(node4)
                color = [255, 0, 0, 127]
                if name == self.selected_region:
                    color[3] = 255
                self.renderer.addQuad("region", region_dict[0], region_dict[1],
                                 region_dict[2], region_dict[3],
                                 *color)
                font = get_manager().getDefaultFont()
                self.renderer.addText("region", region_dict[0], font, name)
                
        for region in self.regions.itervalues():
            regionid = region.name
            subwrapper = pychan.widgets.HBox()
           
            regionLabel = pychan.widgets.Label()
            regionLabel.text = unicode(regionid)
            regionLabel.name = RegionTool.LABEL_NAME_PREFIX + regionid
            regionLabel.capture(self.selectRegion, "mousePressed")          

            subwrapper.addChild(regionLabel)
            
            self.wrapper.addChild(subwrapper)        

        self.container.adaptLayout()                    
        
    def selectRegion(self, event, widget=None, regionid=None):
        """ Callback for Labels 
        
        We hand the regionid over to the mapeditor module to select a 
        new active region
        
        Additionally, we mark the active region widget (changing base color) and reseting the previous one

        @type    event:    object
        @param    event:    pychan mouse event
        @type    widget:    object
        @param    widget:    the pychan widget where the event occurs, transports the region id in it's name
        @type    regionid: string
        @param    regionid: the region id
        """
        
        if not widget and not regionid:
            print "No region ID or widget passed to RegionTool.selectRegion"
            return
        
        if widget is not None:
            regionid = widget.name[len(RegionTool.LABEL_NAME_PREFIX):]    
        
        self.selected_region = regionid
        self.update()
        
    def resetSelection(self):
        """ Deselects selected region """
        self.selected_region = None
        self.update()        
        
    def removeSelectedRegion(self):
        """ Deletes the selected region """
        if self.regions.has_key(self.selected_region):
            del self.regions[self.selected_region]
        self.resetSelection()

    def toggle(self):
        """    Toggles the regiontool visible / invisible and sets
            dock status 
        """
        if self.container.isVisible() or self.container.isDocked():
            self.container.setDocked(False)
            self.container.hide()

            self._action_show.setChecked(False)
        else:
            self.container.show()
            self._action_show.setChecked(True)
            self._adjustPosition()
            
    def create(self):
        """ Create the basic gui container """
        self.container =  pychan.loadXML('gui/regiontool.xml')
        self.wrapper = self.container.findChild(name="regions_wrapper")
        self.remove_region_button = self.container.findChild(name="remove_region_button")
        self.create_region_button = self.container.findChild(name="add_region_button")
        self.edit_region_button = self.container.findChild(name="edit_region_button")
        
        self.remove_region_button.capture(self.removeSelectedRegion)
        self.remove_region_button.capture(cbwa(self._editor.getStatusBar().showTooltip, self.remove_region_button.helptext), 'mouseEntered')
        self.remove_region_button.capture(self._editor.getStatusBar().hideTooltip, 'mouseExited')
        
        self.create_region_button.capture(self.showRegionWizard)
        self.create_region_button.capture(cbwa(self._editor.getStatusBar().showTooltip, self.create_region_button.helptext), 'mouseEntered')
        self.create_region_button.capture(self._editor.getStatusBar().hideTooltip, 'mouseExited')
        
        self.edit_region_button.capture(self.showEditDialog)
        self.edit_region_button.capture(cbwa(self._editor.getStatusBar().showTooltip, self.edit_region_button.helptext), 'mouseEntered')
        self.edit_region_button.capture(self._editor.getStatusBar().hideTooltip, 'mouseExited')
        
        self.select_layer_drop_down = self.container.findChild(name="layer_select_drop_down")
        self.select_layer_drop_down.capture(self.update_region_layer)
        
        self.onNewMap(None)
        
        # overwrite Panel.afterUndock
        self.container.afterUndock = self.on_undock
        self.container.afterDock = self.on_dock
        
    def on_dock(self):
        """ callback for dock event of B{Panel}    widget """
        side = self.container.dockarea.side
        if not side: return

        module = self.default_settings['module']
        self.eds.set(module, 'dockarea', side)
        self.eds.set(module, 'docked', True)
    
    def on_undock(self):
        """ callback for undock event of B{Panel} widget """
        self.container.hide()
        self.toggle()

        module = self.default_settings['module']
        self.eds.set(module, 'dockarea', '')
        self.eds.set(module, 'docked', False)                

    def _adjustPosition(self):
        """    Adjusts the position of the container - we don't want to
        let the window appear at the center of the screen.
        (new default position: left, beneath the tools window)
        """
        self.container.position = (50, 200)
    
    def _regionEdited(self, old_region, region):
        del self.regions[old_region]
        self._regionCreated(region)
    
    def _regionCreated(self, region):
        self.regions[region.name] = region
        self.update()
        
    def save(self, mapview):
        """Save the regions to a file"""
        filename = mapview.getMap().getFilename()
        filename = "%s_regions.yaml" % os.path.splitext(filename)[0]
        regions_file = file(filename, "w")
        yaml.dump(self.regions, regions_file)      