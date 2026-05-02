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
d = 3                                               ## mm
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

print(results)

# filename = rf"C:/Users/joaon/Desktop/NISUS/Truss/Análises/Subdivisão/diametro{d}/geometriadivisao.json"
# tl.save_table(filename, geometria, divisao, results)


# n_div = 480 / np.array(divisao)
# idx = np.argsort(n_div)

# n_div = n_div[idx]
# maxtensionstress = np.array(maxtensionstress)[idx]
# maxcompressionstress = np.array(maxcompressionstress)[idx]

# plt.scatter(n_div, maxtensionstress, label='Tração')
# plt.scatter(n_div, maxcompressionstress, label='Compressão')

# plt.title('Tensão máxima por n de divisões - Cruzada - Estudo base ')
# plt.xlabel('Número de divisões')
# plt.ylabel('Tensão máxima [MPa]')
# plt.legend()
# plt.show()


## COEFICIENTES DE SEGURANÇA
# fig, ax1 = plt.subplots()

# ax1.scatter(divisao, minSFtension, label='SF tensão')
# ax1.scatter(divisao, minSFcompression, label='SF compressão')
# ax1.scatter(divisao, minSFbuckling, label='SF buckling')

# # ---- segundo eixo ----
# ax2 = ax1.twinx()
# ax2.set_ylim(0, 0.035)

# ax2.scatter(divisao, mass, marker='x', label='Peso da treliça')

# ax1.set_xlabel('Comprimento de uma divisão')
# ax1.set_ylabel('SF')
# ax2.set_ylabel('Peso [kg]')

# plt.title('Variação para os coeficientes de segurança de acordo com o comprimento de uma divisão de treliça de 480mm')

# # remover grid
# ax1.grid(False)
# ax2.grid(False)

# # legenda conjunta

# h1, l1 = ax1.get_legend_handles_labels()
# h2, l2 = ax2.get_legend_handles_labels()

# ax1.legend(
#     h1 + h2,
#     l1 + l2,
#     loc='center left',
#     bbox_to_anchor=(-0.4, 0)
# )
# plt.show()
