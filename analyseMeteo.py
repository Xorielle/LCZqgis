"""
This script is written to treat meteorological data of very specific form. Adapt the script for your own meteorological data.

The file Data.txt contains lines of strings: the first line is the header, "POSTE,DATE,RR1,T,FF,DD,U,GLO,N". 
- POSTE is the number of the station
- DATE has format AAAAMMJJHH
- RR1 hourly rainfall (real, kg/m2)
- T temperature (real, K)
- FF mean speed of wind measured every ten minutes (real, m/s)
- DD mean wind direction measured every ten minutes (int, degree)
- U humidity (int, %)
- GLO global radiation (real, J/m2)
- N total nebulosity (int, octa)

One line of data has following format (conventional csv format):
69029001,2012010209,1.2,11.0,7.0,200,85,0,8\n

If using other kind of format, it is possible to use the bash script "convert.sh" before the python analysing script to modify your text file before processing it. Adapt the script to what you have.

Myrtille Grulois − June 2022
"""


##########################################
#                 IMPORTS                #
##########################################

import scipy
import numpy as np
import csv

##########################################
#         PARAMETERS TO COMPLETE         #
##########################################

classification = False #To be set to False except if it is the first time of running code and the files for each season haven’t been created
season = 'ete' #Choose which season is going to be analysed


##########################################
#                 FONCTIONS              #
##########################################

def sorting(sfile):
    '''Sort a file by hour'''
    file = open(sfile, 'r', encoding='utf-8')
    lines = file.readlines()
    file.close()
    lines.sort()
    file = open(sfile, 'w', encoding='utf-8')
    for line in lines:
        file.write(line)
    file.close()


##########################################
#               CLASSIFICATION           #
##########################################

ete = ['06','07','08']
automne = ['09','10','11']
hiver = ['12','01','02']
printemps = ['03','04','05']

if classification:
    with open('Data1.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    fete = open('ete.txt', 'w', encoding='utf-8')
    fautomne = open('automne.txt', 'w', encoding='utf-8')
    fhiver = open('hiver.txt', 'w', encoding='utf-8')
    fprintemps = open('printemps.txt', 'w', encoding='utf-8')
    fnonclass = open('nonclass.txt','w', encoding='utf-8')

    sheader = lines.pop(0)
    inc = 0

    for line in lines:
        mois = line[13:15]
        if mois in ete:
            fete.write(line[17:])
        elif mois in automne:
            fautomne.write(line[17:])
        elif mois in hiver:
            fhiver.write(line[17:])
        elif mois in printemps:
            fprintemps.write(line[17:])
        else:
            fnonclass.write(line)
            inc += 1

    fete.close()
    fautomne.close()
    fhiver.close()
    fprintemps.close()
    fnonclass.close()

    sorting('ete.txt')
    sorting('automne.txt')
    sorting('hiver.txt')
    sorting('printemps.txt')

    print("Sorting done. {} line(s) non classified.".format(inc))


##########################################
#                 ANALYSIS               #
##########################################

# Analyse de la saison voulue pour trouver un jour type selon différentes méthodes statistiques
sfile = season + '.csv'

with open(sfile, 'r', newline='', encoding='utf-8') as file:
    data = []
    reader = csv.reader(file)
    for row in reader:
        row = [v if v else None for v in row]
        data.append(row)

    adata = np.array(data, dtype = np.float32)
    print(adata)

#moyenne = np.mean(adata, 0) #0 means mean over the column, 1 over the rows
moyenne = np.nanmean(adata, 0) #Ignoring NaNs
mediane = np.nanmedian(adata, 0)
stddev = np.nanstd(adata, 0)
variance = np.nanvar(adata, 0)
countnonN = np.count_nonzero(~np.isnan(adata), 0) # ~ inverts the matrix, isnan is a boolean with 1 if value is NaN, this enable to count the number of non NAN values in every column.
stderr = stddev / np.sqrt(countnonN)
qrt25 = np.nanquantile(adata, 0.25, 0)
qrt50 = np.nanquantile(adata, 0.5, 0)
qrt75 = np.nanquantile(adata, 0.75, 0)

np.set_printoptions(precision=3, suppress=True) #The arrays printed in the prompt are easier to read but are not modified. 

print("Mean:", moyenne)
print("Median:", mediane)
print("Standard deviation:", stddev)
print("Standard error:", stderr)
print("Variance:", variance)
print("1st quartile:", qrt25)
print("3rt quartile:", qrt75)


##########################################
#                 GRAPHS                 #
##########################################

