import os
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import pandas as pd
import numpy as np
from io import BytesIO
import base64

from string_api import enriquecer_par #Función para enriquecer la información de un par de proteínas usando STRING y el diccionario de conocimiento biológico
 
# ══════════════════════════════════════════════════════
#  FUNCIONES PARA EXPORTAR GRÁFICOS
# ══════════════════════════════════════════════════════
from io import BytesIO
import base64

def descargar_png(fig, nombre_archivo):
    """Botón para descargar como PNG"""
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight", facecolor="#0d1117")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:image/png;base64,{img_base64}" download="{nombre_archivo}.png" style="text-decoration:none; margin-right:15px">📸 Descargar PNG</a>'

def descargar_pdf(fig, nombre_archivo):
    """Botón para descargar como PDF"""
    buffer = BytesIO()
    fig.savefig(buffer, format="pdf", bbox_inches="tight", facecolor="#0d1117")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:application/pdf;base64,{img_base64}" download="{nombre_archivo}.pdf" style="text-decoration:none">📑 Descargar PDF</a>'

def botones_exportacion(fig, nombre_base):
    """Muestra botones para exportar en PNG y PDF"""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(descargar_png(fig, nombre_base), unsafe_allow_html=True)
    with col2:
        st.markdown(descargar_pdf(fig, nombre_base), unsafe_allow_html=True)



# ══════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="PPI Network Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
#  CSS PERSONALIZADO
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Fondo general */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 50%, #0a0e1a 100%);
    color: #e0e6f0;
}

/* Header principal */
.main-header {
    background: linear-gradient(90deg, #0d1117, #1a1f35, #0d1117);
    border-bottom: 1px solid #1e3a5f;
    padding: 1.5rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    text-align: center;
}
.main-header h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    color: #64b5f6;
    letter-spacing: 0.1em;
    margin: 0;
    text-shadow: 0 0 30px rgba(100, 181, 246, 0.3);
}
.main-header p {
    color: #546e7a;
    font-size: 0.85rem;
    margin: 0.3rem 0 0 0;
    letter-spacing: 0.05em;
}

