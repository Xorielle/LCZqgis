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
import matplotlib.pyplot as plt

##########################################
#         PARAMETERS TO COMPLETE         #
##########################################

classification = False #To be set to False except if it is the first time of running code and the files for each season haven’t been created
season = 'ete' #Choose which season is going to be analysed

toprint = [1,2,3,5,6,7] #List of indexes for parameters to print. [Hour;Rainfall;Tmp;Speed of w;Direction of w;Humidity;Global radiation;Cloud cover] for the files from Lyon Bron and Lyon St-Ex
theader = ["Rainfall", "Temperature", "Wind speed", "Humidity", "Radiation", "Cloud cover"]
tunits = ["$kg.m^{-2}$", "K", "$m.s^{-1}$", "$\%$", "$W.m^{-2}$", "octa"]
#TODO: Direction of wind: how to print that?

np.set_printoptions(precision=3, suppress=True) #The arrays printed in the prompt are easier to read but are not modified. 


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


def statistics(nparray, hour):
    tableau = []
    incr = 0
    line = nparray[0]
    limit = len(nparray)-1
    while line[0] < hour:
        incr += 1
        line = nparray[incr]
    while line[0] == hour and incr < limit:
        tableau.append(line)
        incr += 1
        line = nparray[incr]
    stats = [] #Each row is for all types of values, each column is for all stats for this value
    moyenne = np.nanmean(tableau, 0) #Ignoring NaNs
    mediane = np.nanmedian(tableau, 0)
    stddev = np.nanstd(tableau, 0)
    countnonN = np.count_nonzero(~np.isnan(tableau), 0) # ~ inverts the matrix, isnan is a boolean with 1 if value is NaN, this enable to count the number of non NAN values in every column.
    stderr = stddev / np.sqrt(countnonN)
    qrt25 = np.nanquantile(tableau, 0.25, 0)
    qrt75 = np.nanquantile(tableau, 0.75, 0)
    tmax = np.nanmax(tableau, 0)
    tmin = np.nanmin(tableau, 0)
    stats.append([moyenne, stderr, mediane, countnonN, tmin, qrt25, qrt75, tmax])
    return(stats)


def grmean(table, toprint):
    nbgr = len(toprint)
    fig, axes = plt.subplots(nrows=int((nbgr+1)/2), ncols=2)
    for i in range(0,nbgr):
        var = toprint[i]
        row = int(i/2)
        col = int(2*(i/2-row))
        ymean = []
        ystder = []
        for h in range(0,24):
            ymean.append(table[h][0][0][var])
            ystder.append(table[h][0][1][var])
        axes[row][col].set_title("{}".format(theader[i]))
        axes[row][col].errorbar(hours, ymean, yerr=ystder, fmt='o', capsize=4)
        axes[row][col].set_xlabel("Time (h)")
        axes[row][col].set_ylabel(tunits[i])
    fig.tight_layout(h_pad=2)
    fig.tight_layout()
    fig.suptitle('Mean and standard error in {} for:'.format(season))
    plt.subplots_adjust(top=0.85)
    plt.show()


def grmed(table, toprint):
    nbgr = len(toprint)
    fig, axes = plt.subplots(nrows=int((nbgr+1)/2), ncols=2)
    labels = ['med', 'whislo', 'q1', 'q3', 'whishi']
    indices = [2, 4, 5, 6, 7]
    for i in range(0,nbgr):
        limhours = []
        var = toprint[i]
        row = int(i/2)
        col = int(2*(i/2-row))
        for h in range(0,24):
            dic = {}
            for k in range(0, 5):
                dic[labels[k]] = table[h][0][indices[k]][var]
            limhours.append(dic)
        axes[row][col].set_title("{}".format(theader[i]))
        axes[row][col].bxp(limhours, showfliers=False)
        axes[row][col].set_xlabel("Time (h)")
        axes[row][col].set_ylabel(tunits[i])
    fig.tight_layout(h_pad=2)
    fig.tight_layout()
    fig.suptitle('Mediane, 1st and 3rd quartiles, min and max {} for:'.format(season))
    plt.subplots_adjust(top=0.85)
    plt.show()





##########################################
#               CLASSIFICATION           #
##########################################

ete = ['06','07','08']
automne = ['09','10','11']
hiver = ['12','01','02']
printemps = ['03','04','05']

if classification:
    with open('Data2_generated.csv', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    fete = open('ete.csv', 'w', encoding='utf-8')
    fautomne = open('automne.csv', 'w', encoding='utf-8')
    fhiver = open('hiver.csv', 'w', encoding='utf-8')
    fprintemps = open('printemps.csv', 'w', encoding='utf-8')
    fnonclass = open('nonclass.csv','w', encoding='utf-8')

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

    sorting('ete.csv')
    sorting('automne.csv')
    sorting('hiver.csv')
    sorting('printemps.csv')

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
#    print(adata)



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

#print("Mean:", moyenne)
#print("Median:", mediane)
#print("Standard deviation:", stddev)
#print("Standard error:", stderr)
#print("Variance:", variance)
#print("1st quartile:", qrt25)
#print("3rt quartile:", qrt75)

tttstats = []

#Shape of tttstats:
#[For each hour [[moyenne[Hour;Rainfall;Tmp;Speed of w;Direction of w;Humidity;Global radiation;Cloud cover], stderr, mediane, countnonN, tmin, qrt25, qrt75, tmax]]]

for h in range(0,24):
    tttstats.append(statistics(adata, h))


##########################################
#                 GRAPHS                 #
##########################################

hours = [i for i in range(0,24)]

grmean(tttstats, toprint)
grmed(tttstats, toprint)
grwind(tttstats)
