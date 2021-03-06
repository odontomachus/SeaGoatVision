#! /usr/bin/env python

#    Copyright (C) 2012  Octets - octets.etsmtl.ca
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
"""
Parameter is used by filter and client. This is public variable with specific
type of filter.
Filter must not modify Param.
Different type :
 - INT : integer. Can have min or max value. Can use table of specific value.
 - FLOAT : float. Same of INT, but use float.
 - BOOL : boolean. Only True or False.
 - STRING : string.

TIPS :
 - You want only EVEN number for your gaussian blur?
    lst_gauss_value = [i for i in range(100) if not(i % 2)]
    kern_gauss_blur = Param("kern_gauss_blur", 4, lst_value=lst_gauss_value)
 - In this example, we can't access to -1 because of min.
    p = Param("f", 2, min_v=1, max_v=19, lst_value=[-1,2,4,6,10])
 - We can use a threshold value. In this situation, we have two value.
  The value is always the low value and the threshold_hight is the hight value.
    p = Param("f", 2, min_v=1, max_v=8, thres_h=5)
"""
import numpy as np
from SeaGoatVision.commons import log

logger = log.get_logger(__name__)


class Param(object):

    """Param autodetect basic type
    force_type need to be a <type>
    If you want specific type, cast it to basic type and use force_type
    Param manager type : bool, str, int and float
    """

    def __init__(self, name, value, min_v=None, max_v=None, lst_value=None,
                 force_type=None, thres_h=None, serialize=None):
        # contant float
        self.delta_float = 0.0001
        # Exception, can serialize
        self.lst_notify = []
        self.lst_notify_reset = []
        self.name = name
        self.lst_value = lst_value
        self.min_v = None
        self.max_v = None
        self.value = None
        self.default_value = None
        self.type_t = None
        self.thres_h = None
        self.force_type = None
        self.last_serialize_value = None

        if serialize:
            status = self.deserialize(serialize)
            if not status:
                raise Exception(
                    "Wrong deserialize parameter, can't know the name.")
            logger.debug(
                "Param %s deserialization complete, value %s" %
                (self.name, self.value))
            return

        if not isinstance(name, str) and not isinstance(name, unicode):
            raise Exception("Name must be string value.")

        self._init_param(value, min_v, max_v, lst_value, force_type, thres_h)

    def _init_param(self, value, min_v, max_v, lst_value, force_type, thres_h):
        self._valid_param(value, min_v, max_v, lst_value, thres_h)
        self.set(value)
        self.default_value = self.last_serialize_value = self.value
        if force_type:
            self.force_type = force_type
        else:
            self.force_type = self.type_t

    def _valid_param(self, value, min_v, max_v, lst_value, thres_h):
        type_t = type(value)
        if not(type_t is int or type_t is bool or type_t is float or type_t is str or type_t is np.ndarray or type_t is long or type_t is unicode):
            raise Exception("Param don't manage type %s" % type_t)
        if type_t is unicode:
            type_t = str
        if type_t is long:
            type_t = type_t = int
            value = int(value)
            if min_v is not None:
                min_v = int(min_v)
            if max_v is not None:
                max_v = int(max_v)
        if type_t is float or type_t is int or type_t is long:
            # check min and max
            if min_v is not None:
                type_min = type(min_v)
                if not (type_min is float or type_min is int or type_min is long):
                    raise Exception(
                        "min_v must be float or int, type is %s." %
                        type_min)
            if max_v is not None:
                type_max = type(max_v)
                if not(type_max is float or type_max is int or type_max is long):
                    raise Exception(
                        "max_v must be float or int, type is %s." %
                        type(max_v))
            if lst_value is not None and \
                    not(isinstance(lst_value, tuple) or isinstance(lst_value, list)):
                raise Exception(
                    "lst_value must be list or tuple, type is %s." %
                    type(lst_value))
            if type_t is float:
                min_v = None if min_v is None else float(min_v)
                max_v = None if max_v is None else float(max_v)
                lst_value = None if lst_value is None else \
                    [float(value) for value in lst_value]
            if type_t is int:
                min_v = None if min_v is None else int(min_v)
                max_v = None if max_v is None else int(max_v)
                lst_value = None if lst_value is None else \
                    [int(value) for value in lst_value]
        self.min_v = min_v
        self.max_v = max_v
        self.lst_value = lst_value
        self.type_t = type_t
        self.thres_h = thres_h

    def serialize(self):
        self.last_serialize_value = self.value
        # Force_type is not supported
        return {"name": self.name,
                "value": self.value,
                "min_v": self.min_v,
                "max_v": self.max_v,
                "lst_value": self.lst_value,
                #"force_type":self.force_type,
                "thres_h": self.thres_h}

    def deserialize(self, value):
        if not isinstance(value, dict):
            return False
        name = value.get("name", None)
        if not name:
            return False
        self.name = name
        self._init_param(value.get("value", None),
                         value.get("min_v", None),
                         value.get("max_v", None),
                         value.get("lst_value", None),
                         value.get("force_type", None),
                         value.get("thres_h", None))
        return True

    def reset(self):
        if self.value == self.last_serialize_value:
            return
        self.value = self.last_serialize_value
        for notify in self.lst_notify_reset:
            notify(self.get_name(), self.value)

    def set_as_default(self):
        if self.value == self.default_value:
            return
        self.value = self.default_value
        for notify in self.lst_notify_reset:
            notify(self.get_name(), self.value)

    def merge(self, param):
        self.name = param.name
        self.value = param.value
        self.min_v = param.min_v
        self.max_v = param.max_v
        self.lst_value = param.lst_value
        self.thres_h = param.thres_h

    def get_name(self):
        return self.name

    def get_min(self):
        return self.min_v

    def get_max(self):
        return self.max_v

    def get_list_value(self):
        if not self.lst_value:
            return None
        return self.lst_value

    def add_notify(self, callback):
        # notify when set the value
        # pass the value in argument
        if callback in self.lst_notify:
            logger.warning("Already in notify %s" % self.get_name())
            return
        self.lst_notify.append(callback)

    def remove_notify(self, callback):
        if callback not in self.lst_notify:
            logger.warning(
                "The callback wasn't in the list of notify %s" %
                self.get_name())
            return
        self.lst_notify.remove(callback)

    def add_notify_reset(self, callback):
        # notify when set the value
        # pass the value in argument
        if callback in self.lst_notify_reset:
            logger.warning("Already in notify reset %s" % self.get_name())
            return
        self.lst_notify_reset.append(callback)

    def remove_notify_reset(self, callback):
        if callback not in self.lst_notify_reset:
            logger.warning(
                "The callback wasn't in the list of notify reset %s" %
                self.get_name())
            return
        self.lst_notify_reset.remove(callback)

    def get(self):
        # Exception, cannot convert to numpy array
        # this can create bug in your filter if you pass wrong type
        if self.force_type is np.ndarray:
            return self.value
        if self.thres_h is not None:
            return (self.force_type(self.value), self.force_type(self.thres_h))
        return self.force_type(self.value)

    def get_pos_list(self):
        if not self.lst_value:
            return -1
        return self.lst_value.index(self.get())

    def set(self, value, thres_h=None):
        if isinstance(value, unicode):
            value = str(value)
        if self.type_t is bool:
            value = bool(value)

        if self.type_t is int and (isinstance(value, float) or isinstance(value, long)):
            value = int(value)
        if self.type_t is float and isinstance(value, int):
            value = float(value)
        if not isinstance(value, self.type_t):
            raise Exception("value is wrong type. Expected %s and receive %s"
                            % (self.type_t, type(value)))
        if self.type_t is int or self.type_t is float:
            if self.min_v is not None and value < self.min_v - self.delta_float:
                raise Exception("Value %s is lower then min %s" %
                               (value, self.min_v))
            if self.max_v is not None and value > self.max_v + self.delta_float:
                raise Exception("Value %s is upper then max %s" %
                               (value, self.max_v))
            if self.lst_value is not None and value not in self.lst_value:
                raise Exception("value %s is not in lst of value" % (value))
        if self.thres_h is not None:
            if thres_h is None:
                if value > self.thres_h:
                    msg = "Threshold bot %s is upper then threshold top %s." \
                        % (value, self.thres_h)
                    raise Exception(msg)
            else:
                if self.type_t is int and isinstance(thres_h, float):
                    thres_h = int(thres_h)
                if self.type_t is float and isinstance(thres_h, int):
                    thres_h = float(thres_h)
                if not isinstance(thres_h, self.type_t):
                    msg = "value is wrong type. Expected %s and receive %s" \
                        % (self.type_t, type(thres_h))
                    raise Exception(msg)
                elif value > thres_h:
                    msg = "Threshold low %s is upper then threshold hight %s." \
                        % (value, thres_h)
                    raise Exception(msg)
                if thres_h > self.max_v:
                    raise Exception("Threshold hight %s is upper then max %s."
                                    % (thres_h, self.max_v))
                self.thres_h = thres_h
        self.value = value
        # send the value on all notify callback
        for notify in self.lst_notify:
            notify(value)

    def get_type(self):
        return self.force_type
