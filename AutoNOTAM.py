import re # Regular expressions
import math # Additional math functions
import os # Directory information
from tkinter import Tk, filedialog # File selection
import simplekml # .kml file generator
from polycircles import polycircles # .kml file circle generator

kml = simplekml.Kml() # Initialize kml

root = Tk() # Initialize main GUI window
root.withdraw() # Hide GUI window

cwd = os.getcwd() # Get current working directory

root.filename = filedialog.askopenfilename(initialdir=cwd,
                                           title="Select file",
                                           filetypes=(("Text files", "*.txt"),
                                                      ("all files", "*.*"))) # Accept file input from user

root.destroy() # Close GUI window

with open(root.filename, 'r') as file:
    data = file.read().replace('\n', ' ') # Read NOTAM txt
data = str(re.sub("  "," ",data))

#------------------ Define regular expressions
eventtext = re.compile(r"E\).*? \)")
circletext = re.compile(r" E\)(.*?)(AREA CIRCLE WITH RADIUS) ([\d]*[\.][\d]*|[\d]*) (M|NM) (CENTERED ON) (([0-9]*[\.][0-9]+)|([0-9]*))(N |S )(([0-9]*[\.][0-9]+)|([0-9]*))(W|E)")
polytext = re.compile(r" E\)(.*?)(AREA BOUNDED BY LINES JOINING:((( [0-9]*[\.][0-9]+)|( [0-9]*))(N|S)(( [0-9]*[\.][0-9]+)|( [0-9]*))(W|E))*)")
floattext = re.compile(r"([0-9]*[\.][0-9]+)|([0-9]*)")

#------------------ Search using regular expressions
events = re.findall(eventtext, data) # Number of events
circles = re.findall(circletext, data) # Number of circles
polygons = re.findall(polytext, data) # Number of polygons

#------------------ Display to user
print("Total number of events: ", len(events))
print("Number of circles found: ", len(circles))
print("Number of polygons found: ", len(polygons))

#------------------ Convert circle coordinates to decimal
for index, item in enumerate(range(len(circles))):
    name = str(re.sub("(.*?)E\)","",circles[item][0]))
    latdeg = float(circles[item][5][0:2])
    latmin = float(circles[item][5][2:4])
    latsec = float(circles[item][5][4:len(circles[item][5])])
    lat = latdeg + (latmin/60) + (latsec/3600)

    longdeg = float(circles[item][9][0:3])
    longmin = float(circles[item][9][3:5])
    longsec = float(circles[item][9][5:len(circles[item][9])])
    long = longdeg + (longmin/60) + (longsec/3600)

#------------------ Convert NM to M if present
    if circles[item][3] == "NM":
        rad = (float(circles[item][2]) * 1852.001)
    else:
        rad = float(circles[item][2])
    nov = math.ceil(rad/2)

#------------------ Generate circle kml files
    polycircle = polycircles.Polycircle(latitude=lat,
                                        longitude=long,
                                        radius=rad,
                                        number_of_vertices=nov)

    pol = kml.newpolygon(name=name, outerboundaryis=polycircle.to_kml())
    pol.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
    kml.save("Circle"+str(index)+" "+name+".kml")
    print("File Circle"+str(index)+": "+name+".kml saved")

#------------------ Convert polyon coordinates to decimal and store in list

coordslist = []

for i in range(len(polygons)):
    coordslist.append(polygons[i][1])

for index, item in enumerate(coordslist):
    textlist = item[30:].split()

    boundary = []

    for i in range(0, len(textlist), 2):
        latdeg = float(textlist[i][0:2])
        latmin = float(textlist[i][2:4])
        latsec = float(textlist[i][4:-1])
        lat = latdeg + (latmin/60) + (latsec/3600)

        longdeg = float(textlist[i+1][0:3])
        longmin = float(textlist[i+1][3:5])
        longsec = float(textlist[i+1][5:-1])
        long = longdeg + (longmin/60) + (longsec/3600)

        coord = (long, lat)
        boundary.append(coord)

    name = str(re.sub("(.*?)E\)","",polygons[index][0]))

#------------------ Generate polygon kml files
    pol = kml.newpolygon(name = name)
    pol.outerboundaryis = boundary
    pol.style.linestyle.color = simplekml.Color.green
    pol.style.linestyle.width = 5
    pol.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
    kml.save("Polygon"+str(index)+" "+name+".kml")
    print("File Polygon"+str(index)+": "+name+".kml saved")

input("All files generated, press enter to close")

file.close() # Close NOTAM file
