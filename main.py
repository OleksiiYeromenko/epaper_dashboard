#!/usr/bin/python
# -*- coding:utf-8 -*-


# Didplay Rapberry Pi system information and utilization on e-ink display 176*264.

import sys
import os


libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

import time
import subprocess
from gpiozero import CPUTemperature
import psutil
           
logging.basicConfig(level=logging.INFO) #DEBUG
cpu = CPUTemperature()

# Set fonts
font24 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 18)
font35 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 35)





   
def img_to_display(img_name):
    Himage = Image.open(os.path.join(picdir, img_name))
    #resize image
    Himage = Himage.resize((epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH))
    Himage.show()
    epd.display(epd.getbuffer(Himage))
    time.sleep(3)

def get_font(font_size=18, font_name='Font.ttc'):
    return ImageFont.truetype(os.path.join(libdir, font_name), font_size)

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode("utf-8").rstrip()


def main():
    
    while True:
        # Initialize and clear display
        logging.info("logging.infoing to screen:")
        logging.info("\tInitialisation and clearing screen... ")
        tic = time.perf_counter()
        epd = epd2in7.EPD() # get the display
        epd.init()           # initialize the display
        logging.info("Clear...")    # logging.infos to console, not the display, for debugging
        epd.Clear(0xFF)      # clear the display
        toc = time.perf_counter()
        logging.info(f"took {toc - tic:0.4f} seconds")

        # Get the time
        timestamp = datetime.now().strftime("%d%b%Y,%H:%M")
        # Get the hostname (eg. raspberrypi) 
        device_name = run_cmd("hostname")
        device_ip = run_cmd('hostname -I')
        # Get the CPU temperature
        cpu_temp = round(cpu.temperature,1)
        # Get the GPU temperature
        gpu_temp = run_cmd("vcgencmd measure_temp | grep -o -E '[0-9]+.[0-9]'").rstrip()
        # Get CPU usage
        cpu_usage_pct = psutil.cpu_percent(interval=1)
        cpu_frequency = int(psutil.cpu_freq().current)
        # Get RAM usage
        ram_usage = int((psutil.virtual_memory().total - psutil.virtual_memory().available)/ 1024 / 1024)
        ram_total = int((psutil.virtual_memory().total)/ 1024 / 1024)
        ram_usage_pct = psutil.virtual_memory().percent
        # Get swap 
        swap_used = round(psutil.swap_memory().used/1024/1024,2)
        swap_total = round(psutil.swap_memory().total/1024/1024,2)
        # Get disk usage
        disk_total = round(psutil.disk_usage('/').total / 2**30, 2)# GiB.
        disk_used = round(psutil.disk_usage('/').used / 2**30, 2)
        disk_percent_used = round(psutil.disk_usage('/').percent,2)
         
    #     logging.info(f"host: {device_name}")
    #     logging.info(f"{timestamp}")
    #     logging.info(f"CPU Temperature: {cpu_temp}°C")
    #     logging.info(f"GPU Temperature: {gpu_temp}°C")
    #     logging.info(f'System CPU load: {cpu_usage_pct}%') # Calling psutil.cpu_precent() for 4 seconds 
    #     logging.info(f'RAM usage: {ram_usage}MB/{round(ram_total/1024, 2)}GB, {ram_usage_pct}%') # current RAM usage in MB
    #     logging.info(f'Swap usage: {swap_used}/{swap_total}MB, {round(100*swap_used/swap_total,2)}%')
    #     logging.info(f"Disk usage: {disk_used}/{disk_total}GB, {disk_percent_used}%")

        epd = epd2in7.EPD() # get the display
        Himage = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage) # Create draw object and pass in the image layer we want to work with
        # prepare image to draw
        starting_x = 1
        starting_y = 35
        shift_y = 21
        draw.text((starting_x, 1), f"{device_ip}", font = get_font(18), fill = 0)   # draw the text to the display. First argument is starting location of the text in pixels 
        draw.text((starting_x+115, 1), f"{timestamp}", font = get_font(19), fill = 0)   # draw the text to the display. First argument is starting location of the text in pixels 
        draw.text((starting_x, starting_y), f"CPU Temperature: {cpu_temp}°C", font = get_font(17), fill = 0)   
        draw.text((starting_x, starting_y+shift_y), f"GPU Temperature: {gpu_temp}°C", font = get_font(17), fill = 0)   
        draw.text((starting_x, starting_y+2*shift_y), f'System CPU load: {cpu_usage_pct}%', font = get_font(17), fill = 0)   
        draw.text((starting_x, starting_y+3*shift_y), f'RAM usage: {ram_usage}MB/{round(ram_total/1024, 2)}GB, {ram_usage_pct}%', font = get_font(17), fill = 0)   
        draw.text((starting_x, starting_y+4*shift_y), f'Swap usage: {swap_used}/{swap_total}MB, {round(100*swap_used/swap_total,2)}%', font = get_font(17), fill = 0)   
        draw.text((starting_x, starting_y+5*shift_y), f"Disk usage: {disk_used}/{disk_total}GB, {disk_percent_used}%", font = get_font(17), fill = 0)   
        # Print on display
        logging.info("\tWriting to screen... ")
        tic = time.perf_counter()
        epd.display(epd.getbuffer(Himage))
        toc = time.perf_counter()
        logging.info(f"took {toc - tic:0.4f} seconds")
        
        epd.sleep() # Power off display
        time.sleep(5*60)



    
    
if __name__ == "__main__":
    main()
