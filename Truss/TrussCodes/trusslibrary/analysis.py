import numpy as np
from slientruss3d.truss import Truss
from slientruss3d.type import MemberType
from .geometry import splitnosetrusstailboom

def safetycoefanls(truss, members, stress, elementforces, allowablestress, I, E, 
                   joints=None, members_list=None, I_dict=None):
    """
    Parameters
    ----------
    truss : objeto treliça do slientruss3d
    members: vetor contendo os IDs dos pontos que cada uma das barras liga
    stress : dict que o slientruss retorna com as tensoes das trelicas
    elementforces : dict que o slientruss retorna com as forças internas das treliças
    allowablestress : tensao máxima que o material suporta
    I : momento de inércia da seção das barras (para backward compatibility)
    E : Módulo de Young do material
    joints : lista de coordenadas dos joints (opcional, necessário para análise compartimentalizada)
    members_list : lista de tuplas (j0, j1) dos membros (opcional, necessário para análise compartimentalizada)
    I_dict : dict com momentos de inércia por seção {'nose': I_nose, 'truss': I_truss, 'tailboom': I_tailboom}
             Se fornecido, retorna análise compartimentalizada por seção

    Returns
    -------
    Se I_dict é None (backward compatibility):
        Tupla com: (maxcompressionstress, maxtensionstress, maxcompression, maxtension, 
                   minSFtension, minSFcompression, minSFbuckling)
    
    Se I_dict é fornecido:
        Dict compartimentalizado com estrutura:
        {
            'global': {...valores globais...},
            'nose': {...valores da seção nariz...},
            'truss': {...valores da seção treliça...},
            'tailboom': {...valores da seção tailboom...}
        }
    """
    
    def _calculate_section_results(section_stress, section_forces, section_length_index_pairs, I_value):
        """Calcula resultados para uma seção específica"""
        if not section_stress or not section_forces:
            return None
        
        # Stress analysis
        max_comp_stress = abs(min(section_stress))
        max_tens_stress = max(section_stress)
        
        # Force analysis
        max_comp_force = abs(min(section_forces))
        max_tens_force = max(section_forces)
        
        min_SF_tension = allowablestress / max_tens_stress if max_tens_stress > 0 else np.inf
        min_SF_compression = abs(allowablestress / max_comp_stress) if max_comp_stress > 0 else np.inf
        
        # Buckling analysis para a seção
        buckling_SF = []
        for length, global_member_idx in section_length_index_pairs:
            # Obter força do membro global
            force = elementforces.get(global_member_idx, 0)
            if force < 0 and I_value is not None:
                Pcr = np.pi**2 * E * I_value / length**2
                buckling_SF.append(-Pcr / force)
            elif force < 0:
                buckling_SF.append(np.inf)
        
        min_SF_buckling = min(buckling_SF) if buckling_SF else np.inf
        
        return {
            'max_compression_stress': max_comp_stress,
            'max_tension_stress': max_tens_stress,
            'max_compression_force': max_comp_force,
            'max_tension_force': max_tens_force,
            'min_SF_tension': min_SF_tension,
            'min_SF_compression': min_SF_compression,
            'min_SF_buckling': min_SF_buckling
        }
    
    # ============ ANÁLISE GLOBAL (backward compatibility) ============
    maxcompressionstress = abs(min(stress.values()))
    maxtensionstress = max(stress.values())
    maxcompression = abs(min(elementforces.values()))
    maxtension = max(elementforces.values())
    minSFtension = allowablestress / maxtensionstress
    minSFcompression = abs(allowablestress / maxcompressionstress)

    # Buckling analysis global
    lengths = []
    member_ids_with_forces = []
    for memberID, connect in members.items():
        member = truss.GetMemberFromConnect(connect)
        lengths.append(member.length)
        if memberID in elementforces:
            member_ids_with_forces.append(memberID)
    
    # Se I_dict for fornecido, usar I correto por membro
    if I_dict is not None and joints is not None and members_list is not None:
        nosejoints, trussjoints, tailboomjoints = splitnosetrusstailboom(joints, case='geometry')
        nose_end = len(nosejoints)
        truss_end = nose_end + len(trussjoints)
        
        bucklingsafetyfactor = []
        for memberID in member_ids_with_forces:
            # Encontrar o índice do membro na lista members_list
            member_index = None
            for idx, (j0, j1) in enumerate(members_list):
                # Este é um membro que conecta j0 e j1, mas preciso mapear para memberID
                # Como memberID é sequencial, assumo que member_index = memberID
                if idx == memberID:
                    member_index = idx
                    break
            
            if member_index is not None:
                max_id = max(members_list[member_index][0], members_list[member_index][1])
                if max_id < nose_end:
                    I_member = I_dict.get('nose', I)
                elif max_id < truss_end:
                    I_member = I_dict.get('truss', I)
                else:
                    I_member = I_dict.get('tailboom', I)
                
                P = elementforces[memberID]
                if P < 0:
                    L = lengths[memberID]  # lengths está indexado por memberID
                    Pcr = np.pi**2 * E * I_member / L**2
                    bucklingsafetyfactor.append(-Pcr / P)
                else:
                    bucklingsafetyfactor.append(np.inf)
    else:
        # Análise global original (todos membros com mesmo I)
        bucklingsafetyfactor = []
        for memberID in member_ids_with_forces:
            P = elementforces[memberID]
            if P < 0:
                L = lengths[memberID]
                Pcr = np.pi**2 * E * I / L**2
                bucklingsafetyfactor.append(-Pcr / P)
            else:
                bucklingsafetyfactor.append(np.inf)
    
    minSFbuckling = min(i for i in bucklingsafetyfactor if i > 0) if bucklingsafetyfactor else np.inf

    # ============ SE NÃO FOR COMPARTIMENTALIZADO, RETORNA COMO ANTES ============
    if I_dict is None or joints is None or members_list is None:
        return (
            maxcompressionstress,
            maxtensionstress,
            maxcompression,
            maxtension,
            minSFtension,
            minSFcompression,
            minSFbuckling
        )

    # ============ ANÁLISE COMPARTIMENTALIZADA ============
    nosejoints, trussjoints, tailboomjoints = splitnosetrusstailboom(joints, case='geometry')
    nose_end = len(nosejoints)
    truss_end = nose_end + len(trussjoints)
    
    # Separar por seção
    sections = {'nose': [], 'truss': [], 'tailboom': []}
    
    for member_idx, (j0, j1) in enumerate(members_list):
        max_id = max(j0, j1)
        
        if max_id < nose_end:
            section = 'nose'
        elif max_id < truss_end:
            section = 'truss'
        else:
            section = 'tailboom'
        
        sections[section].append(member_idx)
    
    # Calcular resultados por seção
    results = {
        'global': {
            'max_compression_stress': maxcompressionstress,
            'max_tension_stress': maxtensionstress,
            'max_compression_force': maxcompression,
            'max_tension_force': maxtension,
            'min_SF_tension': minSFtension,
            'min_SF_compression': minSFcompression,
            'min_SF_buckling': minSFbuckling  # Agora usa o valor correto calculado acima
        }
    }
    
    for section_name in ['nose', 'truss', 'tailboom']:
        member_indices = sections[section_name]
        
        if not member_indices:
            results[section_name] = None
            continue
        
        # Coletar stress e forces para esta seção
        section_stress = []
        section_forces = []
        section_length_index_pairs = []
        
        for local_idx, global_member_idx in enumerate(member_indices):
            if global_member_idx in stress:
                section_stress.append(stress[global_member_idx])
            if global_member_idx in elementforces:
                section_forces.append(elementforces[global_member_idx])
            
            # Obter comprimento do membro
            connect = members[global_member_idx]
            member = truss.GetMemberFromConnect(connect)
            section_length_index_pairs.append((member.length, global_member_idx))
        
        if not section_stress or not section_forces:
            results[section_name] = None
            continue
        
        I_section = I_dict.get(section_name, I)
        results[section_name] = _calculate_section_results(
            section_stress, section_forces, section_length_index_pairs, I_section
        )
    
    return results

