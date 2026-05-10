import json
from .geometry import split_parts
from .geometry.fulltrusses import get_section_label
import trusslibrary as tl
import numpy as np

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

def create_member_diameters_dicts(truss, members, E):

    member_diameters = {}

    for idx, (j0, j1) in enumerate(members):
        member = truss.GetMemberFromConnect((j0, j1))
        if member is None:
            continue

        k = member.k
        L = member.length

        # recupera área real usada pelo solver
        A = k * L / E

        # converte pra diâmetro (seção circular)
        d = np.sqrt(4 * A / np.pi)

        member_diameters[idx] = d

    return member_diameters

def get_member_section(joints, j0, j1):
    s0 = joints[j0].get('sections', []) if isinstance(joints[j0], dict) else []
    s1 = joints[j1].get('sections', []) if isinstance(joints[j1], dict) else []
    all_sections = set(s0 + s1)
    if 'landinggear_tow' in all_sections: return 'landinggear_tow'
    if 'landinggear_pyr' in all_sections: return 'landinggear_pyr'
    if 'tailboom'        in all_sections: return 'tailboom'
    if 'truss'           in all_sections: return 'truss'
    if 'nose'            in all_sections: return 'nose'
    return 'truss'                                        

def get_masses(members_list, joints, truss, density, E, member_types_dict=None):
    """
    Parameters
    ----------
    members_list : lista de tuplas (j0, j1) dos membros
    joints       : mesma lista de joints passada ao settruss
    truss        : objeto treliça do slientruss3d
    density      : densidade
    E            : módulo de Young
    member_types_dict : dict de seções (opcional; se None, retorna só total)

    Returns
    -------
    dict com massas por seção e massa total, em kg
    """
    masses = {}

    for j0, j1 in members_list:
        member = truss.GetMemberFromConnect((j0, j1))
        if member is None:
            continue

        A = member.k * member.length / E
        m = A * member.length * density

        label = get_section_label(j0, j1, joints, member_types_dict) or 'unknown'
        masses[label] = masses.get(label, 0.0) + m

    masses['total'] = sum(v for k, v in masses.items() if k != 'total')
    return masses

def print_global_analysis(truss, trussmembers, stress, elementforces, allowablestress,
                          member_types_dict, joints, members, E):

    I_default = member_types_dict['fuselage_1'].I
    I_dict = {label: mt.I for label, mt in member_types_dict.items()}

    results = tl.safetycoefanls(
        truss, trussmembers, stress, elementforces, allowablestress, I_default, E,
        joints=joints, members_list=members, I_dict=I_dict, member_types_dict=member_types_dict
    )

    print("\n" + "="*60)
    print("ANÁLISE GLOBAL")
    print("="*60)
    g = results['global']
    print(f"Min SF Tensão:      {g['min_SF_tension']:.4f}")
    print(f"Min SF Compressão:  {g['min_SF_compression']:.4f}")
    print(f"Min SF Buckling:    {g['min_SF_buckling']:.4f}")

    print("\n" + "="*60)
    print("ANÁLISE COMPARTIMENTALIZADA")
    print("="*60)
    for section in member_types_dict.keys():
        r = results.get(section)
        if r:
            print(f"\n{section.upper()}:")
            print(f"  Min SF Tensão:     {r['min_SF_tension']:.4f}")
            print(f"  Min SF Compressão: {r['min_SF_compression']:.4f}")
            print(f"  Min SF Buckling:   {r['min_SF_buckling']:.4f}")

