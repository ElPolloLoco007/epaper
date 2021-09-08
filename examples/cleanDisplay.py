#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests
import json
import arrow
import python_weather
import asyncio

logging.basicConfig(level=logging.DEBUG)

epd = epd7in5_V2.EPD()
logging.info("init and Clear")
epd.init()
epd.Clear()
