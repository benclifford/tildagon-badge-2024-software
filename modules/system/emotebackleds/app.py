# BUGS: overrides what hexpansion driver has set to and
# doesn't restore them.

import asyncio
import settings
import time
from tildagonos import tildagonos

from machine import PWM

from app import App
from app_components import clear_background
from events.input import BUTTON_TYPES, ButtonDownEvent
from system.hexpansion.config import HexpansionConfig
from system.eventbus import eventbus

from events.emote import EmotePositiveEvent, EmoteNegativeEvent
from system.hexpansion.events import HexpansionRemovalEvent, HexpansionInsertionEvent


class EmoteBackLEDs(App):
  def __init__(self):
    eventbus.on_async(EmotePositiveEvent, self._positive_event, self)
    eventbus.on_async(EmoteNegativeEvent, self._negative_event, self)
    eventbus.on_async(HexpansionInsertionEvent, self._insertion_event, self)
    eventbus.on_async(HexpansionRemovalEvent, self._removal_event, self)
    self.active_back_leds = [False] * 6
    self.lock = asyncio.Lock()

  async def _positive_event(self, event):
    print("positive event")
    await self.lock.acquire()
    for lednum in range(13,19):
      tildagonos.leds[lednum] = (0,255,0)
    tildagonos.leds.write()
    await asyncio.sleep(0.5)
    for lednum in range(13,19):
      tildagonos.leds[lednum] = (0,0,0)
    tildagonos.leds.write()
    self.lock.release()
 
  async def _negative_event(self, event):
    print("negative event")
    await self.lock.acquire()
    for lednum in range(13,19):
      tildagonos.leds[lednum] = (255,0,0)
    tildagonos.leds.write()
    await asyncio.sleep(0.5)
    for lednum in range(13,19):
      tildagonos.leds[lednum] = (0,0,0)
    tildagonos.leds.write()
    self.lock.release()

  async def _insertion_event(self, event):
    print("insertion event")
    self.active_back_leds[event.port-1] = True
    print(self.active_back_leds)

  async def _removal_event(self, event):
    print("removal event")
    self.active_back_leds[event.port-1] = False
    print(self.active_back_leds)

  def background_update(self, delta):
   if not self.lock.locked(): # skip this if some other piece is using the LEDs
    if settings.get("pattern_mirror_hexpansions", False):
    # TODO: manage the case where mirror is turned off (so should use default colour sequence)
      for i in range(0, 6):
        if self.active_back_leds[i]:
          tildagonos.leds[13 + i] = tildagonos.leds[1 + (i * 2)]
        else:
          tildagonos.leds[13 + i] = (0, 0, 0)
        tildagonos.leds.write()
   else:
     # print("skipping because locked")
     pass
