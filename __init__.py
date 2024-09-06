#!/usr/bin/env python3
# authors: Gabriel Auger
# name: xfreerdp wrapper
# licenses: MIT 
__version__= "1.0.0"

from .dev.wrdp import wrdp, MouseCoords, Location
from .gpkgs.prompt import prompt_multiple
from .gpkgs.guitools import Monitors, Monitor

from .gpkgs.etconf import Etconf
from .gpkgs.nargs import Nargs
from .gpkgs import message as msg
