'''
File to store the matrixes representing the parameters of the LCZ.

Tips:
Often, the first letter of a variable indicates its type: i=int, f=float, t=table(list − one t for each dimension, eventually followed by the letter corresponding to the type), v=vector layer, r=raster layer, s=string, q=qgis specific object.
'''

##########################################
#                 IMPORTS                #
##########################################

import numpy as np

##########################################
#                  MATRIX                #
##########################################

# Matrix taken from Stewart and Oke 2012
#For the conversion of roughness classes (Davenport) into roughness length Z0, see Table 5. in Stewart and Oke 2012. 

tsheader = ['SVF','AR','BSF','ISF','PSF','H','Z0']

# Use of fuzzy logic: trapezes. See Muhammad et al. 2022 for the explanation of the notations and the definition of LZB and RZB

# Correspondancy Davenport - z0:
# 1: 0        < z0 < 0.0005
# 2: 0.0005   < z0 < 0.03
# 3: 0.03     < z0 < 0.10
# 4: 0.10     < z0 < 0.25
# 5: 0.25     < z0 < 0.5
# 6: 0.5      < z0 < 1
# 7: 1        < z0 < 2
# 8: 2        < z0 < 10


LB = np.array([
    [0.2, 2, 40, 40, 0, 25, 2],#LCZ 1
    [0.3, 0.75, 40, 30, 0, 10, 0.5],#LCZ 2
    [0.2, 0.75, 40, 20, 0, 3, 0.5],#LCZ 3
    [0.5, 0.75, 20, 30, 30, 25, 1],#LCZ 4
    [0.5, 0.3, 20, 30, 20, 10, 0.25],#LCZ 5
    [0.6, 0.3, 20, 20, 30, 3, 0.25],#LCZ 6
    [0.2, 1, 60, 0, 0, 2, 0.1],#LCZ 7
    [0.7, 0.1, 30, 40, 0, 3, 0.25],#LCZ 8
    [0.8, 0.1, 10, 0, 60, 3, 0.25],#LCZ 9
    [0.6, 0.2, 20, 20, 40, 5, 0.25],#LCZ 10
    [0, 1, 0, 0, 90, 3, 2],#LCZ A (11)
    [0.5, 0.25, 0, 0, 90, 3, 0.25],#LCZ B (12)
    [0.7, 0.25, 0, 0, 90, 0, 0.1],#LCZ C (13)
    [0.9, 0, 0, 0, 90, 0, 0.03],#LCZ D (14)
    [0.9, 0, 0, 90, 0, 0, 0.0005],#LCZ E (15)
    [0.9, 0, 0, 0, 90, 0.25, 0.0005],#LCZ F (16)
    [0.9, 0, 0, 0, 90, 0, 0],#LCZ G (17)
])


RB = np.array([
    [0.4, 20, 60, 60, 10, 1000, 10],#LCZ 1
    [0.6, 2, 70, 50, 20, 25, 2],#LCZ 2
    [0.6, 1.5, 70, 50, 30, 10, 1],#LCZ 3
    [0.7, 1.25, 40, 40, 40, 1000, 10],#LCZ 4
    [0.8, 0.75, 40, 50, 40, 25, 1],#LCZ 5
    [0.9, 0.75, 40, 50, 60, 10, 1],#LCZ 6
    [0.5, 2, 90, 20, 30, 4, 0.5],#LCZ 7
    [1, 0.3, 50, 50, 20, 10, 0.5],#LCZ 8
    [1, 0.25, 20, 20, 80, 10, 1],#LCZ 9
    [0.9, 0.5, 30, 40, 50, 15, 1],#LCZ 10
    [0.4, 20, 10, 10, 100, 30, 10],#LCZ A (11)
    [0.8, 0.75, 10, 10, 100, 15, 1],#LCZ B (12)
    [0.9, 1, 10, 10, 100, 2, 0.5],#LCZ C (13)
    [1, 0.1, 10, 10, 100, 1, 0.25],#LCZ D (14)
    [1, 0.1, 10, 100, 10, 0.25, 0.03],#LCZ E (15)
    [1, 0.1, 10, 10, 100, 0.25, 0.03],#LCZ F (16)
    [1, 0.1, 10, 10, 100, 0, 0.0005],#LCZ G (17)
])

LZB = LB - (RB - LB)
RZB = RB + (RB - LB)

#Correct to have no negative value in LZB: should I let it negative, as nobody mentionned anything about it?
#for lcz in LZB:
#    for i in range(0,7):
#        if lcz[i] < 0:      
#            lcz[i] = 0

#Correct LZB where RB does not exist (no max, one has been filled in by hand)
LZB[0][1] = 1.5 #LCZ1, AR
LZB[0][5] = 15 #LCZ1, Hmean
LZB[0][6] = 1 #LCZ1, z0
LZB[3][5] = 15 #LCZ4, Hmean
LZB[3][6] = 1 #LCZ4, z0
LZB[10][1] = 0.75 #LCZA, AR
LZB[10][6] = 1 #LCZA, z0



