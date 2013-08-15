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

import yaml

from fife import fife
from fife.extensions import pychan
from fife.extensions.pychan import dialogs


class Region(object):
    "Representing a region"

    def __init__(self, name, rect):
        self.name = name
        self.rect = rect

def region_representer(dumper, data):
    # dumper = yaml.Dumper()
    region_data = (data.rect.x, data.rect.y, data.rect.w, data.rect.h)
    return dumper.represent_list(region_data)

yaml.add_representer(Region, region_representer)

class RegionDialog(object):
    """
    The B{RegionDialog} provides a gui dialog for creating and editing regions.
    """
    def __init__(self, engine, regions, callback=None, onCancel=None, region=None):
        self.engine = engine
        self.model = engine.getModel()
        self.regions = regions
        if not region is None and isinstance(region, str):
            region = regions[region]
        self.region = region
        self.callback = callback
        self.onCancel = onCancel
        self._widget = pychan.loadXML('gui/regiondialog.xml')

        if region:
            self._widget.distributeData({
                "regionBox" : unicode(region.name),
                "xPosBox" : unicode(region.rect.x),
                "yPosBox" : unicode(region.rect.y),
				"widthBox" : unicode(region.rect.w),
				"heightBox" : unicode(region.rect.h),
            })

        self._widget.mapEvents({
            'okButton'     : self._finished,
            'cancelButton' : self._cancelled
        })

        self._widget.show()

    def _cancelled(self):
        """ """
        if self.onCancel:
            self.onCancel()
        self._widget.hide()

    def _finished(self):
        """ """
        # Collect and validate data
        regionId = self._widget.collectData('regionBox')
        if regionId == '':
            dialogs.message(message=unicode("Please enter a region id."), caption=unicode("Error"))
            return

        try:
            x_pos = float(self._widget.collectData('xPosBox'))
            y_pos = float(self._widget.collectData('yPosBox'))
            width = float(self._widget.collectData('widthBox'))
            height = float(self._widget.collectData('heightBox'))
            rect = fife.DoubleRect(x_pos, y_pos, width, height)
        except ValueError:
            dialogs.message(message=unicode("Please enter integer or decimal values for scale."), caption=unicode("Error"))
            return

        # Set up region
        region = self.region

        if not self.region:
            if not self.regions.has_key(regionId):
                region = Region(str(regionId), rect)
            else:
                print 'The region ' + str(regionId) + ' already exists!'
                return
        else:
            if region.name == regionId or not self.regions.has_key(regionId):
                region.name = (str(regionId))
                region.rect = rect
            else:
                print 'The region ' + str(regionId) + ' already exists!'
                return

        # Hide dialog and call back
        self._widget.hide()

        if self.callback:
            pychan.tools.applyOnlySuitable(self.callback, region=region)
