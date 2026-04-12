import numpy as np
from .geometry.fulltrusses import splitnosetrusstailboom

def setstudysquare(joints):
    """
    Parameters
    ----------
    joints : recebe joints, que armazena as coordenadas dos pontos.

    What it does

    Atribui forças de acordo com o caso básico de estudo definido:
        35N de tração dividido entre 4 nós frontais,
        380N de sustentação dividido entre nós superiores, desconsiderando primeira e última seções
        70N de payload, divididos entre os 2 nós inferiores localizados em 40% do comprimento
    Fixa nós da última seção - completamente pinados

    Returns
    -------
    pinados : ID dos nós pinados
    forces : ID das forças e vetor de força
    Ambos no formato que o slientruss usa
    """
    jointids = np.arange(0, len(joints), 1)   # getting joint ids
    nsections = len(joints) // 4
    pinados = jointids[-4:]                 ## last 4 nodes pinned
    tracionados = jointids[:4]              ## first 4 nodes get traction
    upperright = np.arange(6, 2 + 4 * (nsections - 1), 4)  ## upper right nodes (looking from front - excluding first and last section)
    upperleft = np.arange(7, 3 + 4 * (nsections - 1), 4)  ## upper left nodes (looking from front - excluding first and last section)
    payloadnode1 = int(nsections * 0.4) * 4           ## payload put on 40% of extension
    payloadnode2 = int(nsections * 0.4) * 4 + 1
    Lforce = 190 / len(upperright)               ## 190N distributed on nodes
    Payload = 35                                 ## 35N each node for 7kg payload
    Tforce = -35 / len(tracionados)              ## 35N distributed on tractioned nodes
    forces = []
    forces.append((payloadnode1, (0, 0, -Payload)))
    forces.append((payloadnode2, (0, 0, -Payload)))
    for i in tracionados:
        forces.append((i, (Tforce, 0, 0)))  ## jointID, vetor
    for i in upperleft:
        forces.append((i, (0, 0, Lforce)))
    for i in upperright:
        forces.append((i, (0, 0, Lforce)))
    return pinados, forces


def setstudyfull(joints):
    """
    Parameters
    ----------
    joints : recebe joints, que armazena as coordenadas dos pontos.

    What it does

    Atribui forças de acordo com o caso básico de estudo definido:
        35N de tração dividido entre 4 nós frontais,
        380N de sustentação dividido entre nós superiores da treliça, desconsiderando primeira e última seções
        70N de payload, divididos entre os 2 nós inferiores localizados em 30% do comprimento da treliça
        200N de sustentação negativa divididos entre os 2 nós da cauda
        Fixa nós inferiores imediatamente após inserir payload - completamente pinados

    """
    joints = np.array(joints)
    nosejoints, trussjoints, tailboomjoints = splitnosetrusstailboom(joints, case = 'forces')
    forces = []
    jointids = np.arange(0, len(joints), 1)   # getting joint ids 
    labels = np.array([0]*len(nosejoints) + [1]*len(trussjoints) + [2]*len(tailboomjoints), dtype=int)  ## 0 for nose, 1 for truss, 2 for tailboom
    tracionados = jointids[labels == 0]  ## first 4 nodes get traction
    upperright = jointids[(labels == 1) & (joints[:,1]>0) & (joints[:,2]>0)]  ## upper right node IDs 
    upperleft = jointids[(labels == 1)& (joints[:,1]==0) & (joints[:,2]>0)]  ## upper left node IDs
    upperright= upperright[1:-1]   ## tirando primeiros e últimos p aplicar forças
    upperleft = upperleft[1:-1]
    negativeliftnodes = jointids[-4:]     ## joints que recebem sustentação invertida
    payloadsection = int(len(trussjoints)//4 * 0.4)    ## seção de payload em 40% de comprimento da treliça
    payloadnodes = np.array((4 * (payloadsection+1), 4 * (payloadsection+1)+1),dtype=int)        ## nós de payload em 40% depois do nariz
    pinnednodes = payloadnodes + np.array((4,4))                                             ## nós pinados, seção seguinte ao payload
    Lforce = 150 / len(upperright)               ## 190N distributed on nodes
    Ldownforce = -200 / len(negativeliftnodes)
    Payload = 35                                 ## 35N each node for 7kg payload
    Tforce = -35 / len(tracionados)              ## 35N distributed on tractioned nodes
    forces = []
    for i in negativeliftnodes:
        forces.append((i, (0, 0, Ldownforce)))
    for i in payloadnodes:
        forces.append((i, (0, 0, -Payload)))
    for i in tracionados:
        forces.append((i, (Tforce, 0, 0)))  ## jointID, vetor
    for i in upperleft:
        forces.append((i, (0, 0, Lforce)))
    for i in upperright:
        forces.append((i, (0, 0, Lforce)))
    return pinnednodes, forces