#! /usr/bin/env python

#    Copyright (C) 2012  Club Capra - capra.etsmtl.ca
#
#    This file is part of SeaGoatVision.
#    
#    SeaGoatVision is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np

from SeaGoatVision.server.filters.parameter import  Parameter
from SeaGoatVision.server.core.filter import Filter

class Psychedelic(Filter):
    """Acid trip"""
    
    def __init__(self):
        Filter.__init__(self)
        self._images = []
        self.nb_images = Parameter("Nb Images", 1, 99, 10)
        
    def execute(self, image):
        self._images.append(image)
        while len(self._images) >= self.nb_images.get_current_value():
            del self._images[0]
            
        try:
            for img in self._images:
                image = np.add(image, img)
        except:
            pass
        return image
