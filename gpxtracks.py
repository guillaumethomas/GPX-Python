# by Cyril Dubus
# Mod by G. THOMAS
# Last version : 2017-09-11

from numpy import pi as pi, sin as sin, cos as cos
import matplotlib.pyplot as plt
from prettytable import PrettyTable as PT
import os
from geopy.geocoders import Nominatim as Nomi
import xml.etree.ElementTree as ET # pour parser des fichiers xml, comme le sont les fichiers gpx
import datetime

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
        #some have milisecond some do not
        try:
            a = datetime.datetime.strptime(elem[1].text, "%Y-%m-%dT%H:%M:%S.%fZ") # construct the datetime list from springs formated as 2017-09-08T18:01:05Z
        except ValueError:
            a = datetime.datetime.strptime(elem[1].text,"%Y-%m-%dT%H:%M:%SZ")  # construct the datetime list from springs formated as 2017-09-08T18:01:05Z
        date_times.append(a)

    return [latitudes,longitudes,elevations,date_times]
    
def distime(lat_lon_ele_datetime): # the argument is a list of four lists : latitudes, longitudes, elevations, datetimes. Return a list of 3 lists : the distance, the projected distance (in an horizontal plane) and the elapsed time form the beginning of the track. Considering that the distance betwenn two consecutive trackpoints is generally extremely small compared to earth radius, the earth is considered to be flat between this two points.

    lat = [elem*pi/180 for elem in lat_lon_ele_datetime[0]] # convert in radian
    lon = [elem*pi/180 for elem in lat_lon_ele_datetime[1]] # convert in radian

    ele = lat_lon_ele_datetime[2] # list of elevations (meter)

    date_time = lat_lon_ele_datetime[3] # list of datetimes

    times = [0] #initialize elapsed time
    dist = [0] # initialise distance
    projdist = [0] #initialize projected distancece

    R = 6371000 # "mean" earth radius

    for i in range(1,len(lat)):
        timedif=date_time[i]-date_time[0] # timedif is a datetime.timedelta, which is converted in a duration in seconds in the next line
        times.append(timedif.days*24*3600+timedif.seconds)
        a = projdist[i-1]
        a += R*((sin(lat[i])-sin(lat[i-1]))**2+(cos(lat[i])*cos(lon[i])-cos(lat[i-1])*cos(lon[i-1]))**2+(cos(lat[i])*sin(lon[i])-cos(lat[i-1])*sin(lon[i-1]))**2)**.5
        projdist.append(a)
        a = dist[i-1]
        a += (((R+ele[i])*sin(lat[i])-(R+ele[i-1])*sin(lat[i-1]))**2+((R+ele[i])*cos(lat[i])*cos(lon[i])-(R+ele[i-1])*cos(lat[i-1])*cos(lon[i-1]))**2+((R+ele[i])*cos(lat[i])*sin(lon[i])-(R+ele[i-1])*cos(lat[i-1])*sin(lon[i-1]))**2)**.5
        dist.append(a)


    return [dist,projdist,times]

def address(coord):
    location = Nomi().reverse(coord)
    return location.address

def average_per_hour(dpt, interval = 3600):
    if dpt[2][-1] < interval:
        print('Activity is too short for an avg per hour GO ride more !')
        return [],[]
    else:
        data_point=[[dpt[0][0],dpt[2][0]]]
        hour_mult = 1
        for time in dpt[2]:
            if time >= (hour_mult * interval):
                b = dpt[2].index(time)
                data_point.append([dpt[0][b],time])
                hour_mult += 1

        data_point.append([dpt[0][-1],dpt[2][-1]])

#        data_point.reverse()

        avg_speed = list()
        for i in range(len(data_point)-1):
            avg_speed_elem = (data_point[i][0] - data_point[i+1][0]) / (data_point[i][1] - data_point[i+1][1])
            avg_speed_elem *= 3.6
            avg_speed_elem = round(avg_speed_elem,2)
            avg_speed.append(avg_speed_elem)
        return data_point, avg_speed, interval

def print_avg(average_speed, interval):
    Time_Heading = str(interval / 3600) + ' Hours Segment'
    Table = PT([Time_Heading, 'Avg (km/h)'])
    for avg in average_speed:
        Table.add_row([str(average_speed.index(avg)+1),str(round(avg,2))])
    return Table

def main():

    for file in os.listdir():
        if file.endswith(".gpx"):
            dpt = distime(gpxread(file))
            plt.plot(dpt[2],dpt[0]) # distance (m) vs time (s)
            plt.plot(dpt[2],dpt[1]) # projected distance (m) vs time (s)
            print(file)
            print('total dist is ', str(round( dpt[0][-1] / 1000,2)), ' km' )
            avg_speed = round((dpt[0][-1] * 3.6) / (dpt[2][-1] - dpt[2][0]),2)
            print('avg speed is', avg_speed, ' km/h')
            plt.title(file)
            plt.show()
            data_point, average_speed, interval = average_per_hour(dpt, 1800)
            if average_speed != []:
                print(print_avg(average_speed, interval))

if __name__ == "__main__":
    main()
