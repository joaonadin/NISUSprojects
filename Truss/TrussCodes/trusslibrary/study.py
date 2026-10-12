import numpy as np
from .geometry.fulltrusses import split_parts
from .geometry.landing_gear import get_matched_joints_tower
from .geometry.landing_gear import get_matched_joints_pyramid

def setstudysquare(joints, mode, Lforce):
    """
    Parameters
    ----------
    joints : recebe joints, que armazena as coordenadas dos pontos.

    What it does

    Atribui forças de acordo com o caso básico de estudo definido:
        35N de tração dividido entre 4 nós frontais,
        Lforce de sustentação dividido entre nós superiores, desconsiderando primeira e última seções
        No caso concentrado, Lforce aplicado na metade da treliça, dividido entre os 2 nós superiores da seção correspondente
        80N de payload, divididos entre os 2 nós inferiores localizados em 40% do comprimento
        OBS: no caso concentrated, insere forças concentradas no início - mais coerente com a proposta
             adotada pela equipe para o projeto 2026
    Fixa nós da última seção - completamente pinados

    Returns
    -------
    pinados : ID dos nós pinados
    forces : ID das forças e vetor de força
    Ambos no formato que o slientruss usa
    """
    # pega apenas joints da fuselagem com seus índices globais
    truss_ids = [i for i, j in enumerate(joints)
                 if isinstance(j, dict) and 'truss' in j.get('sections', [])]
    nose_ids =  [i for i, j in enumerate(joints)
                 if isinstance(j, dict) and 'nose' or 'truss' in j.get('sections', [])]           

    nsections = len(truss_ids) // 4

    pinados    = np.array(truss_ids[-4:])
    tracionados = np.array(nose_ids[:4])

    if (mode == 'distributed'):
        # nós superiores excluindo primeira e última seção (índices locais 6,7 por seção)
        upperright = np.array([truss_ids[4*s + 2] for s in range(1, nsections - 1)])
        upperleft  = np.array([truss_ids[4*s + 3] for s in range(1, nsections - 1)])
        payload_section = int(nsections * 0.4)
        payloadnode1 = truss_ids[payload_section * 4]
        payloadnode2 = truss_ids[payload_section * 4 + 1]
    elif (mode == 'concentrated'):
        s = nsections//2                                             ## apply on first section
        upperright = np.array([truss_ids[4*s + 2] ])
        upperleft  = np.array([truss_ids[4*s + 3] ])
        payload_section = s+1
        payloadnode1 = truss_ids[payload_section * 4]
        payloadnode2 = truss_ids[payload_section * 4 + 1]
    else: 
        print("ERRO: especifique um estudo")
        return 


    Force  =  Lforce/2 / len(upperright)    ## metade da sustentação cada lado, dividido pela dist
    Payload =  80 / 2                            ## 100N de payload dividido entre os 2 nós
    Tforce  = -35 / len(tracionados)

    forces = []
    forces.append((payloadnode1, (0, 0, -Payload)))
    forces.append((payloadnode2, (0, 0, -Payload)))
    for i in tracionados:
        forces.append((int(i), (Tforce, 0, 0)))
    for i in upperright:
        forces.append((int(i), (0, 0, Force)))
    for i in upperleft:
        forces.append((int(i), (0, 0, Force)))

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
    nosejoints, trussjoints, tailboomjoints = split_parts(joints, case = 'forces')[0:3]
    forces = []
    jointids = np.arange(0, len(joints), 1)   # getting joint ids 
    labels = np.array([0]*len(nosejoints) + [1]*len(trussjoints) + [2]*len(tailboomjoints), dtype=int)  ## 0 for nose, 1 for truss, 2 for tailboom
    tracionados = jointids[labels == 0][:4]   ## first 4 nodes get traction
    coords = np.array([j['coords'] if isinstance(j, dict) else j for j in joints])
    upperright = jointids[(labels == 1) & (coords[:,1] > 0) & (coords[:,2] > 0)]
    upperleft  = jointids[(labels == 1) & (coords[:,1] == 0) & (coords[:,2] > 0)]
    # upperright = jointids[(labels == 1) & (joints[:,1]>0) & (joints[:,2]>0)]  ## upper right node IDs 
    # upperleft = jointids[(labels == 1)& (joints[:,1]==0) & (joints[:,2]>0)]  ## upper left node IDs
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

