"""
This script is written to work directly in the QGIS Python console. The aim is to create a vector layer with the LCZ of a city, using square one-band rasters with same resolution and with all needed indicators, without using another software than QGIS.

Execute it after opening it in the editor, or directly copy-paste it in the QGIS Python console.

 - Some parameters have to be change, namely the working directory and the names used for the layers in QGIS.
 - Pay attention to the order of the names!
 - Code foreseen for square one-band rasters. Some changes have to be done if it is not the case.
 - If used on Windows: change function createPath
 - Preliminary: a grid vector layer of same dimensions and resolution than the raster layers should be created by hand.
 - Copy the Matrix.py file directly in the folder containing the QGIS project

Tips:
Often, the first letter of a variable indicates its type: i=int, f=float, t=table(list − one t for each dimension, eventually followed by the letter corresponding to the type), v=vector layer, r=raster layer, s=string, q=qgis specific object.

Myrtille Grulois − May 2022
"""

##########################################
#                 IMPORTS                #
##########################################

#from osgeo import gdal, osr
import numpy as np
import Matrix


##########################################
#         PARAMETERS TO COMPLETE         #
##########################################

spath_to_folder = '/home/xorielle/Desktop/Stage/NUDAPT/TestCommandes/MVE' #Where the layers are on the computer
sfile_format = '.shp'
tslayers_name = ['Grid20', 'HEIGHT'] #First name should be the one of the vector layer which will contain the LCZ at the end, then rasters: mean height
resolution = 100
itotalnb_rasters = 1


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
#     Preparation of the vector layer     #
###########################################

#List the layers (dic: {"Key=unique id":"Value=related layer"}). Kind of index creation.
dlayers = QgsProject.instance().mapLayers()

#Get the layer that we will edit, and the names of its fields in a list
vlayer = getLayer(tslayers_name[0])
tslayerlcz_field_names = vlayer.fields().names()

#Check that the vlayer can be edited
vcaps = vlayer.dataProvider().capabilities()
try:
    print("Verification of capabilies in processing...")
    if vcaps & QgsVectorDataProvider.ChangeAttributeValues:
        print('The layer supports the modification of attribute values')
    else:
        print("'WARNING: the layer does NOT support the modification of attribute values")
    if vcaps & QgsVectorDataProvider.AddAttributes:
        print('The layer supports the adding of new attributes')
    else:
        print("'WARNING: the layer does NOT support the adding of new attributes")
except:
    print("'WARNING: no verification of capacities done")

#Create new columns (where the int corresponding to local LCZ (choices 1, 2 and 3) will be stored)
vlayer_provider=vlayer.dataProvider()
try:
    vlayer_provider.addAttributes([QgsField("LCZ_c1",QVariant.Int)])
    vlayer.updateFields()
    print ("Field LCZ_c1 created")
    vlayer_provider.addAttributes([QgsField("LCZ_c2",QVariant.Int)])
    vlayer.updateFields()
    print ("Field LCZ_c2 created")
    vlayer_provider.addAttributes([QgsField("LCZ_c3",QVariant.Int)])
    vlayer.updateFields()
    print ("Field LCZ_c3 created")
except:
    print("'WARNING: the fields LCZ could not be created")

#Create the fourth new column (where the int corresponding to final LCZ will be stored, meaning after verification that the considered zone is wide enough)
try:
    vlayer_provider.addAttributes([QgsField("LCZ_final",QVariant.Int)])
    vlayer.updateFields()
    print ("Field LCZ_final created")
except:
    print("'WARNING: the field LCZ_final could not be created")


###########################################
#                  Main                   #
#       Preparation of raster layers      #
###########################################

#Verify that the length of all lists containing rasters is the same
#FIXME: add all lists
longueur = ((itotalnb_rasters+1)==len(tslayers_name))
if longueur:
    print("Les longueurs semblent correspondre, vérifier dans la définition des fonctions.")
else:
    print("'WARNING: lenghts are not all the same!")

# Preparing tables to store the layers and parameters
trrasters = [None]*(itotalnb_rasters+1)
tirasters_height = [0]*(itotalnb_rasters+1)
tirasters_width = [0]*(itotalnb_rasters+1)
tqrasters_extent = [None]*(itotalnb_rasters+1)

# Get all raster layers
try:
    for i in range(1, itotalnb_rasters+1):
        trrasters[i] = getLayer(tslayers_name[i])
    print("Layers imported successfully")
except:
    print("'WARNING: Layers could not be imported")

# Get size, position and extent of each raster 
try:
    for i in range(1, itotalnb_rasters+1):
        tirasters_height[i] = trrasters[i].height()#Full height and width of the raster in QGIS unit (i.e. meters here)
        tirasters_width[i] = trrasters[i].width()
        tqrasters_extent[i] = trrasters[i].extent()#Extent in QGIS extent format
    print("Shape of layers correctly stored")
except:
    print("'WARNING: Something went wrong when importing the shape of the layers")

# Get geometry of first raster layer
try:
    isize = int(trrasters[1].height()/resolution)
    qextent0 = trrasters[1].extent()
    #Get the position of layer (useful for geotransform later)
    ixmax = qextent0.xMaximum()
    iymax = qextent0.yMaximum()
    ixmin = qextent0.xMinimum()
    iymin = qextent0.yMinimum()
    print("Geometry parameters of first raster layer imported successfully")
except:
    print("'WARNING: geomotry parameters of first raster layer not imported")

# Check if the layers have same shape, size and position
try:
    bextent = True
    for i in range(1, itotalnb_rasters):
        qextent2 = tqrasters_extent[i]
        bextent = verifExtent(qextent0, qextent2, bextent)
    print("All layers have same shape: {b}".format(b = bextent))
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
#    Compute LCZ for each vector cell     #
###########################################

# This first part of the computation aims to find for each cell of the vector layer which are the three LCZ the more probable.

features=vlayer.getFeatures()

# Go through all cells of vector layer
for cell in features:
    x = (cell['left'] + cell['right']) /2
    y = (cell['top'] + cell['bottom']) /2
    print(x,y)


print("End of script, check for WARNINGs...")
