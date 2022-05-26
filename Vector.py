"""
This script is written to work directly in the QGIS Python console. The aim is to create a vector layer with the LCZ of a city, using square one-band rasters with same resolution and with all needed indicators, without using another software than QGIS.

Execute it after opening it in the editor, or directly copy-paste it in the QGIS Python console.

 - Some parameters have to be change, namely the working directory and the names used for the layers in QGIS.
 - Pay attention to the order of the names!
 - Code foreseen for square one-band rasters. Some changes have to be done if it is not the case.
 - If used on Windows: change function createPath
 - Preliminary: a grid vector layer of same dimensions and resolution than the raster layers should be created by hand.

Tips:
Often, the first letter of a variable indicates its type: i=int, f=float, t=table(list − one t for each dimension, eventually followed by the letter corresponding to the type), v=vector layer, r=raster layer, s=string, q=qgis specific object.

Myrtille Grulois − May 2022
"""

##########################################
#                 IMPORTS                #
##########################################

#from osgeo import gdal, osr
import numpy as np


##########################################
#         PARAMETERS TO COMPLETE         #
##########################################

spath_to_folder = '/home/xorielle/Desktop/Stage/NUDAPT/TestCommandes/' #Where the layers are on the computer
sfile_format = '.shp'
layers_name = ['Statistics'] #First name should be the one of the vector layer which will contain the LCZ at the end
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
vlayer = getLayer(layers_name[0])
tslayerlcz_field_names = vlayer.fields().names()

#Get the index corresponding to the coordinates of each cell in the layer
tsfield_names = ['left', 'right', 'top', 'bottom']
ilen_fields = len(tsfield_names)
tifield_index = [0]*ilen_fields #Store the index
print("Looking for the index of the cell position in vector layer...")
for i in range (0, ilen_fields):
    try:
        tifield_index[i] = tslayerlcz_field_names.index(tsfield_names[i])
        print("Index {i} found".format(i=i))
    except:
        print("WARNING: Index {i} not found".format(i=i))

#Check that the vlayer can be edited
tscaps_check = ['ChangeAttributeValues']
vcaps = vlayer.dataProvider().capabilities()

if vcaps & QgsVectorDataProvider.ChangeAttributeValues:
    print('The layer supports the modification of attribute values')
else:
    print('WARNING: the layer does NOT support the modification of attribute values')
if vcaps & QgsVectorDataProvider.AddAttributes:
    print('The layer supports the adding of new attributes')
else:
    print('WARNING: the layer does NOT support the adding of new attributes')

#Create the new column (where the int corresponding to LCZ will be stored)
vlayer_provider=vlayer.dataProvider()
try:
    vlayer_provider.addAttributes([QgsField("LCZ",QVariant.Int)])
    vlayer.updateFields()
    print ("Field LCZ created")
except:
    print("WARNING: the field LCZ could not be created")


###########################################
#                  Main                   #
#      Edit each cell of vector layer     #
###########################################

# Get raster value
try:
    rlayer = getLayer("ALTEZZA MEDIA")
    isize = int(rlayer.height()/resolution)
    qextent0 = rlayer.extent()
    #Get the position of layer (useful for geotransform later)
    ixmax = qextent0.xMaximum()
    iymax = qextent0.yMaximum()
    ixmin = qextent0.xMinimum()
    iymin = qextent0.yMinimum()#Does not work
#caps = vlayer.capabilities()
#if caps & QgsVectorDataProvider.DeleteFeatures:
#    print('The layer supports DeleteFeatures')
    print("First layer imported successfully")
except:
    print("WARNING: Raster layer not imported")
    
    
#UPDATING/ADD ATTRIBUTE VALUE
features=vlayer.getFeatures()
#for f in features:
#    print ("f : {f}, attributes: {a}".format(f = f, a = f.attributes()))
vlayer.startEditing()
for f in features:
    id=f.id()
    attr_value={7:43}
    vlayer_provider.changeAttributeValues({id:attr_value})
vlayer.commitChanges()

#DELETE FIELD
#layer_provider.deleteAttributes([8])
#vlayer.updateFields()

##########################################
# If you are working inside QGIS (either from the console
#or from a plugin), it might be necessary to force a redraw
#of the map canvas in order to see the changes you’ve done
#to the geometry, to the style or to the attributes:
# If caching is enabled, a simple canvas refresh might not be sufficient
#to trigger a redraw and you must clear the cached image for the layer

#if iface.mapCanvas().isCachingEnabled():
#    layer.triggerRepaint()
#else:
#    iface.mapCanvas().refresh()It is possible to either change feature’s geometry or to change some attributes. The following example first changes values of attributes with index 0 and 1, then it changes the feature’s geometry.

###########################################
# It is possible to either change feature’s geometry or to
#change some attributes. The following example changes values
#of attributes with index 0 and 1

#fid = 100   # ID of the feature we will modify
#if caps & QgsVectorDataProvider.ChangeAttributeValues:
#    attrs = { 0 : "hello", 1 : 123 }
#    layer.dataProvider().changeAttributeValues({ fid : attrs })


############################################
 
#ADDING NEW FIELD OUT OF PYQGIS
#from PyQt5.QtCore import QVariant
#vlayer_provider=vlayer.dataProvider()
#vlayer_provider.addAttributes([QgsField("Length",QVariant.Double)])
#vlayer.updateFields()
#print (vlayer.fields().names())

#PRINT STRING OF ALL CAPABILITIES (WORDS SEPARED BY SPACES AND CAPABILITIES BY COMMA)
#caps_string = vlayer.dataProvider().capabilitiesString()
#print(caps_string)