def settruss(joints, supports, forces, members, truss, memberType, member_types_dict=None):
    """
    Parameters
    ----------
    joints : recebe joints, que armazena as coordenadas dos pontos.
    supports : vetor contendo os tipos de suporte para cada nó na mesma ordem de joints
    forces : ID das forças e vetor de força
    members: vetor contendo os IDs dos pontos que cada uma das barras liga, ex: barra de ID i liga a tupla i de pontos
    truss : truss que foi criada a partir da biblioteca usando Truss().
    memberType : definido por MemberType(area, E, density). Usado como padrão para todos os membros se member_types_dict não for fornecido.
    member_types_dict : dict opcional com tipos de membro para diferentes partes: {'nose': memberType_nose, 'truss': memberType_truss, 'tailboom': memberType_tailboom}.
                        Se fornecido, atribui tipos diferentes com base na seção da estrutura.

    Returns
    -------
    trussmembers : objeto treliça, que será resolvido para obtenção dos resultados

    """
    # Split joints to determine ranges for member assignment
    nosejoints, trussjoints, tailboomjoints = splitnosetrusstailboom(joints)
    nose_end = len(nosejoints)
    truss_end = nose_end + len(trussjoints)

    for joint, support in zip(joints, supports):
        truss.AddNewJoint(joint, support)
    for jointID, force in forces:
        truss.AddExternalForce(jointID, force)
    for jointID0, jointID1 in members:
        max_id = max(jointID0, jointID1)
        if member_types_dict:
            if max_id < nose_end:
                mt = member_types_dict.get('nose', memberType)
            elif max_id < truss_end:
                mt = member_types_dict.get('truss', memberType)
            else:
                mt = member_types_dict.get('tailboom', memberType)
        else:
            mt = memberType
        truss.AddNewMember(jointID0, jointID1, mt)
    trussmembers = truss.GetMembers()
    return trussmembers

