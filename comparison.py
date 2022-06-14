"""
This script is written to work directly in the QGIS Python console. The aim is to compare the raster layer with the LCZ of a city (square one-band raster) to the raster resulting from the WUDAPT map.

Execute it after opening it in the editor, or directly copy-paste it in the QGIS Python console.

 - Some parameters have to be change, namely the working directory and the names used for the layers in QGIS.
 - Code foreseen for square one-band rasters. Some changes have to be done if it is not the case.
 - If used on Windows: change function createPath
 - The raster coming from WUDAPT should have been croped to the same extent than the raster created with QGIS. It should also have been converted to a grid of 100x100m, using the statistical analysis tool.
 - On the QGIS raster, one category for "rural" areas should be created, and called "20" so that there is no confusion.
 - The WUDAPT layer should also have been treated: all rural classes regrouped under one called "20" (with raster calculator, syntaxe: if(raster>10, 20, raster) )

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
    return(ixmin+(x+0.5)*resolution, iymin+(y+0.5)*resolution)

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

try:
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
            tiicm[ij][ii] += 1
    print("Confusion matrix correcly calculated")
except:
    print("'WARNING: the confusion matrix could not be computed")

# Printing of the results
print("Printing of Confusion Matrix. One line represents how QGIS classified all cells that WUDAPT detected as the same LCZ.")
titles = ["Ru", " 1", " 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", "ND"]
print(titles)
for i in range(0, 12):
    print(titles[i], tiicm[i])


###########################################
#                  Main                   #
#       Some statistics with the CM       #
###########################################

inbtot_cells = 0
titot_wudapt = np.zeros(12)
titot_gis = np.zeros(12)
tftrue_pos = np.zeros(12)

for i in range (0, 12):
    for j in range(0, 12):
        nb = tiicm[i][j]
        inbtot_cells += nb
        titot_gis[j] += nb
        titot_wudapt[i] += nb
        if i == j:
            tftrue_pos[i] = nb          

tottrue = sum(tftrue_pos)

tfdenom_prec = titot_gis #True positive + False positive (classified as the LCZ but WUDAPT says something else)
tfdenom_sens = titot_wudapt #True Positive + False Negative (classified as something else but WUDAPT says it is this particular LCZ)
tffalse_pos = tfdenom_prec - tftrue_pos
tffalse_neg = tfdenom_sens - tftrue_pos
tfdenom_accu = tottrue + tffalse_neg + tffalse_pos
tftrue_neg = tottrue - tftrue_pos

tfaccuracy = (tftrue_pos + tftrue_neg) / (tftrue_pos + tftrue_neg + tffalse_neg + tffalse_pos)
tfprecision = tftrue_pos / (tftrue_pos + tffalse_pos)
tfsensitivity = tftrue_pos / (tftrue_pos + tffalse_neg)
tff1score = 2 * (tfprecision * tfsensitivity) / (tfprecision + tfsensitivity)

print("\nStatistics on all LCZ")
print(titles)
print("Accuracy:", np.round_(tfaccuracy, 2))
print("Precision:", np.round_(tfprecision, 2))
print("Sensitivity:", np.round_(tfsensitivity, 2))
print("F1-score:", np.round_(tff1score, 2))

#Same statistics but regrouping 20 and None into "rural", and all urban LCZ into one category
tiicm2 = [[0,0],[0,0]]
titles = ["Ru", "Urb"]

for i in range(0, 12):
    for j in range(0, 12):
        if (i == 0 or i == 11) and (j == 0 or j == 11):
            tiicm2[0][0] += tiicm[i][j]
        elif (i == 0 or i == 11) and 0 < j < 11:
            tiicm2[0][1] += tiicm[i][j]
        elif 0 < i < 11 and (j == 0 or j == 11):
            tiicm2[1][0] += tiicm[i][j]
        else:
            tiicm2[1][1] += tiicm[i][j]

titot_wudapt = np.zeros(2)
titot_gis = np.zeros(2)
tftrue_pos = np.zeros(2)

for i in range (0, 2):
    for j in range(0, 2):
        nb = tiicm2[i][j]
        titot_gis[j] += nb
        titot_wudapt[i] += nb
        if i == j:
            tftrue_pos[i] = nb          

tottrue = sum(tftrue_pos)

tfdenom_prec = titot_gis #True positive + False positive (classified as the LCZ but WUDAPT says something else)
tfdenom_sens = titot_wudapt #True Positive + False Negative (classified as something else but WUDAPT says it is this particular LCZ)
tffalse_pos = tfdenom_prec - tftrue_pos
tffalse_neg = tfdenom_sens - tftrue_pos
tfdenom_accu = tottrue + tffalse_neg + tffalse_pos
tftrue_neg = tottrue - tftrue_pos

tfaccuracy = (tftrue_pos + tftrue_neg) / (tftrue_pos + tftrue_neg + tffalse_neg + tffalse_pos)
tfprecision = tftrue_pos / (tftrue_pos + tffalse_pos)
tfsensitivity = tftrue_pos / (tftrue_pos + tffalse_neg)
tff1score = 2 * (tfprecision * tfsensitivity) / (tfprecision + tfsensitivity)

print("\nStatistics on urban / rural LCZ")
print(titles)
print("Accuracy:", np.round_(tfaccuracy, 2))
print("Precision:", np.round_(tfprecision, 2))
print("Sensitivity:", np.round_(tfsensitivity, 2))
print("F1-score:", np.round_(tff1score, 2))


print("End of script, check for WARNINGs...")