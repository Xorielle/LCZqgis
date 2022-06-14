"""
This script is written to treat meteorological data of very specific form. Adapt the script for your own meteorological data.

The file Data.txt contains lines of strings: the first line is the header, "POSTE;DATE;RR1;T;FF;DD;U;GLO;N". 
- POSTE is the number of the station
- DATE has format AAAAMMJJHH
- RR1 hourly rainfall (real, kg/m2)
- T temperature (real, K)
- FF mean speed of wind measured every ten minutes (real, m/s)
- DD mean wind direction measured every ten minutes (int, degree)
- U humidity (int, %)
- GLO global radiation (real, J/m2)
- N total nebulosity (int, octa)

One line of data has following format:
69029001;2012010209;1,2;11,0;7,0;200;85;0;8

Myrtille Grulois − June 2022
"""


##########################################
#                 IMPORTS                #
##########################################




##########################################
#         PARAMETERS TO COMPLETE         #
##########################################

ete = ['06','07','08']
automne = ['09','10','11']
hiver = ['12','01','02']
printemps = ['03','04','05']

classification = True #To be set to False except if it is the first time of running code and the files for each season haven’t been created
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

if classification:
    with open('Data1.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    fete = open('ete.txt', 'w', encoding='utf-8')
    fautomne = open('automne.txt', 'w', encoding='utf-8')
    fhiver = open('hiver.txt', 'w', encoding='utf-8')
    fprintemps = open('printemps.txt', 'w', encoding='utf-8')
    fnonclass = open('nonclass.txt','w', encoding='utf-8')

    sheader = lines.pop(0)

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

    fete.close()
    fautomne.close()
    fhiver.close()
    fprintemps.close()
    fnonclass.close()

    sorting('ete.txt')
    sorting('automne.txt')
    sorting('hiver.txt')
    sorting('printemps.txt')



#    print(lines[1].split(';'))





#Analyse de la saison voulue pour trouver un jour type 

    
    
    
    
#lines = ['Readme', 'How to write text files in Python']
#with open('readme.txt', 'w') as f:
#    f.write('\n'.join(lines))