def analyzetruss(comprimento, divisao, d, E, density, allowablestress, jointtype, trusstype):
    """
    Parameters

    comprimento = comprimento da trelica
    divisao = comprimento de uma unidade fundamental
    d = diametro das barras [mm]
    E = Módulo de Young do material das barras [MPa]
    density = densidade do material das barras [kg/mm³] - eu sei, confia nas unidadas
    allowablestress = tensão máxima elástica do material [MPa]
    jointtype = tipo de junta a ser usada, 0 -> squarejoint
    trusstype = tipo de trelica a ser usada, 0 -> warrentruss / 1-> pratttruss / 2-> howetruss / 3-> crosstruss
    study = tipo de estudo, funcao que vai retornar os nos que serao pinados e as forcas no modelo id,(vetor)

    What it does

    Cria e analisa uma geometria de treliça com base no modelo escolhido e considerando o caso proposto para
    estudo. Retorna resultados da análise para o modelo escolhido

    Returns
    -------
    """
    from .geometry import generatesquarejoints, generatesupports, warrentruss, pratttruss, howetruss, crosstruss
    from .study import setstudysquare
    from .constants import TRUSS_DIMENSION

    ## basic setup

    truss = Truss(dim=TRUSS_DIMENSION)
    joints = generatesquarejoints(comprimento, divisao)
    pinados, forces = setstudysquare(joints)                                        ## forca aplicada no ponto
    supports = generatesupports(pinados, joints)                             ## quais suportes queremos pinar
    if trusstype == 0:
        members = warrentruss(joints)                                          ## barras ligando os pontos
    if trusstype == 1:
        members = pratttruss(joints)
    if trusstype == 2:
        members = howetruss(joints)
    if trusstype == 3:
        members = crosstruss(joints)

    ## geometry
    area = np.pi * d**2 / 4
    I = np.pi * d**4 / 64
    memberType = MemberType(area, E, density)

    ## setando a treliça a partir da biblioteca slientruss3d

    trussmembers = settruss(joints, supports, forces, members, truss, memberType)

    ## resolvendo e obtendo resultados via slientruss3d
    truss.Solve()
    stress = truss.GetInternalStresses()
    elementforces = truss.GetInternalForces()

    ## pos processamento dos dados
    (
    maxcompressionstress,
    maxtensionstress,
    maxcompression,
    maxtension,
    minSFtension,
    minSFcompression,
    minSFbuckling,
    ) = safetycoefanls(truss, trussmembers, stress, elementforces, allowablestress, I, E)

    return (
    maxcompressionstress,
    maxtensionstress,
    maxcompression,
    maxtension,
    minSFtension,
    minSFcompression,
    minSFbuckling,
    truss.weight
    )