# Código de exemplo para realizar uma análise de subdivisão de treliças, variando o número
# de divisões e a geometria da treliça. Considera apenas treliças sem nariz e tailboom.
# Cria um dict com resultados e salva no formato json para posterior análise.

import trusslibrary as tl
import numpy as np
import matplotlib.pyplot as plt

###### MAIN 

comprimento = 480
divisao = [20, 30, 40, 60, 80, 120]
geometria = [0, 1, 2, 3]
d = 3.5                                               ## mm
E = 210000                                         # MPa (N/mm²)
density = 1.5e-6                                   # kg/mm³
allowablestress = 400                              ## MPa
jointtype = 0                                      ## junta quadrada (nao tem outras implementadas)
# trusstype = 3                                     ## 0->warren / 1-> pratt / 2-> howe / 3-> cross 

maxcompressionstress = np.zeros((len(geometria),len(divisao)))
maxtensionstress = np.zeros((len(geometria),len(divisao)))
maxcompression = np.zeros((len(geometria),len(divisao)))
maxtension = np.zeros((len(geometria),len(divisao)))
normalsafetyfactor = np.zeros((len(geometria),len(divisao)))
minSFtension = np.zeros((len(geometria),len(divisao)))
minSFcompression = np.zeros((len(geometria),len(divisao)))
minSFbuckling = np.zeros((len(geometria),len(divisao)))
mass = np.zeros((len(geometria),len(divisao)))

results = {}
for j,div in enumerate(divisao):
    for i in geometria:
        trusstype = i
        (
        maxcompressionstress[i,j],
        maxtensionstress[i,j],
        maxcompression[i,j],
        maxtension[i,j],
        minSFtension[i,j],
        minSFcompression[i,j],
        minSFbuckling[i,j],
        mass[i,j]
        ) = tl.analyzetruss(comprimento,div,d,E,density,allowablestress,jointtype,trusstype)
        results[(i,div)] = { "SFtension " : minSFtension[i,j],
                          "SFcompression " : minSFcompression[i,j],
                          "SFbuckling " : minSFbuckling[i,j],
                          "mass " : mass[i,j],
            }

#filename = rf"C:/Users/joaon/Desktop/NISUS/Truss/Análises/Full/diametro{d}/geometriadivisao.json"
#tl.save_table(filename, geometria, divisao, results)