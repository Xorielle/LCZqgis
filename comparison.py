"""
This script is written to work directly in the QGIS Python console. The aim is to compare the raster layer with the LCZ of a city (square one-band raster) to the raster resulting from the WUDAPT map.

Execute it after opening it in the editor, or directly copy-paste it in the QGIS Python console.

 - Some parameters have to be change, namely the working directory and the names used for the layers in QGIS.
 - Code foreseen for square one-band rasters. Some changes have to be done if it is not the case.
 - If used on Windows: change function createPath
 - The raster coming from WUDAPT should have been croped to the same extent than the raster created with QGIS. It should also have been converted to a grid of 100x100m, using the statistical analysis tool.
 - On the QGIS raster, one category for "rural" areas should be created, and called "20" so that there is no confusion. 

Tips:
Often, the first letter of a variable indicates its type: i=int, f=float, t=table(list − one t for each dimension, eventually followed by the letter corresponding to the type), v=vector layer, r=raster layer, s=string, q=qgis specific object.

Myrtille Grulois − June 2022
"""

##########################################
#                 IMPORTS                #
##########################################

import numpy as np


##########################################
#         PARAMETERS TO COMPLETE         #
##########################################

spath_to_folder = '/home/xorielle/Desktop/Stage/NUDAPT/TestCommandes/MVE' #Where the layers are on the computer
tslayers_name = ['WUDAPT100x100R', 'LCZ_c1'] #First WUDAPT raster, then QGIS raster (without homogeneization !)
itotalnb_rasters = 2
resolution = 100


###########################################
#         Definition of functions         #
###########################################

def createPath(rasters_name, pos):
    """Return the path to a file"""
    spath = spath_to_folder+rasters_name[pos]+sfile_format
    return(spath)

def getLayer(sname):
    """Return the layer thanks to its exact name"""
    return(QgsProject.instance().mapLayersByName(sname)[0])

def verifExtent(qextent0, qextent2, bextent):
    """Check if to extent are the same, considering previous extents are all matching. Else, return False."""
    if bextent==True:
        return(qextent0==qextent2)
    else:
        return(bextent)

def getCoordinates(x, y):
    """Return the coordinates corresponding to the cell located in the x line and y column"""
    return(ixmin+x*resolution, iymin+y*resolution)

def getRasterContent(raster,x,y):
    """Return the content (qgis object) of the pixel (x,y) in the raster"""
    return(raster.dataProvider().identify(QgsPointXY(x,y), QgsRaster.IdentifyFormatValue))


###########################################
#                  Main                   #
#       Preparation of raster layers      #
###########################################

# Preparing tables to store the layers and parameters
trrasters = [None]*(itotalnb_rasters)
tirasters_height = [0]*(itotalnb_rasters)
tirasters_width = [0]*(itotalnb_rasters)
tqrasters_extent = [None]*(itotalnb_rasters)

# Get all raster layers
try:
    for i in range(0, itotalnb_rasters):
        trrasters[i] = getLayer(tslayers_name[i])
    print("Layers imported successfully")
except:
    print("'WARNING: Layers could not be imported")

# Get size, position and extent of each raster 
try:
    for i in range(0, itotalnb_rasters):
        tirasters_height[i] = trrasters[i].height()#Full height and width of the raster in QGIS unit (i.e. meters here)
        tirasters_width[i] = trrasters[i].width()
        tqrasters_extent[i] = trrasters[i].extent()#Extent in QGIS extent format
    print("Shape of layers correctly stored")
except:
    print("'WARNING: Something went wrong when importing the shape of the layers")

# Get geometry of first raster layer
try:
    isize = int(trrasters[0].height()/resolution)
    qextent0 = trrasters[0].extent()
    #Get the position of layer (useful for geotransform later)
    ixmax = qextent0.xMaximum()
    iymax = qextent0.yMaximum()
    ixmin = qextent0.xMinimum()
    print(ixmin)
    iymin = qextent0.yMinimum()
    print(iymin)
    print("Geometry parameters of first raster layer imported successfully")
except:
    print("'WARNING: geomotry parameters of first raster layer not imported")

# Check if the layers have same shape, size and position
try:
    bextent = True
    for i in range(1, itotalnb_rasters):
        qextent2 = tqrasters_extent[i]
        bextent = verifExtent(qextent0, qextent2, bextent)
    if bextent:
        print("All layers have same shape: {b}".format(b = bextent))
    else:
        print("'WARNING: not all layers have same shape!")
except:
    print("'WARNING: Something went wrong during the verification of layers extent")
    
# Get size of layer and check if square
iheight = tirasters_height[0]
iwidth = tirasters_width[0]
if iheight != iwidth:
    print("'WARNING: Layers are not squares, something will go wrong. You have to modify the layers (or the program)")
else:
    print("Square rasters, the rest of the programm should go well")


###########################################
#                  Main                   #
#       Comparison of LCZ: occurence      #
###########################################

tiicm = [] #Confusion matrix
for i in range(0,12):
    tiicm.append([0]*12)
    #The confusion matrix has to be created this way, else all lines are the same...
#Chaque ligne correspond à une seule LCZ attribuée par WUDAPT, chaque colonne est une LCZ de QGIS. 

#TODO: Add try/except
for y in range(0, isize):
    for x in range(0, isize):
        ix, iy = getCoordinates(x,y)
        #Handle data for one cell on every layer
        tqcontents = []
        tfvalues = []
        #Add the QGIS content for each cell of the two rasters
        tqcontents.append(getRasterContent(trrasters[0], ix, iy))
        tqcontents.append(getRasterContent(trrasters[1], ix, iy))
        #Separate the value from the rest of content
        wudapt = tqcontents[0].results()[1]
        gis = tqcontents[1].results()[1]
        #Get the index of the position of this cell in the confusion matrix
        if wudapt == 20:
            ij = 0
        elif wudapt == None:
            ij = 11
        else:
            ij = int(wudapt)
        if gis == 20:
            ii = 0
        elif gis == None:
            ii = 11
        else:
            ii = int(gis)
        tiicm[ii][ij] += 1

print(tiicm)

        

    
print("End of script, check for WARNINGs...")