/* Métricas */
.metric-card {
    background: linear-gradient(135deg, #111827, #1a2035);
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}
.metric-card .value {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #64b5f6;
}
.metric-card .label {
    font-size: 0.72rem;
    color: #546e7a;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* Sección info de arista */
.edge-info {
    background: linear-gradient(135deg, #0f1923, #131d2e);
    border: 1px solid #1e3a5f;
    border-left: 3px solid #64b5f6;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}
.edge-info h4 {
    color: #64b5f6;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    margin: 0 0 0.4rem 0;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.edge-info p {
    color: #90a4ae;
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.6;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e1a 0%, #0d1117 100%);
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] p {
    color: #90a4ae !important;
    font-size: 0.82rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1117;
    border-bottom: 1px solid #1e3a5f;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #546e7a;
    letter-spacing: 0.05em;
    padding: 0.6rem 1.2rem;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #64b5f6 !important;
    border-bottom: 2px solid #64b5f6 !important;
    background: transparent !important;
}

/* Dataframe */
.stDataFrame {
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    overflow: hidden;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid #1e3a5f;
    margin: 1.5rem 0;
}

/* Badge de tipo */
.type-badge {
    display: inline-block;
    background: #1a2035;
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    color: #64b5f6;
    letter-spacing: 0.05em;
}

/* Predicción card */
.pred-card {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.pred-score {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  DATOS BIOLÓGICOS
# ══════════════════════════════════════════════════════
CONOCIMIENTO_BIOLOGICO = {
    frozenset({"TP53", "MDM2"}): {"funcion": "Regulación negativa de TP53 vía ubiquitinación", "mecanismo": "MDM2 se une al dominio N-terminal de TP53 e induce su degradación proteasomal. Es el principal regulador negativo de TP53.", "cancer": "La amplificación de MDM2 en ~7% de tumores inactiva TP53 sin mutarlo. Blanco terapéutico de inhibidores Nutlin.", "tipo": "Inhibición / Degradación"},
    frozenset({"TP53", "ATM"}): {"funcion": "Activación de TP53 ante daño en el ADN", "mecanismo": "ATM fosforila a TP53 en Ser15 y Ser20, impidiendo que MDM2 lo degrade. Activa el punto de control del ciclo celular.", "cancer": "Mutaciones en ATM predisponen a leucemia linfocítica crónica y cáncer de mama. Eje central en respuesta a radioterapia.", "tipo": "Fosforilación / Activación"},
    frozenset({"TP53", "EP300"}): {"funcion": "Activación transcripcional de genes supresores de tumor", "mecanismo": "EP300 acetila a TP53 en Lys382, aumentando su afinidad por el ADN y potenciando la transcripción de p21, PUMA y BAX.", "cancer": "EP300 mutado en ~6% de cánceres colorectales. La acetilación de TP53 es clave para la apoptosis inducida por quimioterapia.", "tipo": "Acetilación / Activación transcripcional"},
    frozenset({"TP53", "CREBBP"}): {"funcion": "Co-activación transcripcional de TP53", "mecanismo": "CREBBP (CBP) acetila TP53 y actúa como puente entre TP53 y la maquinaria transcripcional basal.", "cancer": "Mutaciones en CREBBP frecuentes en linfomas. Coopera con EP300 en la respuesta apoptótica mediada por TP53.", "tipo": "Acetilación / Co-activación"},
    frozenset({"EP300", "CREBBP"}): {"funcion": "Complejo de co-activadores transcripcionales", "mecanismo": "EP300 y CREBBP son parálogos que forman complejos y comparten sustratos de acetilación, incluyendo histonas y TP53.", "cancer": "Su inactivación conjunta elimina la respuesta apoptótica de TP53 y favorece la progresión tumoral.", "tipo": "Interacción de complejo / Cooperación funcional"},
    frozenset({"TP53", "DAXX"}): {"funcion": "Regulación de la estabilidad y localización de TP53", "mecanismo": "DAXX interactúa con TP53 en el núcleo y puede modular su actividad transcripcional y su resistencia a la degradación por MDM2.", "cancer": "DAXX mutado en ~25% de tumores pancreáticos neuroendocrinos. Su pérdida altera la respuesta de TP53 al estrés.", "tipo": "Regulación de estabilidad"},
    frozenset({"MDM2", "ATM"}): {"funcion": "Inhibición de MDM2 ante daño en el ADN", "mecanismo": "ATM fosforila a MDM2 en Ser395, bloqueando su capacidad de exportar TP53 al citoplasma para su degradación.", "cancer": "Este eje es la razón por la que las células con ATM funcional pueden estabilizar TP53 tras quimioterapia.", "tipo": "Fosforilación inhibitoria"},
    frozenset({"TP53", "SIRT1"}): {"funcion": "Desacetilación y represión de TP53", "mecanismo": "SIRT1 desacetila a TP53 en Lys382 (opuesto a EP300), reduciendo su actividad transcripcional y favoreciendo la supervivencia celular.", "cancer": "SIRT1 sobreexpresado en varios cánceres como mecanismo de escape a la apoptosis mediada por TP53.", "tipo": "Desacetilación / Represión"},
    frozenset({"TP53", "RPA1"}): {"funcion": "Coordinación de reparación de ADN con respuesta de TP53", "mecanismo": "RPA1 (subunidad de RPA) se une a TP53 durante la reparación por escisión de nucleótidos. TP53 estimula la actividad de RPA.", "cancer": "Vínculo entre la detección del daño y la activación del punto de control. Relevante en resistencia a cisplatino.", "tipo": "Cooperación en reparación de ADN"},
    frozenset({"TP53", "HSP90AA1"}): {"funcion": "Estabilización de TP53 mutante por chaperona", "mecanismo": "HSP90 se une preferentemente a formas mutantes de TP53, impidiendo su degradación y acumulando proteína disfuncional en el tumor.", "cancer": "Mecanismo por el que TP53 mutante se acumula en tumores. Inhibidores de HSP90 (geldanamicina) reactivarían la vía.", "tipo": "Chaperoneo / Estabilización patológica"},
    frozenset({"TP53", "SFN"}): {"funcion": "Secuestro citoplasmático de TP53 fosforilado", "mecanismo": "SFN (14-3-3σ) retiene a TP53 fosforilado en el citoplasma, regulando su localización nuclear y actividad transcripcional.", "cancer": "SFN es a su vez diana transcripcional de TP53, formando un bucle de retroalimentación en el arresto del ciclo celular G2/M.", "tipo": "Retención citoplasmática / Regulación de localización"},
    frozenset({"TP53", "TP53BP2"}): {"funcion": "Potenciación de la actividad apoptótica de TP53", "mecanismo": "TP53BP2 (ASPP2) se une al dominio de unión al ADN de TP53 y dirige su actividad hacia promotores pro-apoptóticos (BAX, PIG3).", "cancer": "ASPP2 frecuentemente inactivado en tumores, permitiendo que TP53 active genes de arresto pero no de apoptosis.", "tipo": "Co-activación apoptótica"},
    frozenset({"BRCA1", "BARD1"}): {"funcion": "Formación del complejo E3 ubiquitina ligasa BRCA1/BARD1", "mecanismo": "BRCA1 y BARD1 heterodimeriza a través de sus dominios RING. El complejo tiene actividad E3 ligasa esencial para la HR.", "cancer": "Mutaciones en BRCA1 que disrumpen esta interacción causan cáncer de mama/ovario hereditario (síndrome HBOC).", "tipo": "Heterodimerización RING / Ubiquitina ligasa"},
    frozenset({"BRCA1", "PALB2"}): {"funcion": "Reclutamiento de BRCA2 al sitio de daño en el ADN", "mecanismo": "PALB2 actúa como adaptador molecular entre BRCA1 y BRCA2, permitiendo el ensamblaje del complejo de recombinación homóloga.", "cancer": "Mutaciones en PALB2 confieren riesgo de cáncer de mama similar a BRCA2. Gen de susceptibilidad de alta penetrancia.", "tipo": "Adaptador molecular / Ensamblaje de complejo"},
    frozenset({"BRCA1", "ATM"}): {"funcion": "Activación de BRCA1 tras detección de doble cadena rota", "mecanismo": "ATM fosforila a BRCA1 en Ser1387 y Ser1423 en respuesta a DSB. Esto recluta a BRCA1 a los focos de reparación.", "cancer": "Eje crítico en respuesta a radioterapia e inhibidores de PARP. Tumores BRCA1-mutantes son sensibles a inhibidores de PARP.", "tipo": "Fosforilación / Reclutamiento a DSB"},
    frozenset({"BRCA1", "MRE11"}): {"funcion": "Inicio de la resección del ADN en recombinación homóloga", "mecanismo": "MRE11 (parte del complejo MRN) inicia la resección 5'→3' del ADN en las roturas. BRCA1 coordina esta actividad nucleasa.", "cancer": "Defectos en MRE11 causan ataxia-telangiectasia-like disorder. La resección defectuosa bloquea la HR.", "tipo": "Coordinación de resección de ADN"},
    frozenset({"BRCA1", "BRIP1"}): {"funcion": "Desenrollamiento del ADN en reparación por HR", "mecanismo": "BRIP1 (BACH1/FANCJ) es una helicasa que interactúa con el dominio BRCT de BRCA1. Desenrolla estructuras secundarias del ADN.", "cancer": "Mutaciones en BRIP1 asociadas a cáncer de mama y ovario. También implicado en la vía de Fanconi.", "tipo": "Interacción BRCT / Actividad helicasa"},
    frozenset({"ATM", "MRE11"}): {"funcion": "Detección inicial de roturas de doble cadena (DSB)", "mecanismo": "El complejo MRN (MRE11-RAD50-NBS1) detecta DSB y recluta/activa ATM. MRE11 activa a ATM mediante un mecanismo alostérico.", "cancer": "Primer paso en la cascada de señalización de daño al ADN. Defectos aquí impiden toda respuesta a DSB.", "tipo": "Sensor de DSB / Activación de quinasa"},
    frozenset({"BRCA1", "FANCD2"}): {"funcion": "Coordinación entre la vía FA y la reparación por HR", "mecanismo": "FANCD2 monoubiquitinado se localiza en focos de daño junto a BRCA1. BRCA1 promueve la monoubiquitinación de FANCD2.", "cancer": "Anemia de Fanconi causada por mutaciones bialélicas en FANCD2. Tumores FA-deficientes hipersensibles a agentes entrecruzadores.", "tipo": "Monoubiquitinación / Coordinación de vías de reparación"},
    frozenset({"BRCA1", "TOPBP1"}): {"funcion": "Activación del punto de control S-phase y G2/M", "mecanismo": "TOPBP1 activa a ATR, que a su vez fosforila a CHK1. BRCA1 interactúa con TOPBP1 para coordinar la respuesta al estrés replicativo.", "cancer": "Eje BRCA1-TOPBP1-ATR activo en células con oncogenes activados. Su pérdida permite replicación con ADN dañado.", "tipo": "Punto de control de replicación"},
    frozenset({"BRCA1", "TP53"}): {"funcion": "Cooperación en supresión tumoral y respuesta a daño", "mecanismo": "BRCA1 potencia la actividad transcripcional de TP53 sobre genes como p21 y GADD45. Ambas proteínas se co-localizan en focos de daño.", "cancer": "Mutaciones en BRCA1 y TP53 frecuentemente coexisten en tumores triple-negativo de mama, el subtipo más agresivo.", "tipo": "Co-activación transcripcional / Supresión tumoral"},
    frozenset({"EGFR", "EGF"}): {"funcion": "Activación del receptor por su ligando canónico", "mecanismo": "EGF se une al dominio extracelular de EGFR, induciendo dimerización del receptor y autofosforilación en tirosinas intracelulares.", "cancer": "Sobreexpresión de EGFR en ~30% de cánceres epiteliales. Diana de cetuximab y erlotinib/gefitinib (TKIs).", "tipo": "Ligando-receptor / Activación por dimerización"},
    frozenset({"EGFR", "ERBB2"}): {"funcion": "Heterodimerización que amplifica la señal de EGFR", "mecanismo": "ERBB2 (HER2) es el socio de dimerización preferido de EGFR. El heterodímero EGFR/ERBB2 genera señales más potentes y prolongadas.", "cancer": "HER2 amplificado en ~20% de cánceres de mama. Diana de trastuzumab (Herceptin) y pertuzumab.", "tipo": "Heterodimerización / Amplificación de señal"},
    frozenset({"EGFR", "ERBB3"}): {"funcion": "Heterodimerización y activación de la vía PI3K/AKT", "mecanismo": "ERBB3 carece de actividad quinasa propia pero tiene múltiples sitios de unión a PI3K. El heterodímero EGFR/ERBB3 es el activador más potente de PI3K/AKT.", "cancer": "Mecanismo de resistencia a inhibidores de EGFR: las células upregular ERBB3 para mantener la señal de supervivencia.", "tipo": "Heterodimerización / Activación de PI3K"},
    frozenset({"ERBB2", "ERBB3"}): {"funcion": "Heterodímero más oncogénico de la familia ERBB", "mecanismo": "El par ERBB2/ERBB3 es considerado el heterodímero más potente de la familia. ERBB2 amplifica la señal quinasa; ERBB3 recluta PI3K.", "cancer": "Sobreactivación en cánceres de mama HER2+. Pertuzumab bloquea específicamente esta dimerización.", "tipo": "Heterodimerización oncogénica"},
    frozenset({"EGFR", "CBL"}): {"funcion": "Ubiquitinación y degradación de EGFR activado", "mecanismo": "CBL es una E3 ubiquitina ligasa que se une a EGFR fosforilado en Y1045 y lo poliubiquitina, dirigiéndolo a degradación lisosomal.", "cancer": "CBL actúa como supresor tumoral. Mutaciones en CBL impiden la degradación de EGFR, prolongando la señal proliferativa.", "tipo": "Ubiquitinación / Terminación de señal"},
    frozenset({"EGFR", "PIK3CA"}): {"funcion": "Activación directa de la vía PI3K/AKT/mTOR", "mecanismo": "EGFR fosforilado recluta la subunidad p85 de PI3K (que contiene PIK3CA como subunidad catalítica p110α), activando AKT y mTOR.", "cancer": "PIK3CA mutado en ~30% de cánceres de mama. La activación constitutiva confiere resistencia a inhibidores de EGFR.", "tipo": "Reclutamiento / Activación de supervivencia celular"},
    frozenset({"EGFR", "GAB1"}): {"funcion": "Amplificación de señales de EGFR vía proteína scaffolding", "mecanismo": "GAB1 es una proteína adaptadora que se une a EGFR fosforilado y amplifica las señales hacia RAS/MAPK y PI3K/AKT.", "cancer": "GAB1 sobreexpresado en glioblastoma. Amplifica oncogénicamente las cascadas downstream de EGFR.", "tipo": "Scaffolding / Amplificación de cascadas"},
    frozenset({"EGFR", "HBEGF"}): {"funcion": "Activación de EGFR por ligando alternativo HB-EGF", "mecanismo": "HB-EGF activa EGFR y ERBB4 con alta afinidad. Se libera por proteólisis de su forma transmembrana (shedding).", "cancer": "HB-EGF elevado en cáncer de ovario y glioblastoma. Mecanismo de activación de EGFR independiente de EGF.", "tipo": "Ligando alternativo / Activación por shedding"},
    frozenset({"EGFR", "EREG"}): {"funcion": "Activación de EGFR por epiregulina con menor afinidad", "mecanismo": "EREG (epiregulina) activa EGFR y ERBB4 con menor afinidad que EGF, generando señales más sostenidas.", "cancer": "Alta expresión de EREG en cáncer colorectal predice respuesta a cetuximab. Biomarcador de sensibilidad a anti-EGFR.", "tipo": "Ligando de baja afinidad / Señal sostenida"},
    frozenset({"EGFR", "DCN"}): {"funcion": "Inhibición del receptor EGFR por decorina", "mecanismo": "DCN (decorina) es un proteoglicano de la matriz extracelular que se une directamente al dominio extracelular de EGFR e inhibe su activación.", "cancer": "DCN suprime tumores in vivo al bloquear EGFR. Su pérdida en el estroma tumoral permite la sobreactivación de EGFR.", "tipo": "Inhibición por proteoglicano extracelular"},
    frozenset({"EGFR", "CDH1"}): {"funcion": "Regulación cruzada entre adhesión celular y proliferación", "mecanismo": "CDH1 (E-cadherina) secuestra β-catenina en la membrana. EGFR activado puede fosforilar CDH1 y disolver las uniones adherentes.", "cancer": "La pérdida de CDH1 es un sello de tumores invasivos. EGFR activo + CDH1 perdida = máxima capacidad metastásica.", "tipo": "Regulación de EMT / Adhesión-proliferación"},
} # Clave: par de proteínas (orden no importa) -> Valor: dict con función, mecanismo, relevancia en cáncer y tipo de interacción

COLORES_TIPO = {
    "Fosforilación / Activación": "#FFE600",
    "Fosforilación inhibitoria": "#FF8C00",
    "Inhibición / Degradación": "#E24B4A",
    "Regulación negativa de TP53 vía ubiquitinación": "#E24B4A",
    "Ubiquitinación / Terminación de señal": "#E24B4A",
    "Heterodimerización RING / Ubiquitina ligasa": "#E24B4A",
    "Acetilación / Activación transcripcional": "#00CED1",
    "Acetilación / Co-activación": "#00CED1",
    "Desacetilación / Represión": "#DA70D6",
    "Co-activación transcripcional / Supresión tumoral": "#00CED1",
    "Co-activación apoptótica": "#00CED1",
    "Interacción de complejo / Cooperación funcional": "#4FC3F7",
    "Adaptador molecular / Ensamblaje de complejo": "#4FC3F7",
    "Scaffolding / Amplificación de cascadas": "#4FC3F7",
    "Sensor de DSB / Activación de quinasa": "#FFD700",
    "Coordinación de resección de ADN": "#FF8C00",
    "Monoubiquitinación / Coordinación de vías de reparación": "#FF8C00",
    "Punto de control de replicación": "#FF8C00",
    "Cooperación en reparación de ADN": "#FF8C00",
    "Interacción BRCT / Actividad helicasa": "#FF8C00",
    "Fosforilación / Reclutamiento a DSB": "#FFD700",
    "Ligando-receptor / Activación por dimerización": "#69F0AE",
    "Heterodimerización / Amplificación de señal": "#69F0AE",
    "Heterodimerización / Activación de PI3K": "#69F0AE",
    "Heterodimerización oncogénica": "#69F0AE",
    "Ligando alternativo / Activación por shedding": "#69F0AE",
    "Ligando de baja afinidad / Señal sostenida": "#D2F1C1",
    "Reclutamiento / Activación de supervivencia celular": "#4FC3F7",
    "Inhibición por proteoglicano extracelular": "#DA70D6",
    "Regulación de EMT / Adhesión-proliferación": "#DA70D6",
    "Chaperoneo / Estabilización patológica": "#A8A8A8",
    "Retención citoplasmática / Regulación de localización": "#A8A8A8",
    "Regulación de estabilidad": "#A8A8A8",
    "Desconocido": "#555555",
}

def color_arista(tipo):
    return COLORES_TIPO.get(tipo, "#555555")

# ══════════════════════════════════════════════════════
#  CARGA DE DATOS
# ══════════════════════════════════════════════════════
CARPETA = os.path.dirname(os.path.abspath(__file__))


# Información de las redes disponibles: nombre, archivo CSV, hub central y color para visualización
REDES_INFO = {
    "🔴  Red TP53":  {"archivo": "red_tp53.csv",  "hub": "TP53",  "color": "#E24B4A"},
    "🔵  Red BRCA1": {"archivo": "red_brca1.csv", "hub": "BRCA1", "color": "#378ADD"},
    "🟢  Red EGFR":  {"archivo": "red_egfr.csv",  "hub": "EGFR",  "color": "#1D9E75"},
}

@st.cache_data
def cargar_grafo(nombre_csv, nombre_red):
    ruta = os.path.join(CARPETA, nombre_csv)
    if not os.path.exists(ruta):
        return None
    df = pd.read_csv(ruta)
    df["par"] = df.apply(lambda r: tuple(sorted([r["proteina_a"], r["proteina_b"]])), axis=1)
    df = df.drop_duplicates(subset="par").drop(columns="par")
    G = nx.Graph(name=nombre_red)
    for _, fila in df.iterrows():
        clave = frozenset({fila["proteina_a"], fila["proteina_b"]})
        bio = CONOCIMIENTO_BIOLOGICO.get(clave, {})
        G.add_edge(
            fila["proteina_a"], fila["proteina_b"],
            evidencia_experimental=fila["evidencia_exp"],
            base_datos=fila["base_datos"],
            mineria_texto=fila["mineria_texto"],
            score=fila["score"],
            weight=fila["score"],
            funcion=bio.get("funcion", "No anotada"),
            mecanismo=bio.get("mecanismo", "Sin descripción"),
            relevancia_cancer=bio.get("cancer", "Sin datos"),
            tipo_interaccion=bio.get("tipo", "Desconocido"),
        )
    return G

# ══════════════════════════════════════════════════════
#  FUNCIONES DE ANÁLISIS
# ══════════════════════════════════════════════════════
def calcular_centralidades(G):
    return {
        "grado":        nx.degree_centrality(G),
        "between":      nx.betweenness_centrality(G, weight="weight"),
        "close":        nx.closeness_centrality(G),
        "clustering":   nx.clustering(G, weight="weight"),
    }

def predecir_enlaces(G, top_n=5):
    no_aristas = list(nx.non_edges(G))
    if not no_aristas:
        return pd.DataFrame()
    cn   = list(nx.common_neighbor_centrality(G, no_aristas))
    jacc = list(nx.jaccard_coefficient(G, no_aristas))
    aa   = list(nx.adamic_adar_index(G, no_aristas))
    ra   = list(nx.resource_allocation_index(G, no_aristas))
    resultados = []
    for (u, v, cn_val), (_, _, j_val), (_, _, aa_val), (_, _, ra_val) in zip(cn, jacc, aa, ra):
        score = (0.25 * min(cn_val / 10, 1.0) + 0.25 * j_val +
                 0.25 * min(aa_val / 5, 1.0) + 0.25 * min(ra_val * 5, 1.0))
        resultados.append({
            "Par": f"{u} — {v}",
            "Vecinos comunes": int(cn_val),
            "Jaccard": round(j_val, 4),
            "Adamic-Adar": round(aa_val, 4),
            "Resource Alloc.": round(ra_val, 4),
            "Score Ensemble": round(score, 4),
        })
    return pd.DataFrame(resultados).sort_values("Score Ensemble", ascending=False).head(top_n)

def graficar_red(G, hub, color_red, centralidades):
    fig, ax = plt.subplots(figsize=(9, 7), facecolor="#0d1117")
    ax.set_facecolor("#13171f") # color de fondo oscuro para resaltar los nodos y aristas, con contraste suficiente para la paleta de colores elegida.
# 
    pos = nx.spring_layout(G, seed=42, k=2.8)
    grado_c = centralidades["grado"]

    node_sizes  = [1200 + grado_c[n] * 3500 for n in G.nodes()]
    node_colors = []
    NODOS_PUENTE = {"ATM", "TP53"}
    for n in G.nodes():
        if n == hub:
            node_colors.append("#FFD700")
        elif n in NODOS_PUENTE and n != hub:
            node_colors.append("#FF6B6B")
        else:
            node_colors.append(color_red)

    for u, v, data in G.edges(data=True):
        tipo  = data.get("tipo_interaccion", "Desconocido")
        color = color_arista(tipo)
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v)],
                               edge_color=color, width=2.2, alpha=0.75)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=node_colors, edgecolors="#ffffff",
                           linewidths=1.0, alpha=0.95)

    for n, (x, y) in pos.items():
        ax.text(x, y, n, fontsize=7, fontweight="bold", color="white",
                ha="center", va="center", fontfamily="monospace",
                path_effects=[pe.withStroke(linewidth=2.2, foreground="#000000")])

    for u, v, data in G.edges(data=True):
        tipo = data.get("tipo_interaccion", "")
        if tipo not in ("Desconocido", "No anotada"):
            x = (pos[u][0] + pos[v][0]) / 2
            y = (pos[u][1] + pos[v][1]) / 2
            palabra = tipo.split("/")[0].strip()[:18]
            ax.text(x, y, palabra, fontsize=3.8, color="#CCCCCC",
                    ha="center", va="center", fontfamily="monospace", alpha=0.8,
                    bbox=dict(boxstyle="round,pad=0.1", fc="#111111", ec="none", alpha=0.5))

    ax.axis("off")
    fig.tight_layout(pad=0.3)
    return fig

## ══════════════════════════════════════════════════════
## GRÁFICO DE BARRAS DE CENTRALIDADES
## Muestra las centralidades de grado y intermediación para cada nodo, ordenados por grado.
## Los nodos se ordenan de mayor a menor centralidad de grado para facilitar la comparación visual.
## Cada barra representa una centralidad diferente, con colores contrastantes
## El eje x muestra los nombres de los nodos, rotados para mejor legibilidad, y el eje y muestra los valores de centralidad.

def graficar_barras(G, color_red, centralidades):
    grado_c   = centralidades["grado"]
    between_c = centralidades["between"]
    nodos  = sorted(G.nodes(), key=lambda n: grado_c[n], reverse=True)
    vals_g = [grado_c[n]   for n in nodos]
    vals_b = [between_c[n] for n in nodos]
    x = np.arange(len(nodos))

    fig, ax = plt.subplots(figsize=(9, 3.5), facecolor="#0d1117")
    ax.set_facecolor("#111827")
    ax.bar(x - 0.2, vals_g, 0.38, label="Centralidad grado", color=color_red, alpha=0.85)
    ax.bar(x + 0.2, vals_b, 0.38, label="Intermediación", color="#FFD700", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(nodos, rotation=40, ha="right", fontsize=8, color="white", fontfamily="monospace")
    ax.tick_params(colors="#546e7a")
    ax.spines[:].set_color("#1e3a5f")
    ax.set_ylabel("Centralidad", fontsize=8, color="#546e7a")
    ax.set_facecolor("#111827")
    legend = ax.legend(fontsize=8, labelcolor="white", facecolor="#0d1117", edgecolor="#1e3a5f")
    fig.tight_layout()
    return fig

# ══════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>🧬 PPI Network Explorer</h1>
    <p>Redes de interacción proteína-proteína · TP53 · BRCA1 · EGFR · Datos: STRING Database</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    red_seleccionada = st.selectbox(
        "Red proteica",
        list(REDES_INFO.keys()),
        help="Selecciona qué red PPI analizar"
    )
    info_red = REDES_INFO[red_seleccionada]

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("### 🎨 Tipos de interacción")

    leyenda = {
        "🟡 Fosforilación / Activación": "#FFD700",
        "🟠 Reparación de ADN": "#FF8C00",
        "🔴 Ubiquitinación / Degradación": "#E24B4A",
        "🔵 Acetilación / Transcripción": "#00CED1",
        "🟣 Inhibición / Represión": "#DA70D6",
        "🟢 Ligando-receptor (EGFR)": "#69F0AE",
        "💠 Complejo / Scaffolding": "#4FC3F7",
        "⚪ Chaperoneo / Localización": "#A8A8A8",
    }
    for label, _ in leyenda.items():
        st.markdown(f"<small style='color:#90a4ae'>{label}</small>", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    top_n = st.slider("Top predicciones de enlace", 3, 10, 5)
    seed_layout = st.slider("Semilla layout de red", 1, 100, 42)

# ══════════════════════════════════════════════════════
#  CARGA DEL GRAFO
# ══════════════════════════════════════════════════════
nombre_limpio = red_seleccionada.split("  ")[-1]
G = cargar_grafo(info_red["archivo"], nombre_limpio)

if G is None:
    st.error(f"⚠️ No se encontró el archivo `{info_red['archivo']}` en la carpeta del script. Asegúrate de que los CSV estén en el mismo directorio que `app.py`.")
    st.stop()

centralidades = calcular_centralidades(G)

# ══════════════════════════════════════════════════════
#  MÉTRICAS RÁPIDAS
# ══════════════════════════════════════════════════════
col1, col2, col3, col4, col5 = st.columns(5)
metricas = [
    (G.number_of_nodes(), "Proteínas"),
    (G.number_of_edges(), "Interacciones"),
    (f"{nx.density(G):.3f}", "Densidad"),
    (max(centralidades["grado"], key=centralidades["grado"].get), "Hub principal"),
    (f"{np.mean(list(centralidades['clustering'].values())):.3f}", "Clustering medio"),
] # streamlit run c:/Users/valen/Documents/UNIVERSIDAD/UNINORTE/ppi_app/app.py --server.port 8502
for col, (val, lab) in zip([col1, col2, col3, col4, col5], metricas):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{val}</div>
            <div class="label">{lab}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  TABS PRINCIPALES
# ══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🕸️  Red PPI",
    "📊  Centralidades",
    "🔮  Predicción de enlaces",
    "🔬  Detalle de interacciones",
]) # streamlit run c:/Users/valen/Documents/UNIVERSIDAD/UNINORTE/ppi_app/app.py --server.port 8502

# ─── TAB 1: RED ───────────────────────────────────────
with tab1:
    col_red, col_info = st.columns([2, 1])
# aquí se muestra la visualización de la red con formato personalizado
    with col_red:
        st.markdown(f"#### Red {nombre_limpio}")
        fig_red = graficar_red(G, info_red["hub"], info_red["color"], centralidades)
        st.pyplot(fig_red, use_container_width=True)
        
    
        botones_exportacion(fig_red, f"red_{nombre_limpio}")
        
        plt.close(fig_red)

    with col_info:
        st.markdown("#### Proteínas ordenadas por grado")
        grado_c = centralidades["grado"]
        df_nodos = pd.DataFrame([
            {"Proteína": n, "Grado": G.degree(n), "Centralidad": round(grado_c[n], 4)}
            for n in sorted(G.nodes(), key=lambda n: grado_c[n], reverse=True)
        ])
        st.dataframe(df_nodos, use_container_width=True, hide_index=True,
                     column_config={"Centralidad": st.column_config.ProgressColumn(
                         "Centralidad", min_value=0, max_value=1, format="%.4f")})

# ─── TAB 2: CENTRALIDADES ─────────────────────────────
with tab2:
    st.markdown("#### Centralidad de grado vs. Intermediación")
    fig_bar = graficar_barras(G, info_red["color"], centralidades)
    st.pyplot(fig_bar, use_container_width=True)
    
    # BOTONES DE EXPORTACIÓN
    botones_exportacion(fig_bar, f"centralidades_{nombre_limpio}")
    
    plt.close(fig_bar)
# aquí se muestra la tabla completa de centralidades con formato personalizado
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("#### Tabla completa de centralidades") 
# se ordena por centralidad de grado y se redondean los valores para mejor visualización
    df_c = pd.DataFrame({
        "Proteína":       list(G.nodes()),
        "Grado":          [G.degree(n) for n in G.nodes()],
        "C. Grado":       [round(centralidades["grado"][n], 4) for n in G.nodes()],
        "C. Intermediación": [round(centralidades["between"][n], 4) for n in G.nodes()],
        "C. Cercanía":    [round(centralidades["close"][n], 4) for n in G.nodes()],
        "Clustering":     [round(centralidades["clustering"][n], 4) for n in G.nodes()],
    }).sort_values("C. Grado", ascending=False)
    st.dataframe(df_c, use_container_width=True, hide_index=True)

# ─── TAB 3: PREDICCIÓN ────────────────────────────────
with tab3:
    st.markdown("#### 🔮 Interacciones no observadas con mayor probabilidad topológica")
    st.markdown("""
    <p style='color:#546e7a; font-size:0.82rem; margin-bottom:1rem'>
    Se combinan 4 métricas topológicas (Vecinos Comunes, Jaccard, Adamic-Adar, Resource Allocation)
    en un <em>Score Ensemble</em>. Un score alto indica que dos proteínas comparten suficiente
    contexto de red como para que una interacción directa sea plausible.
    </p>
    """, unsafe_allow_html=True)
# aquí se muestra la tabla de predicciones con formato personalizado
    df_pred = predecir_enlaces(G, top_n=top_n)
    if df_pred.empty:
        st.info("No hay pares no enlazados en esta red.")
    else:
        for _, row in df_pred.iterrows():
            score = row["Score Ensemble"]
            if score >= 0.7:
                color_score = "#69F0AE"
            elif score >= 0.4:
                color_score = "#FFD700"
            else:
                color_score = "#90a4ae"
            st.markdown(f"""
            <div class="pred-card">
                <div>
                    <span style='font-family:monospace; color:#e0e6f0; font-size:0.95rem'>{row['Par']}</span><br>
                    <span style='font-size:0.72rem; color:#546e7a'>
                        Vecinos: {row['Vecinos comunes']} &nbsp;|&nbsp;
                        Jaccard: {row['Jaccard']} &nbsp;|&nbsp;
                        A-A: {row['Adamic-Adar']} &nbsp;|&nbsp;
                        R-A: {row['Resource Alloc.']}
                    </span>
                </div>
                <div class="pred-score" style='color:{color_score}'>{score:.4f}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── TAB 4: DETALLE ───────────────────────────────────
with tab4:
    st.markdown("#### 🔬 Explorador de interacciones anotadas")
 
    # ── Cache de sesión: guarda lo consultado en STRING ───
    # Así al cambiar de par y volver, no hay que consultar de nuevo
    if "string_cache" not in st.session_state:
        st.session_state.string_cache = {}
 
    # ── Selector de interacción ───────────────────────────
    todas_aristas = list(G.edges(data=True))
    opciones_todas = [f"{u} — {v}" for u, v, _ in todas_aristas]
 
    if not opciones_todas:
        st.info("No hay interacciones en esta red.")
    else:
        seleccion = st.selectbox("Selecciona una interacción", opciones_todas)
        idx = opciones_todas.index(seleccion)
        u, v, data = todas_aristas[idx]
        clave = frozenset({u, v})
        clave_cache = f"{min(u,v)}_{max(u,v)}"
 
        # ── Determinar fuente de datos ────────────────────
        # Prioridad: cache de sesión > CONOCIMIENTO_BIOLOGICO > datos del CSV
        if clave_cache in st.session_state.string_cache:
            bio = st.session_state.string_cache[clave_cache]
            # Mezclar con data del grafo para no perder scores del CSV
            data_mostrar = {**data, **bio}
            origen = "🌐 Desde STRING (esta sesión)"
        elif clave in CONOCIMIENTO_BIOLOGICO and CONOCIMIENTO_BIOLOGICO[clave].get("tipo", "Desconocido") != "Desconocido":
            data_mostrar = data
            origen = "📚 Anotación local"
        else:
            data_mostrar = data
            origen = "📄 Solo datos CSV"
 
        # ── Header con origen y botón de consulta ─────────
        col_header, col_btn = st.columns([3, 1])
        with col_header:
            st.markdown(f"<small style='color:#546e7a'>{origen}</small>", unsafe_allow_html=True)
        with col_btn:
            consultar_string = st.button("🔍 Consultar STRING", key=f"string_{u}_{v}")
 
        # ── Consultar STRING y guardar en cache ───────────
        if consultar_string:
            with st.spinner(f"Consultando STRING para {u} ↔ {v}..."):
                bio_fresco = enriquecer_par(u, v)
            st.session_state.string_cache[clave_cache] = bio_fresco
            data_mostrar = {**data, **bio_fresco}
            origen = "🌐 Desde STRING (esta sesión)"
            st.success(f"✅ Datos actualizados desde STRING para {u} ↔ {v}")
 
        # ── Mostrar info ──────────────────────────────────
        tipo  = data_mostrar.get("tipo_interaccion") or data_mostrar.get("tipo", "Desconocido")
        color = color_arista(tipo)
 
        col_a, col_b = st.columns([1, 2])
        with col_a:
            # Score: mostrar experimental si viene de STRING, combinado si es CSV
            if clave_cache in st.session_state.string_cache:
                score_label  = "Score exp. STRING"
                score_val    = round(data_mostrar.get("escore", 0), 3)
                score_extra  = f"Combinado: {round(data_mostrar.get('score_combinado', data.get('score', 0)), 3)}"
            else:
                score_label  = "Score STRING"
                score_val    = round(data_mostrar.get("score", 0), 3)
                score_extra  = ""
 
            st.markdown(f"""
            <div class="metric-card" style='margin-bottom:0.8rem'>
                <div class="value" style='font-size:1.1rem; color:{color}'>{u}</div>
                <div class="label">Proteína A</div>
            </div>
            <div class="metric-card" style='margin-bottom:0.8rem'>
                <div class="value" style='font-size:1.1rem; color:{color}'>{v}</div>
                <div class="label">Proteína B</div>
            </div>
            <div class="metric-card">
                <div class="value" style='font-size:1rem'>{score_val}</div>
                <div class="label">{score_label}</div>
            </div>
            {"<div style='color:#546e7a; font-size:0.72rem; text-align:center; margin-top:0.4rem'>" + score_extra + "</div>" if score_extra else ""}
            """, unsafe_allow_html=True)
 
        with col_b:
            st.markdown(f"<span class='type-badge'>{tipo}</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
 
            st.markdown(f"""
            <div class="edge-info">
                <h4>🎯 Función</h4>
                <p>{data_mostrar.get("funcion", data_mostrar.get("funcion", "No anotada"))}</p>
            </div>
            <div class="edge-info">
                <h4>⚙️ Mecanismo molecular</h4>
                <p>{data_mostrar.get("mecanismo", "Sin descripción")}</p>
            </div>
            <div class="edge-info">
                <h4>🏥 Relevancia en cáncer</h4>
                <p>{data_mostrar.get("relevancia_cancer") or data_mostrar.get("cancer", "Sin datos")}</p>
            </div>
            """, unsafe_allow_html=True)
 
            ev_exp  = data_mostrar.get("evidencia_experimental", "N/A")
            mineria = data_mostrar.get("mineria_texto", "N/A")
            st.markdown(f"""
            <div style='margin-top:0.8rem; display:flex; gap:0.5rem; flex-wrap:wrap'>
                <span style='background:#1a2035; border:1px solid #1e3a5f; border-radius:4px;
                             padding:0.15rem 0.5rem; font-size:0.72rem; color:#64b5f6'>
                    Evidencia exp: {ev_exp}
                </span>
                <span style='background:#1a2035; border:1px solid #1e3a5f; border-radius:4px;
                             padding:0.15rem 0.5rem; font-size:0.72rem; color:#64b5f6'>
                    Minería texto: {mineria}
                </span>
                <span style='background:#1a2035; border:1px solid #1e3a5f; border-radius:4px;
                             padding:0.15rem 0.5rem; font-size:0.72rem; color:#64b5f6'>
                    BD: {data_mostrar.get("base_datos", "N/A")}
                </span>
            </div>
            """, unsafe_allow_html=True)
 