# by Cyril Dubus
# Last version : 2017-09-11

#from math import *
import numpy as np
#import scipy as sp
#import scipy.integrate as integr
#import matplotlib as mp
import matplotlib.pyplot as plt
#import os
import xml.etree.ElementTree as ET # pour parser des fichiers xml, comme le sont les fichiers gpx
import datetime

gpxfilename = '2017-09-05_chezine_10km.gpx'

def gpxread(FileName): # return the four lists : latitudes, longitudes and elevation are float lists and date_times is a datetime.datetime list
    latitudes = []
    longitudes = []
    elevations = []
    date_times = []
    tree=ET.parse(FileName)
    doc=tree.getroot()
    trkptlist = doc.findall('{http://www.topografix.com/GPX/1/1}trk/{http://www.topografix.com/GPX/1/1}trkseg/{http://www.topografix.com/GPX/1/1}trkpt') # track points list (each point is a xml.etree.ElementTree.Element)
    for elem in trkptlist:
        latitudes.append(float(elem.get('lat')))
        longitudes.append(float(elem.get('lon')))
        elevations.append(float(elem[0].text))
        date_times.append(datetime.datetime.strptime(elem[1].text, "%Y-%m-%dT%H:%M:%SZ")) # construct the datetime list from springs formated as 2017-09-08T18:01:05Z        
    return [latitudes,longitudes,elevations,date_times]
    
def distime(lat_lon_ele_datetime): # the argument is a list of four lists : latitudes, longitudes, elevations, datetimes. Return a list of 3 lists : the distance, the projected distance (in an horizontal plane) and the elapsed time form the beginning of the track. Considering that the distance betwenn two consecutive trackpoints is generally extremely small compared to earth radius, the earth is considered to be flat between this two points.
    lat = lat_lon_ele_datetime[0] # list of latitudes (degree)
    lat = [elem*np.pi/180 for elem in lat] # convert in radian
    lon = lat_lon_ele_datetime[1] # list of longitudes (degree)
    lon = [elem*np.pi/180 for elem in lon] # convert in radian
    ele = lat_lon_ele_datetime[2] # list of elevations (meter)
    date_time = lat_lon_ele_datetime[3] # list of datetimes
    times = [0] #initialize elapsed time
    dist = [0] # initialise distance
    projdist = [0] #initialize projected disatnce
    R = 6371000 # "mean" earth radius
    for i in range(1,len(lat)-1):
        timedif=date_time[i]-date_time[0] # timedif is a datetime.timedelta, which is converted in a duration in seconds in the next line
        times.append(timedif.days*24*3600+timedif.seconds) 
        projdist.append(projdist[i-1] + R*((np.sin(lat[i])-np.sin(lat[i-1]))**2+(np.cos(lat[i])*np.cos(lon[i])-np.cos(lat[i-1])*np.cos(lon[i-1]))**2+(np.cos(lat[i])*np.sin(lon[i])-np.cos(lat[i-1])*np.sin(lon[i-1]))**2)**.5)
        dist.append(dist[i-1] + (((R+ele[i])*np.sin(lat[i])-(R+ele[i-1])*np.sin(lat[i-1]))**2+((R+ele[i])*np.cos(lat[i])*np.cos(lon[i])-(R+ele[i-1])*np.cos(lat[i-1])*np.cos(lon[i-1]))**2+((R+ele[i])*np.cos(lat[i])*np.sin(lon[i])-(R+ele[i-1])*np.cos(lat[i-1])*np.sin(lon[i-1]))**2)**.5)
    return [dist,projdist,times]

dpt = distime(gpxread(gpxfilename))

#dpt = np.asarray(dpt)

plt.plot(dpt[2],dpt[0]) # distance (m) vs time (s)
plt.plot(dpt[2],dpt[1]) # projected distance (m) vs time (s)

plt.show()
    