"""Visualización interactiva de schelling_general2.py (2 poblaciones + matriz de afinidad).

Uso como script standalone (abre una pestaña de navegador con play/pausa/paso):

    solara run src/visualizacion_general2.py

Uso desde una celda de Jupyter/notebook:

    import sys
    sys.path.insert(0, "src")
    from visualizacion_general2 import Page
    Page

Controles disponibles:
- Panel "Model Parameters" (n1, n2, N, M): solo se aplican al pulsar "Reset",
  porque cambiar poblaciones o el tamaño de la grilla implica recrear los
  agentes desde cero.
- Play / Step / Pause (arriba del todo): controlan la simulación en curso.
- Panel "Controles en caliente" (tolerancia y cada coeficiente de la matriz
  de afinidad): a diferencia de "Model Parameters", estos se aplican
  directamente sobre la simulación en marcha, sin reiniciarla — pausa,
  cambia un valor y dale a Step/Play para ver el efecto sobre la
  configuración espacial actual.
- Cuando el modelo alcanza el equilibrio se anuncia en el panel de
  información el número de pasos que hicieron falta.
"""

import textwrap

import solara

from mesa.visualization import SolaraViz, Slider, make_space_component, make_plot_component
from mesa.visualization.utils import update_counter

from schelling_general2 import ModeloGeneral2


def agent_portrayal(agent):
    color = {1: "tab:blue", 2: "tab:red"}.get(agent.tipo, "gray")
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

    texto = textwrap.dedent(f"""\
        **Estado del Modelo**

        - **Estado:** {anuncio}
        - **Pasos dados:** {model.steps_to_equilibrium}
        - **Insatisfacción promedio tipo 1:** {model.insatisfaccion_tipo1:.3f}
        - **Insatisfacción promedio tipo 2:** {model.insatisfaccion_tipo2:.3f}
        - **Proporciones de contacto:** 1-1: {model.prop_11:.3f} · 2-2: {model.prop_22:.3f} · 1-2: {model.prop_12:.3f}
        - **Entropía local promedio:** {model.entropia:.3f}
        - **Tolerancia actual:** {model.tolerancia}
        - **Matriz de afinidad actual:** {model.afinidad}
        """)

    return solara.Card(
        title="Información del Modelo",
        children=[solara.Markdown(texto)],
    )


@solara.component
def ControlesEnCaliente(model):
    """Tolerancia y matriz de afinidad: se aplican sobre la simulación en
    marcha, sin reiniciarla (a diferencia de los de 'Model Parameters')."""
    tol, set_tol = solara.use_state(float(model.tolerancia) if model else 1.0)
    a01, set_a01 = solara.use_state(float(model.afinidad[0][1]) if model else 1.0)
    a10, set_a10 = solara.use_state(float(model.afinidad[1][0]) if model else 1.0)
    a00, set_a00 = solara.use_state(float(model.afinidad[0][0]) if model else 0.0)
    a11, set_a11 = solara.use_state(float(model.afinidad[1][1]) if model else 0.0)

    def cambiar_tol(value):
        set_tol(value)
        if model is not None:
            model.tolerancia = value

    def cambiar_afinidad(i, j, setter):
        def on_change(value):
            setter(value)
            if model is not None:
                model.afinidad[i][j] = value
        return on_change

    return solara.Card(
        title="Controles en caliente (sin reset)",
        children=[
            solara.SliderFloat(label="Tolerancia", value=tol, min=0.0, max=8.0, step=0.5, on_value=cambiar_tol),
            solara.Markdown("**Matriz de afinidad** (aversión del tipo i hacia el tipo j)"),
            solara.SliderFloat(label="afinidad[1][1] (auto-aversión tipo1)", value=a00, min=0.0, max=5.0, step=0.5, on_value=cambiar_afinidad(0, 0, set_a00)),
            solara.SliderFloat(label="afinidad[1][2] (tipo1 hacia tipo2)", value=a01, min=0.0, max=5.0, step=0.5, on_value=cambiar_afinidad(0, 1, set_a01)),
            solara.SliderFloat(label="afinidad[2][1] (tipo2 hacia tipo1)", value=a10, min=0.0, max=5.0, step=0.5, on_value=cambiar_afinidad(1, 0, set_a10)),
            solara.SliderFloat(label="afinidad[2][2] (auto-aversión tipo2)", value=a11, min=0.0, max=5.0, step=0.5, on_value=cambiar_afinidad(1, 1, set_a11)),
            solara.Markdown(
                "Pausa la simulación, mueve un slider y pulsa Step/Play: "
                "se aplica sobre la configuración espacial actual, sin reiniciar."
            ),
        ],
    )


model_params = {
    "n1": Slider("n1 (tipo 1)", 500, 0, 1500, 10),
    "n2": Slider("n2 (tipo 2)", 500, 0, 1500, 10),
    "N": Slider("N (ancho de la grilla)", 40, 5, 100, 1),
    "M": Slider("M (alto de la grilla)", 40, 5, 100, 1),
}


def crear_modelo(n1=500, n2=500, N=40, M=40):
    return ModeloGeneral2(n1, n2, N, M)


modelo_inicial = crear_modelo()

SpaceGraph = make_space_component(agent_portrayal)
PlotInsatisfaccion = make_plot_component(["Insatisfaccion_Tipo1", "Insatisfaccion_Tipo2"])
PlotProporciones = make_plot_component(["Prop_11", "Prop_22", "Prop_12"])
PlotEntropia = make_plot_component("Entropia")

Page = SolaraViz(
    modelo_inicial,
    components=[SpaceGraph, PlotInsatisfaccion, PlotProporciones, PlotEntropia, InfoComponent, ControlesEnCaliente],
    model_params=model_params,
    name="Schelling General 2 — 2 poblaciones con matriz de afinidad",
)