def set_study_tailboom(joints, force, moment):
    """
    Parameters
    ----------
    joints : recebe joints, que armazena as coordenadas dos pontos.
    force: força de sustentação negativa a ser aplicada na cauda, em N
    moment: momento a ser induzido na cauda, em Nm

    What it does

    Atribui forças de acordo com o caso básico de estudo definido para o tailboom:
        Força de sustentação negativa dividida no fim do tailboom
        Momento induzido por binário no fim do tailboom
        Se há encaixe, aplica forças do upper_last_section em G2 e H2,
        e upper_last_but_one_section em G e H

    """
    joints_coords = np.array([joint['coords'] if isinstance(joint, dict) else joint for joint in joints])
    forces = []
    jointids = np.arange(0, len(joints), 1)   # getting joint ids 
    labels = []
    for joint in joints:
        if isinstance(joint, dict):
            sections = joint.get('sections', [])
            if 'tailboom' in sections:
                labels.append(2)
            elif 'truss' in sections:
                labels.append(1)
            elif 'nose' in sections:
                labels.append(0)
            else:
                labels.append(3)
        else:
            labels.append(3)
    labels = np.array(labels, dtype=int)
    tailboom_nodes = jointids[labels == 2]       ## joints que recebem sustentação invertida
    fixed_nodes = tailboom_nodes[:4]              ## primeiros 4 nós do tailboom são fixos
    
    # Verificar se há encaixe
    encaixe_nodes = [idx for idx, j in enumerate(joints) if isinstance(j, dict) and 'encaixe' in j.get('sections', [])]
    if encaixe_nodes:
        # Há encaixe: aplicar forças nos joints específicos do encaixe
        # Assumindo ordem: E, F, G, H, C2, D2, G2, H2
        G = encaixe_nodes[2]   # G
        H = encaixe_nodes[3]   # H
        G2 = encaixe_nodes[6]  # G2
        H2 = encaixe_nodes[7]  # H2
        upper_last_section = [G2, H2]  # forças do upper_last_section em G2 e H2
        upper_last_but_one_section = [G, H]  # forças do upper_last_but_one_section em G e H
        # Distância para momento: usar entre G e G2 (distância em x = b)
        distance_between_nodes = abs(joints_coords[G2][0] - joints_coords[G][0])
    else:
        # Sem encaixe: comportamento padrão
        upper_last_section = tailboom_nodes[-2:]       ## ultimos 2 nós
        upper_last_but_one_section = tailboom_nodes[-6:-4]   ## 2 nós superiores da ultima seção
        distance_between_nodes = abs(joints_coords[tailboom_nodes[-1]][0] - joints_coords[tailboom_nodes[-5]][0])  ## distância em x entre os últimos nós do tailboom
    
    Fmoment = moment / (distance_between_nodes*1e-3) ## força equivalente para o momento aplicado
    for i in upper_last_section:
        forces.append((i, (0, 0, force/2 + Fmoment/2)))
    for i in upper_last_but_one_section:
        forces.append((i, (0, 0, - Fmoment/2)))
    return fixed_nodes, forces

def set_study_landinggear(joints, force):
    """
    Parameters
    ----------
    joints : recebe joints, que armazena as coordenadas dos pontos.
    force: tupla (Fx, Fy, Fz) com as componentes da força a ser aplicada, em N

    What it does

    Atribui forças de acordo com o caso básico de estudo definido para o landing gear:
        Força dividida igualmente entre os 4 últimos nós do landing gear
        Fixa os 4 primeiros nós do landing gear

    """
    forces = []
    jointids = np.arange(0, len(joints), 1)
    labels = []
    landinggear_types = set()

    for joint in joints:
        if isinstance(joint, dict):
            sections = joint.get('sections', [])
            is_landinggear = any(tag in sections for tag in ('landinggear_tow', 'landinggear_pyr'))
            if is_landinggear:
                labels.append(1)
                if 'landinggear_tow' in sections:
                    landinggear_types.add('tower')
                if 'landinggear_pyr' in sections:
                    landinggear_types.add('pyramid')
            else:
                labels.append(0)
        else:
            labels.append(0)

    labels = np.array(labels, dtype=int)
    landinggear_nodes = jointids[labels == 1]
    nosejoints, trussjoints, _, landinggearjoints = split_parts(joints, case='forces')
    truss_indices = [idx for idx, joint in enumerate(joints)
                     if isinstance(joint, dict) and 'truss' in joint.get('sections', [])]

    fixed_nodes = np.array([], dtype=int)
    if 'tower' in landinggear_types:
        matched_local = get_matched_joints_tower(landinggearjoints, trussjoints)
        fixed_nodes = np.array([truss_indices[i] for i in matched_local], dtype=int)
    elif 'pyramid' in landinggear_types:
        print("Pyramid landing gear detected. Matching joints for boundary conditions...")
        matched_local = get_matched_joints_pyramid(joints, landinggearjoints, trussjoints)
        fixed_nodes = np.array([truss_indices[i] for i in matched_local], dtype=int)

    last_nodes = landinggear_nodes[-4:]
    for i in last_nodes:
        forces.append((i, (force[0] / 4, force[1] / 4, force[2] / 4)))
    return fixed_nodes, forces