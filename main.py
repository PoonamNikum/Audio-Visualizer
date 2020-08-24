import pygame
import numpy as np
from pygame import mixer
from AudioAnalyzer import *
import random
import colorsys



def rnd_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    return [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
#rnd_result = rnd_color()
filename = 'AudioFile.wav'
pygame.init()
infoObject = pygame.display.Info()
screen_w = int(infoObject.current_w/2.2)
screen_h = int(infoObject.current_w/2.2)
screen = pygame.display.set_mode((screen_w,screen_h))  #screen size 
pygame.display.set_caption('Audio Visualizer')  #Game name caption
#mixer.music.load('AudioFile.wav')  #background sound of game
#mixer.music.play(-1) 

analyzer = AudioAnalyzer()
analyzer.load(filename)

red = (213, 50, 80)

t = pygame.time.get_ticks()
getTicksLastFrame = t

timeCount = 0

avg_bass = 0
bass_trigger = -30
bass_trigger_started = 0

min_decibel = -80
max_decibel = 80

circle_color = (40, 40, 40)
polygon_default_color = [255, 255, 255]
color = [0,255,255]
polygon_bass_color = polygon_default_color.copy()
polygon_color_vel = [0, 0, 0]

poly = []
poly_color = polygon_default_color.copy()


min_radius = 100
max_radius = 150
radius = min_radius
radius_vel = 0

circleX = int(screen_w / 2)
circleY = int(screen_h/2)

bass = {"start": 50, "stop": 100, "count": 12}
heavy_area = {"start": 120, "stop": 250, "count": 40}
low_mids = {"start": 251, "stop": 2000, "count": 50}
high_mids = {"start": 2001, "stop": 6000, "count": 20}

freq_groups = [bass, heavy_area, low_mids, high_mids]

bars = []

tmp_bars = []

length = 0
for group in freq_groups:

    g = []

    s = group["stop"] - group["start"]
    #print(s)
    count = group["count"]
    #print('count ', count)
    reminder = s%count
    #print('reminder ', reminder)
    step = int(s/count)
    rng = group["start"]

    for i in range(count):

        arr = None

        if reminder > 0:
            reminder -= 1
            arr = np.arange(start=rng, stop=rng + step + 2)
            rng += step + 3
        else:
            arr = np.arange(start=rng, stop=rng + step + 1)
            rng += step + 2
        #print('rng ', rng)
        g.append(arr)

        length += 1

    tmp_bars.append(g)
#print(tmp_bars)
#print('length ',length)
angle_dt = 360/length
ang = 0
#print('angle_dt ',angle_dt)
for g in tmp_bars:
    gr = []
    for c in g:
        gr.append(
            RotatedAverageAudioBar(circleX+radius*math.cos(math.radians(ang - 90)), circleY+radius*math.sin(math.radians(ang - 90)), c, (255, 0, 255), angle=ang, width=8, max_height=370))
        ang += angle_dt

    bars.append(gr)

pygame.mixer.music.load(filename)
pygame.mixer.music.play(0)

running = True
while running:
    avg_bass = 0
    poly = []

    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    timeCount += deltaTime

    screen.fill((0,100,100))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    for b1 in bars:
        for b in b1:
            b.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer)
    #print('bars[0] ', bars[0])
    for b in bars[0]:
        avg_bass += b.avg
    #print('avg_bass ', avg_bass )
    #print('len(bars[0] ', len(bars[0]) )
    avg_bass /= len(bars[0])
    #print('avg_bass1: ', avg_bass )
    #print('bass_trigger: ', bass_trigger )
    #print('bass_trigger_started: ', bass_trigger_started )
    #print('rnd_result: ', rnd_result )
    if avg_bass > bass_trigger:
        if bass_trigger_started == 0:
            bass_trigger_started = pygame.time.get_ticks()
        if (pygame.time.get_ticks() - bass_trigger_started)/1000.0 > 2:
            polygon_bass_color = rnd_color()   #change rnd_Color
            bass_trigger_started = 0
        if polygon_bass_color is None:
            polygon_bass_color = rnd_color()    #change rnd_Color
        newr = min_radius + int(avg_bass * ((max_radius - min_radius) / (max_decibel - min_decibel)) + (max_radius - min_radius))
        radius_vel = (newr - radius) / 0.15
        #print(' polygon_bass_color: ',polygon_bass_color)
        #for x in range(len(poly_color)):
            #print('polygon_bass_color[x]: ', polygon_bass_color[x])
            #print('poly_color[x]: ', poly_color[x])
        polygon_color_vel = [(polygon_bass_color[x] - poly_color[x])/0.15 for x in range(len(poly_color))]

    elif radius > min_radius:
        bass_trigger_started = 0
        polygon_bass_color = None
        radius_vel = (min_radius - radius) / 0.15
        polygon_color_vel = [(polygon_default_color[x] - poly_color[x])/0.15 for x in range(len(poly_color))]

    else:
        bass_trigger_started = 0
        poly_color = polygon_default_color.copy()
        polygon_bass_color = None
        polygon_color_vel = [0, 0, 0]

        radius_vel = 0
        radius = min_radius

    radius += radius_vel * deltaTime
    #print('deltaTime ', deltaTime)
    #print('polygon_color_vel ', polygon_color_vel)
    #print('polygon_color ', poly_color)
    for x in range(len(polygon_color_vel)):
        value = polygon_color_vel[x]*deltaTime + poly_color[x]
        poly_color[x] = value

    for b1 in bars:
        for b in b1:
            b.x, b.y = circleX+radius*math.cos(math.radians(b.angle - 90)), circleY+radius*math.sin(math.radians(b.angle - 90))
            b.update_rect()

            poly.append(b.rect.points[3])
            poly.append(b.rect.points[2])

    pygame.draw.polygon(screen, poly_color, poly)

    pygame.draw.circle(screen, circle_color, (circleX, circleY), int(radius))
    #screen.fill((0,0,0))
    pygame.display.flip()
    #pyga
