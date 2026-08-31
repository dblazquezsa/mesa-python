"""Visualización interactiva de schelling_general3.py (3 poblaciones + matriz de aversión).

Uso como script standalone (abre una pestaña de navegador con play/pausa/paso):

    solara run src/visualizacion_general3.py

Uso desde una celda de Jupyter/notebook:

    import sys
    sys.path.insert(0, "src")
    from visualizacion_general3 import Page
    Page

Controles disponibles:
- Panel "Model Parameters" (n1, n2, n3, N, M, tolerancia y los 9 coeficientes
  de la matriz de aversión): cajas de texto que solo se aplican al pulsar
  "Reset", porque cualquier cambio recrea el modelo desde cero.
- Play / Step / Pause (arriba del todo): controlan la simulación en curso.
- Cuando el modelo alcanza el equilibrio se anuncia en el panel de
  información el número de pasos que hicieron falta.
"""

import textwrap

import solara

from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from mesa.visualization.utils import update_counter

from schelling_general3 import ModeloGeneral3


def agent_portrayal(agent):
    color = {1: "tab:blue", 2: "tab:red", 3: "tab:green"}.get(agent.tipo, "gray")
    return {"color": color, "size": 50}


@solara.component
def InfoComponent(model):
    """Resumen del estado actual y anuncio de equilibrio."""
    update_counter.get()  # suscribe este componente a force_update() (ver ModelController)
    if model is None:
        return solara.Markdown("## Esperando inicio del modelo...")

    if model.in_equilibrium:
        anuncio = f"<span style='color: green'>**¡Equilibrio alcanzado en {model.steps_to_equilibrium} pasos!**</span>"
    else:
        anuncio = "<span style='color: orange'>En proceso...</span>"

    filas_aversion = "\n".join(
        "        " + " | ".join(f"{model.aversion[i][j]:.1f}" for j in range(3))
        for i in range(3)
    )

    texto = textwrap.dedent(f"""\
        **Estado del Modelo**

        - **Estado:** {anuncio}
        - **Pasos dados:** {model.steps_to_equilibrium}
        - **Insatisfacción promedio:** tipo1: {model.insatisfaccion_tipo1:.3f} · tipo2: {model.insatisfaccion_tipo2:.3f} · tipo3: {model.insatisfaccion_tipo3:.3f}
        - **Proporciones de contacto:** 1-1: {model.prop_11:.3f} · 2-2: {model.prop_22:.3f} · 3-3: {model.prop_33:.3f} · 1-2: {model.prop_12:.3f} · 1-3: {model.prop_13:.3f} · 2-3: {model.prop_23:.3f}
        - **Entropía local promedio:** {model.entropia:.3f}
        - **Tolerancia actual:** {model.tolerancia}

        **Matriz de aversión actual:**
        ```
{filas_aversion}
        ```
        """)

    return solara.Card(
        title="Información del Modelo",
        children=[solara.Markdown(texto)],
    )


model_params = {
    "n1": {"type": "InputText", "value": "350", "label": "n1 (tipo 1)"},
    "n2": {"type": "InputText", "value": "350", "label": "n2 (tipo 2)"},
    "n3": {"type": "InputText", "value": "350", "label": "n3 (tipo 3)"},
    "N": {"type": "InputText", "value": "40", "label": "N (ancho de la grilla)"},
    "M": {"type": "InputText", "value": "40", "label": "M (alto de la grilla)"},
    "tolerancia": {"type": "InputText", "value": "1.0", "label": "Tolerancia"},
    "a11": {"type": "InputText", "value": "0", "label": "aversion[1][1] (auto-aversión tipo1)"},
    "a12": {"type": "InputText", "value": "1", "label": "aversion[1][2] (tipo1 hacia tipo2)"},
    "a13": {"type": "InputText", "value": "1", "label": "aversion[1][3] (tipo1 hacia tipo3)"},
    "a21": {"type": "InputText", "value": "1", "label": "aversion[2][1] (tipo2 hacia tipo1)"},
    "a22": {"type": "InputText", "value": "0", "label": "aversion[2][2] (auto-aversión tipo2)"},
    "a23": {"type": "InputText", "value": "1", "label": "aversion[2][3] (tipo2 hacia tipo3)"},
    "a31": {"type": "InputText", "value": "1", "label": "aversion[3][1] (tipo3 hacia tipo1)"},
    "a32": {"type": "InputText", "value": "1", "label": "aversion[3][2] (tipo3 hacia tipo2)"},
    "a33": {"type": "InputText", "value": "0", "label": "aversion[3][3] (auto-aversión tipo3)"},
}


def crear_modelo(n1=350, n2=350, n3=350, N=40, M=40, tolerancia="1.0",
                  a11="0", a12="1", a13="1", a21="1", a22="0", a23="1",
                  a31="1", a32="1", a33="0"):
    return ModeloGeneral3(n1, n2, n3, N, M, tolerancia=tolerancia,
                           a11=a11, a12=a12, a13=a13,
                           a21=a21, a22=a22, a23=a23,
                           a31=a31, a32=a32, a33=a33)


modelo_inicial = crear_modelo()

SpaceGraph = make_space_component(agent_portrayal)
PlotInsatisfaccion = make_plot_component(["Insatisfaccion_Tipo1", "Insatisfaccion_Tipo2", "Insatisfaccion_Tipo3"])
PlotProporciones = make_plot_component(["Prop_11", "Prop_22", "Prop_33", "Prop_12", "Prop_13", "Prop_23"])
PlotEntropia = make_plot_component("Entropia")

Page = SolaraViz(
    modelo_inicial,
    components=[SpaceGraph, PlotInsatisfaccion, PlotProporciones, PlotEntropia, InfoComponent],
    model_params=model_params,
    name="Schelling General 3 — 3 poblaciones con matriz de aversión",
)
