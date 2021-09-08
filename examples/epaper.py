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
import configparser as cp
config = cp.ConfigParser()
config.read('/home/pi/epaper/examples/config.ini')

logging.basicConfig(level=logging.DEBUG)

while True:
    try:
        logging.info("F1 Demo")
        epd = epd7in5_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
        font14 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)
        font20 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)

        # Drawing on the Horizontal image
        logging.info("1.Drawing on the Horizontal image...")
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        y=70

        url = "https://api-formula-1.p.rapidapi.com/rankings/drivers"
        querystring = {"season":"2021"}
        headers = {
            'x-rapidapi-host': "api-formula-1.p.rapidapi.com",
            'x-rapidapi-key': config['RAPID']['key']
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
    
        # SECTION 1
        draw.text((10,30),"STANDINGS", font=font24, fill=0)
        driver_dict = json.loads(response.text)
        for i in range(len(driver_dict['response'])):
            ws = ".  " if driver_dict['response'][i]['position'] < 10 else ". "
            x = str(driver_dict['response'][i]['position']) + \
                ws+driver_dict['response'][i]['driver']['name']
            draw.text((10, y), x, font=font24, fill=0)
            p = str(driver_dict['response'][i]['points'])
            draw.text((260, y), p, font=font24, fill=0)
            y = y+20

        draw.line((0, 60, epd.width, 60), fill = 0,width=5)
        draw.line((310,60,310,epd.height), fill = 0,width=7)

        # SECTION 2
        url = "https://api-formula-1.p.rapidapi.com/races"
        querystring = {"type":"race","season":"2021","last":"1"}
        response = requests.request("GET", url, headers=headers, params=querystring)

        race_dict = json.loads(response.text)
        id=race_dict['response'][0]['id']
        lracename=race_dict['response'][0]['competition']['name']
        lcircuit=race_dict['response'][0]['circuit']['name']

        draw.text((320,2),lracename,font=font16, fill=0)
        draw.text((320,17),lcircuit,font=font14, fill=0)
        draw.text((320,30),"LAST RACE", font=font24, fill=0)

        url = "https://api-formula-1.p.rapidapi.com/rankings/races"
        querystring = {"race":str(id)}
        response = requests.request("GET", url, headers=headers, params=querystring)
    
        race_dict = json.loads(response.text)

        y=70
        for i in range(len(race_dict['response'])):
            ws = ".  " if driver_dict['response'][i]['position'] < 10 else ". "
            x=str(race_dict['response'][i]['position'])+ws+race_dict['response'][i]['driver']['name']
            draw.text((320,y),x,font=font24, fill=0)
            y=y+20

        draw.line((570,60,570,epd.height), fill = 0,width=7)

        # SECTION 3
        url = "https://api-formula-1.p.rapidapi.com/races"
        querystring = {"season": "2021", "next": "1"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        racetrack_dict = json.loads(response.text)
        name = racetrack_dict['response'][0]['competition']['name']
        country = racetrack_dict['response'][0]['competition']['location']['country']
        city = racetrack_dict['response'][0]['competition']['location']['city']
        cname = racetrack_dict['response'][0]['circuit']['name']
        urlimg = racetrack_dict['response'][0]['circuit']['image']
        type = racetrack_dict['response'][0]['type']
        distance = racetrack_dict['response'][0]['distance']
        total = racetrack_dict['response'][0]['laps']['total']
        date = racetrack_dict['response'][0]['date']
        status = racetrack_dict['response'][0]['status']

        utc = arrow.get(date)
        local = utc.to('local')
        ldate = local.format('DD-MM-YYYY HH:mm')
        time.sleep(2)
        draw.text((580,5),type, font=font20, fill=0)
        draw.text((580,30),"NEXT", font=font24, fill=0)
        draw.text((650,34),ldate, font=font16, fill=0)

        draw.text((580,60),name, font=font20, fill=0)
        draw.text((580,100),country, font=font20, fill=0)
        draw.text((580,118),city, font=font20, fill=0)

        bmp = Image.open(requests.get(urlimg, stream=True).raw)
        img = bmp.resize((210,160))
        Himage.paste(img, (577,295))
        draw.text((580,80),cname, font=font16, fill=0)
        draw.text((580,140),"Dist: "+str(distance), font=font24, fill=0)
        draw.text((580,170),"Laps: "+str(total), font=font24, fill=0)
        draw.text((580,200),"Status: "+str(status), font=font24, fill=0)
    
        async def getweather(draw,city):
    
            client = python_weather.Client(format=python_weather.METRIC)
            weather = await client.find(city)
            draw.text((580,230),"Weather:", font=font24, fill=0)

            draw.text((580,260),weather.current.sky_text+" "+str(weather.current.temperature)+"C"+ " "+str(weather.current.wind_speed)+"m/s", font=font20, fill=0)

            await client.close()


        loop = asyncio.get_event_loop()
        loop.run_until_complete(getweather(draw,city))


        # END
        epd.display(epd.getbuffer(Himage))
        logging.info("Goto Sleep...")
        epd.sleep()
        time.sleep(10800)
    
    except IOError as e:
        logging.info(e)
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()