def export_apdl(joints, members, member_types_dict, E_dict=None, density_dict=None,
                forces=None, supports=None, filepath='truss.dat'):
    """
    Exporta a treliça para um script ANSYS APDL (.dat) pronto para rodar.

    Parameters
    ----------
    joints           : lista de joints
    members          : lista de tuplas (j0, j1)
    member_types_dict: dict {label: mt} com mt.d, mt.I etc
    E_dict           : dict {label: E} — se None usa mt.E se disponível
    density_dict     : dict {label: density} — se None usa mt.density se disponível
    forces           : lista de tuplas (joint_id, [Fx, Fy, Fz]) ou None
    supports         : lista de tuplas (joint_id, [ux, uy, uz]) onde 1=fixo, 0=livre, ou None
    filepath         : caminho do arquivo de saída
    """

    coords = [j['coords'] if isinstance(j, dict) else j for j in joints]

    # ── seções únicas e suas áreas ─────────────────────────────────────────
    section_labels = list(member_types_dict.keys())
    section_index  = {label: idx + 1 for idx, label in enumerate(section_labels)}

    # ── classifica cada membro ─────────────────────────────────────────────
    member_sections = []
    for i, j in members:
        label = get_section_label(i, j, joints, member_types_dict) or section_labels[0]
        member_sections.append(label)

    lines = []
    w = lines.append  # alias para não repetir lines.append

    w("! ============================================================")
    w("! TRELIÇA — GERADO AUTOMATICAMENTE POR export_apdl()")
    w("! ============================================================")
    w("/PREP7")
    w("")

    # ── materiais (um por seção para permitir E diferentes) ───────────────
    w("! --- MATERIAIS ---")
    for idx, label in enumerate(section_labels, start=1):
        mt = member_types_dict[label]
        E       = (E_dict or {}).get(label, getattr(mt, 'E', 210000))
        density = (density_dict or {}).get(label, getattr(mt, 'density', 1.5e-6))
        w(f"! {label}")
        w(f"MP,EX,  {idx}, {E}")
        w(f"MP,DENS,{idx}, {density}")
        w(f"MP,NUXY,{idx}, 0.3")
        w("")

    # ── tipo de elemento ───────────────────────────────────────────────────
    w("! --- ELEMENTO ---")
    w("ET,1,LINK180")
    w("KEYOPT,1,3,0  ! sem rigidez inicial (compressão permitida)")
    w("")

    # ── seções transversais ────────────────────────────────────────────────
    w("! --- SEÇÕES TRANSVERSAIS ---")
    for label in section_labels:
        mt   = member_types_dict[label]
        area = getattr(mt, 'area', None) or (3.14159 * getattr(mt, 'd', 0)**2 / 4)
        idx  = section_index[label]
        w(f"! {label}  d={getattr(mt, 'd', '?')}  A={area:.4f} mm²")
        w(f"SECTYPE,{idx},LINK")
        w(f"SECDATA,{area:.6f}")
        w("")

    # ── nós ────────────────────────────────────────────────────────────────
    w("! --- NÓS ---")
    for idx, c in enumerate(coords, start=1):
        w(f"N,{idx:>5}, {c[0]:>12.4f}, {c[1]:>12.4f}, {c[2]:>12.4f}")
    w("")

    # ── elementos ─────────────────────────────────────────────────────────
    w("! --- ELEMENTOS ---")
    for mid, ((i, j), label) in enumerate(zip(members, member_sections), start=1):
        mat_idx = section_index[label]
        sec_idx = section_index[label]
        w(f"TYPE,1  $  MAT,{mat_idx}  $  SECNUM,{sec_idx}")
        w(f"E,{i+1},{j+1}  ! {label}")
    w("")

    # ── condições de contorno ──────────────────────────────────────────────
    if supports:
        w("! --- APOIOS ---")
        for joint_id, dofs in supports:
            nid = joint_id + 1
            labels_dof = ['UX', 'UY', 'UZ']
            for dof_label, val in zip(labels_dof, dofs):
                if val == 1:
                    w(f"D,{nid},{dof_label},0")
        w("")

    # ── forças ────────────────────────────────────────────────────────────
    if forces:
        w("! --- FORÇAS EXTERNAS ---")
        dof_map = ['FX', 'FY', 'FZ']
        for joint_id, fvec in forces:
            nid = joint_id + 1
            for dof_label, val in zip(dof_map, fvec):
                if val != 0:
                    w(f"F,{nid},{dof_label},{val:.4f}")
        w("")

    # ── solução estática ───────────────────────────────────────────────────
    w("! --- SOLUÇÃO ---")
    w("FINISH")
    w("/SOLU")
    w("ANTYPE,STATIC")
    w("PSTRES,ON      ! ativa tensão de pré-carga para buckling posterior")
    w("SOLVE")
    w("FINISH")
    w("")

    # ── pós-processamento básico ───────────────────────────────────────────
    w("! --- PÓS-PROCESSAMENTO ---")
    w("/POST1")
    w("SET,LAST")
    w("PRNSOL,U,COMP  ! deslocamentos nodais")
    w("PRETAB,MFORX   ! força axial por elemento")
    w("PRETAB,SMISC,1 ! tensão axial por elemento")
    w("FINISH")
    w("")

    # ── análise modal (livre-livre) ────────────────────────────────────────
    w("! ============================================================")
    w("! ANÁLISE MODAL — livre-livre (descomentar para rodar)")
    w("! ============================================================")
    w("!/SOLU")
    w("!ANTYPE,MODAL")
    w("!MODOPT,LANB,20   ! 20 modos, método Lanczos")
    w("!MXPAND,20,,,YES  ! expande com cálculo de tensões")
    w("!SOLVE")
    w("!FINISH")
    w("!/POST1")
    w("!SET,LIST         ! lista frequências")
    w("!FINISH")
    w("")

    # ── buckling (descomentar após estático) ───────────────────────────────
    w("! ============================================================")
    w("! BUCKLING EIGENVALUE — (descomentar para rodar após estático)")
    w("! ============================================================")
    w("!/SOLU")
    w("!ANTYPE,BUCKLE")
    w("!BUCOPT,LANB,10   ! 10 autovalores")
    w("!SOLVE")
    w("!FINISH")
    w("!/POST1")
    w("!SET,LIST")
    w("!FINISH")

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    print(f"APDL exportado: {filepath}")
    print(f"  {len(coords)} nós | {len(members)} elementos | {len(section_labels)} seções")


