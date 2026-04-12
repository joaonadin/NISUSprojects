# Código de exemplo para pós-processar os resultados das análises estruturais,
# escolher a melhor treliça com base em uma métrica que normaliza o menor coeficiente
# de segurança pela massa da treliça. 
# O código lê os resultados de arquivos JSON, calcula a métrica para cada combinação de
# geometria e divisão, e plota os resultados para comparação visual. 
# Por fim, ele identifica a melhor treliça para cada diâmetro e imprime as informações
# relevantes.

import json
import numpy as np
import matplotlib.pyplot as plt

diameters = [2, 2.5, 3, 3.5]
best_trusses = []

for d in diameters:
    filename = rf"C:/Users/joaon/Desktop/NISUS/Truss/Análises/Subdivisão/diametro{d}/geometriadivisao.json"
    with open(filename, "r") as f:
        dados = json.load(f)

    #print(dados.keys())              ## data tem as chaves "axes" e "data"
    axes = dados["axes"]              ## usando data.keys() conseguimos ver os eixos
    resultados = dados["data"]        ## data tem os resultados, acessados por data[geometria][divisao]

    geometria = axes["axis1"]         ## geometria vai ser o primeiro eixo [0, 1, 2, 3]
    divisao = axes["axis2"]           ## divisao vai ser o segundo eixo [20, 30, 40, 60, 80, 120]

    minSFtension = np.zeros((len(geometria), len(divisao)))
    minSFcompression = np.zeros((len(geometria), len(divisao))) 
    minSFbuckling = np.zeros((len(geometria), len(divisao)))
    mass = np.zeros((len(geometria), len(divisao)))

    for i,geo in enumerate(geometria):
        for j,div in enumerate(divisao):
            minSFtension[i,j] = resultados[str(geo)][str(div)]["SFtension "]
            minSFcompression[i,j] = resultados[str(geo)][str(div)]["SFcompression "]
            minSFbuckling[i,j] = resultados[str(geo)][str(div)]["SFbuckling "]
            mass[i,j] = resultados[str(geo)][str(div)]["mass "]

    resultados = np.zeros((len(geometria), len(divisao)))  ## we want to pick the better truss

    for i in range(len(geometria)):
        for j in range(len(divisao)):
            SF = np.array((minSFtension[i,j], minSFcompression[i,j], minSFbuckling[i,j]))
            menorSF = np.min(SF)  
            SFpormassa = menorSF / mass[i,j]  
            resultados[i,j] = SFpormassa


    geometrianomes = ["Warren", "Pratt", "Howe", "Cross"]

    plt.figure()
    colors = ['red', 'blue', 'green', 'orange']
    for i in range(len(geometria)):
        plt.scatter(divisao, resultados[i, :], color=colors[i], label=f'{geometrianomes[i]}')
    plt.xlabel('Comprimento de subdivisão (mm)')
    plt.ylabel('SF normalizado por massa')
    plt.title(f'Diâmetro {d}')
    plt.legend()
    plt.show()
    best_idx = np.unravel_index(np.argmax(resultados), resultados.shape)
    best_trusses.append((f"Diametro: {d}mm", f"Geometria: {geometria[best_idx[0]]}", f"Divisão: {divisao[best_idx[1]]}", f"SF normalizado: {resultados[best_idx]}"))
    
print(best_trusses)



