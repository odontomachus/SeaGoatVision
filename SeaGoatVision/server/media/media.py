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

from thread_media import ThreadMedia
import numpy as np
from SeaGoatVision.commons import log

logger = log.get_logger(__name__)


class Media(object):

    def __init__(self):
        self.sleep_time = 1 / 30.0
        self.lst_observer = []
        self.thread = None
        self.media_name = None
        self.active_loop = True
        self.is_client_manager = False
        self.publisher = None

    def set_is_client_manager(self, is_client_manager):
        self.is_client_manager = is_client_manager

    def is_media_streaming(self):
        # complete it into media_streaming and media_video
        pass

    def is_media_video(self):
        # complete it into media_streaming and media_video
        pass

    def get_type_media(self):
        # complete it into media_streaming and media_video
        # type is Video or Streaming
        pass

    def get_dct_media_param(self):
        return {param.get_name(): param for param in self.get_properties_param()}

    def get_properties_param(self):
        return []

    def update_property_param(self, param_name, value):
        return False

    def get_name(self):
        return self.media_name

    def __iter__(self):
        return self

    def get_total_frames(self):
        return -1

    def get_info(self):
        fps = int(1 / self.sleep_time) if self.thread else -1
        return {"fps": fps, "nb_frame": self.get_total_frames()}

    def serialize(self):
        pass

    def deserialize(self, data):
        return True

    def get_real_fps(self):
        if self.thread:
            return self.thread.get_fps()
        return -1

    def open(self):
        # IMPORTANT, if inherit, call this at the end
        # the thread need to be start when device is ready
        logger.info("Open media %s" % self.get_name())
        if self.is_client_manager:
            return True
        if self.thread:
            return False
        cb_publisher = self._get_cb_publisher()
        self.thread = ThreadMedia(self, cb_publisher)
        self.thread.start()
        return True

    def next(self):
        # edit me in child
        pass

    def reset(self):
        # restore the media
        pass

    def close(self):
        logger.info("Close media %s" % self.get_name())
        self._remove_cb_publisher()
        if self.is_client_manager:
            return True
        if not self.thread:
            return False
        self.thread.stop()
        self.thread = None
        return True

    def initialize(self):
        pass

    def reload(self):
        if not self.thread:
            return True
        status = self.close()
        if not status:
            return False
        # TODO force re-init filterchain
        self.initialize()
        status = self.open()
        return status

    def change_sleep_time(self, sleep_time):
        self.sleep_time = sleep_time

    def add_observer(self, observer):
        start_media = False
        if not self.lst_observer:
            start_media = True
        self.lst_observer.append(observer)
        if start_media:
            self.open()

    def remove_observer(self, observer):
        if observer in self.lst_observer:
            self.lst_observer.remove(observer)
        else:
            logger.warning(
                "Observer missing into media %s" %
                (self.get_name()))
        if not self.lst_observer:
            self.close()

    def notify_observer(self, image):
        # be sure the image is different for all observer
        for observer in self.lst_observer:
            observer(np.copy(image))

    def set_loop_enable(self, enable):
        self.active_loop = enable

    def set_publisher(self, publisher):
        self.publisher = publisher

    def get_publisher(self):
        return self.publisher

    def _get_cb_publisher(self):
        if not self.publisher:
            return None
        key = self.get_name()
        self.publisher.register(key)
        return self.publisher.get_callback_publish(key)

    def _remove_cb_publisher(self):
        if not self.publisher:
            return None
        key = self.get_name()
        self.publisher.deregister(key)
