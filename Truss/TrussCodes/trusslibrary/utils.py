import json
from .geometry import splitnosetrusstailboom

def save_table(
        filename,
        axis1_values,
        axis2_values,
        results,
        axis1_name="axis1",
        axis2_name="axis2"):
    """
    Salva resultados paramétricos em JSON.

    Parameters
    ----------
    filename : endereço e nome do arquivo json
    axis1_values : vetor com valores do primeiro eixo (ex: geometrias de treliça)
    axis2_values : vetor com valores do segundo eixo (ex: nº divisões)
    results : dict
        deve ser acessado como:
        results[(axis1, axis2)] = {
            'SF_buckling': ...,
            'SF_compression': ...,
            'SF_tension': ...,
            'mass': ...
        }
    axis1_name / axis2_name : nomes descritivos dos eixos
    """

    table = {
        "axes": {
            axis1_name: list(axis1_values),
            axis2_name: list(axis2_values)
        },
        "data": {}
    }

    for a1 in axis1_values:
        table["data"][str(a1)] = {}

        for a2 in axis2_values:
            key = (a1, a2)

            if key in results:
                table["data"][str(a1)][str(a2)] = results[key]

    with open(filename, "w") as f:
        json.dump(table, f, indent=4)


def create_member_diameters_dicts(joints, members, d_nose, d_truss, d_tailboom):
    """
    Cria um dict unificado de diâmetros dos membros para visualização com diferentes espessuras.
    
    Parameters
    ----------
    joints : lista de coordenadas dos joints
    members : lista de tuplas (j0, j1) ou lista de members do setgeom
    d_nose : diâmetro dos membros do nariz (mm)
    d_truss : diâmetro dos membros da treliça principal (mm)
    d_tailboom : diâmetro dos membros do tailboom (mm)
    
    Returns
    -------
    member_diameters : dict unificado {index: diameter} que funciona para plottruss e plottrussBC
    """
    # Determinar os ranges de cada seção
    nosejoints, trussjoints, tailboomjoints = splitnosetrusstailboom(joints, case='geometry')
    nose_end = len(nosejoints)
    truss_end = nose_end + len(trussjoints)
    
    member_diameters = {}
    
    # Mapear cada membro para seu diâmetro baseado na seção
    for member_idx, (j0, j1) in enumerate(members):
        max_id = max(j0, j1)
        
        if max_id < nose_end:
            diameter = d_nose
        elif max_id < truss_end:
            diameter = d_truss
        else:
            diameter = d_tailboom
        
        member_diameters[member_idx] = diameter
    
    return member_diameters