def print_material_lengths(members_list, joints, truss, member_types_dict, E):
    """
    Printa o comprimento total necessário de cada diâmetro na treliça.
    """
    lengths = {}

    for j0, j1 in members_list:
        member = truss.GetMemberFromConnect((j0, j1))
        if member is None:
            continue

        label = get_section_label(j0, j1, joints, member_types_dict) or 'unknown'
        mt = member_types_dict.get(label)
        d = getattr(mt, 'd', '?') if mt else '?'
        key = (label, d)
        lengths[key] = lengths.get(key, 0.0) + member.length

    print("\n" + "="*50)
    print("COMPRIMENTO TOTAL POR SEÇÃO")
    print("="*50)
    print(f"{'Seção':<15} {'Diâmetro (mm)':>14} {'Comprimento (mm)':>17} {'Comprimento (m)':>16}")
    print("-"*50)
    for (label, d), total_L in sorted(lengths.items()):
        d_str = f"{d:.2f}" if isinstance(d, float) else str(d)
        print(f"{label:<15} {d_str:>14} {total_L:>17.1f} {total_L/1000:>16.3f}")
    print("-"*50)
    total = sum(lengths.values())
    print(f"{'TOTAL':<15} {'':>14} {total:>17.1f} {total/1000:>16.3f}")

def export_spaceclaim(joints, members, member_types_dict, filepath='truss_spaceclaim.py'):
    coords = [j['coords'] if isinstance(j, dict) else j for j in joints]

    from collections import defaultdict
    section_members = defaultdict(list)
    member_sections = []
    for i, j in members:
        label = get_section_label(i, j, joints, member_types_dict) or list(member_types_dict.keys())[0]
        section_members[label].append((i, j))
        member_sections.append(label)

    lines = []
    w = lines.append

    w("# ============================================================")
    w("# TRELIÇA — GERADO AUTOMATICAMENTE POR export_spaceclaim()")
    w("# ============================================================")
    w("from SpaceClaim.Api.V252.Scripting.Helpers.Units import MM")
    w("from SpaceClaim.Api.V252.Scripting.Helpers.DocumentHelper import GetRootPart")
    w("from SpaceClaim.Api.V252.Scripting.Commands import BeamProfile")
    w("from SpaceClaim.Api.V252.Scripting.Commands import Beam")
    w("from SpaceClaim.Api.V252.Scripting.Commands.CommandResults import BeamResult")
    w("from SpaceClaim.Api.V252 import DesignCurve")
    w("from SpaceClaim.Api.V252.Geometry import Point, CurveSegment, CircleProfile, Plane, PointUV")
    w("from SpaceClaim.Api.V252.Scripting.Selection import CurveSelection")
    w("")
    w("root = GetRootPart()")
    w("doc  = root.Document")
    w("")

    # ── perfis por seção ──────────────────────────────────────────────────
    w("# --- PERFIS ---")
    for label in section_members.keys():
        mt = member_types_dict.get(label)
        d  = getattr(mt, 'd', 0)
        r  = d / 2
        w(f"# {label} — d={d:.2f} mm")
        w(f"profile_result_{label} = BeamProfile.Create(doc, '{label}_d{d:.2f}', MM({r:.4f}), MM({r:.4f}))")
        w(f"profile_part_{label} = profile_result_{label}.BeamProfilePart")
        w("")

    # ── curvas e beams por seção ──────────────────────────────────────────
    w("# --- MEMBROS ---")
    for label, mlist in section_members.items():
        mt = member_types_dict.get(label)
        d  = getattr(mt, 'd', 0)
        w(f"# {label} — d={d:.2f} mm  ({len(mlist)} membros)")
        for i, j in mlist:
            x0, y0, z0 = coords[i]
            x1, y1, z1 = coords[j]
            w(f"seg   = CurveSegment.Create(Point.Create(MM({x0:.4f}), MM({y0:.4f}), MM({z0:.4f})), Point.Create(MM({x1:.4f}), MM({y1:.4f}), MM({z1:.4f})))")
            w(f"curve = DesignCurve.Create(root, seg)")
            w(f"sel   = CurveSelection.Create(curve)")
            w(f"Beam.Create(profile_part_{label}, sel)")
        w("")

    w("# Fit view")
    w("ViewHelper.ZoomToFit()")
    w("print('Treliça carregada com sucesso.')")

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    print(f"SpaceClaim script exportado: {filepath}")
    print(f"  {len(coords)} pontos | {len(members)} membros | {len(section_members)} seções")