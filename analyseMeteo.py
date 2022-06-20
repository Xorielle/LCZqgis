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

from cmath import nan
import scipy
import numpy as np
import csv
import matplotlib.pyplot as plt

##########################################
#         PARAMETERS TO COMPLETE         #
##########################################

classification = False #To be set to False except if it is the first time of running code and the files for each season haven’t been created
season = 'automne' #Choose which season is going to be analysed

toprint = [1,2,3,5,6,7] #List of indexes for parameters to print. [Hour;Rainfall;Tmp;Speed of w;Direction of w;Humidity;Global radiation;Cloud cover] for the files from Lyon Bron and Lyon St-Ex
theader = ["Rainfall", "Temperature", "Wind speed", "Humidity", "Radiation", "Cloud cover"]
tunits = ["$kg.m^{-2}$", "K", "$m.s^{-1}$", "$\%$", "$J.m^{-2}$", "octa"]

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
        axes[row][col].set_xticklabels(hours)
        axes[row][col].set_xlabel("Time (h)")
        axes[row][col].set_ylabel(tunits[i])
    fig.tight_layout(h_pad=2)
    fig.tight_layout()
    fig.suptitle('Mediane, 1st and 3rd quartiles, min and max in {} for:'.format(season))
    plt.subplots_adjust(top=0.85)
    plt.show()


def grrain(nparray):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    total = np.zeros(24)
    ilines = len(nparray)
    for h in range(0,24):
        incr = 0
        line = nparray[0]
        while line[0] < h:
            incr += 1
            line = nparray[incr]
        while line[0] == h and incr < ilines-1 : #With this way of doing, I may forget the last line of 11p.m.
            total[h] += line[1]
            incr += 1
            line = nparray[incr]
    ax.set_title("Total rainfall per hour in {}".format(season))
    ax.plot(hours, total)
    ax.set_xticks(hours)
    #ax.set_xticklabels([str(h) for h in hours])
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("$kg.m^{-2}$")
    plt.show()


def grwindtotal(table, mode):
    ax = plt.subplot(111, projection='polar')
    dir = mode
    speed = np.zeros(24)
    for h in range(0,24):
        speed[h] = table[h][0][0][3] #mean of wind speed
    colors = hours
    angle = dir * 2 * np.pi / 36 
    scatter1 = ax.scatter(angle[0], speed, c=colors, cmap='hsv', label='max')
    ax.scatter(angle[1], speed, c=colors, cmap='hsv', label='2nd max')
    ax.scatter(angle[2], speed, c=colors, cmap='hsv', label='3rd max')
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    label_position=ax.get_rlabel_position() #Find the place for the label
    ax.text(np.radians(label_position+10),ax.get_rmax()/2.,'Wind speed ($m.s^{-1}$)', rotation=label_position+40,ha='center',va='center')
    plt.title("Mode of wind direction and mean wind speed for every hour")
    plt.legend(handles=scatter1.legend_elements(num=24)[0], labels=hours, title="Hours")
    plt.show()


def grwind24(nparray): #Attention ici la table à considérer c’est adata, pas tttstats !
    fig, axes = plt.subplots(nrows=4, ncols=6, subplot_kw={'projection': 'polar'})       
    ilines = len(nparray)
    mode = np.zeros((3, 24)) #Table to get in output to reinject in windtotal
    for h in range(0,24):
        row = int(h/6)
        col = round(6*(h/6-row))
        dirspeed = np.zeros((36,20)) #From 0 to 360°, rounded to the 10° the more close. Speed: from 0 to 19m.s-1, the 19th taken into account all those that are greater than 19.    
        tableau = []
        incr = 0
        line = nparray[0]
        while line[0] < h:
            incr += 1
            line = nparray[incr]
        while line[0] == h and incr < ilines-1 : #With this way of doing, I may forget the last line of 11p.m.
            tableau.append(line)
            incr += 1
            line = nparray[incr]
        for nline in tableau:
            dir = nline[4]
            sp = nline[3]
            try:
                idir = round(dir/10)
                if idir == 36:
                    idir = 0
                if sp >= 19:
                    isp = 19
                else:
                    isp = round(sp)
                dirspeed[idir][isp] += 1
            except:
                print("NaN detected?")        
        angle = np.array([i for i in range(0,36)]*20) * 2 * np.pi / 36
        ttspeed = [[i]*36 for i in range(0,20)]
        speed = []
        for liste in ttspeed:
            for nb in liste:
                speed.append(nb)
        area = dirspeed.flatten()
        scatter = axes[row][col].scatter(angle, speed, s=area)
        #label_position=axes[row][col].get_rlabel_position() #Find the place for the label
        #axes[row][col].text(np.radians(label_position+10),axes[row][col].get_rmax()/2.,'Wind speed ($m.s^{-1}$)', rotation=label_position+40,ha='center',va='center')
        axes[row][col].set_title("{}h".format(hours[h]))
        #Creation of table to use in global wind
        tsum = np.sum(dirspeed, axis=0)
        max1 = np.max(tsum)
        loc1 = np.where(tsum==max1)[0]
        tsum[loc1] = -1
        max2 = np.max(tsum, axis=0)
        loc2 = np.where(tsum==max2)[0]
        tsum[loc2] = -1
        max3 = np.max(tsum, axis=0)
        loc3 = np.where(tsum==max3)[0]
        mode[0][h] = loc1
        mode[1][h] = loc2
        mode[2][h] = loc3
    #fig.set_theta_offset(np.pi/2)
    #fig.set_theta_direction(-1)
    #fig.tight_layout()
    fig.suptitle('3 main wind directions and wind speed for each hour in {}'.format(season))
    plt.legend(handles=scatter.legend_elements("sizes", num=6)[0], labels=scatter.legend_elements("sizes", num=6)[1], title="Nb of occurrences")
    plt.subplots_adjust(top=0.85)
    plt.show()
    return(mode)

#handles, labels = scatter_plot.legend_elements(prop="sizes", alpha=0.6, num=4)
#labels = ["< 5000", "< 20000", " <50000", "> 50000"]
#legend = ax.legend(handles, labels, loc="upper right", title="Sizes")

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
mode = grwind24(adata)
grwindtotal(tttstats, mode)
grrain(adata)