"""Visualización interactiva de schelling_general3.py (3 poblaciones + matriz de afinidad).

Uso como script standalone (abre una pestaña de navegador con play/pausa/paso):

    solara run src/visualizacion_general3.py

Uso desde una celda de Jupyter/notebook:

    import sys
    sys.path.insert(0, "src")
    from visualizacion_general3 import Page
    Page

Controles disponibles:
- Panel "Model Parameters" (n1, n2, n3, N, M): solo se aplican al pulsar
  "Reset", porque cambiar poblaciones o el tamaño de la grilla implica
  recrear los agentes desde cero.
- Play / Step / Pause (arriba del todo): controlan la simulación en curso.
- Panel "Controles en caliente" (tolerancia y cada coeficiente de la matriz
  de afinidad 3x3): a diferencia de "Model Parameters", estos se aplican
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

from schelling_general3 import ModeloGeneral3

TIPOS = (1, 2, 3)


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

    filas_afinidad = "\n".join(
        "        " + " | ".join(f"{model.afinidad[i][j]:.1f}" for j in range(3))
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

        **Matriz de afinidad actual:**
        ```
{filas_afinidad}
        ```
        """)

    return solara.Card(
        title="Información del Modelo",
        children=[solara.Markdown(texto)],
    )


@solara.component
def ControlesEnCaliente(model):
    """Tolerancia y matriz de afinidad 3x3: se aplican sobre la simulación en
    marcha, sin reiniciarla (a diferencia de los de 'Model Parameters')."""
    tol, set_tol = solara.use_state(float(model.tolerancia) if model else 1.0)

    def valor_inicial(i, j):
        return float(model.afinidad[i][j]) if model else (0.0 if i == j else 1.0)

    # 9 pares de estado explícitos (uno por celda de la matriz 3x3) en vez de
    # un bucle: las reglas de hooks de Solara exigen que use_state se llame
    # el mismo número de veces, en el mismo orden, en cada render.
    a00, set_a00 = solara.use_state(valor_inicial(0, 0))
    a01, set_a01 = solara.use_state(valor_inicial(0, 1))
    a02, set_a02 = solara.use_state(valor_inicial(0, 2))
    a10, set_a10 = solara.use_state(valor_inicial(1, 0))
    a11, set_a11 = solara.use_state(valor_inicial(1, 1))
    a12, set_a12 = solara.use_state(valor_inicial(1, 2))
    a20, set_a20 = solara.use_state(valor_inicial(2, 0))
    a21, set_a21 = solara.use_state(valor_inicial(2, 1))
    a22, set_a22 = solara.use_state(valor_inicial(2, 2))

    celdas = {
        (0, 0): (a00, set_a00), (0, 1): (a01, set_a01), (0, 2): (a02, set_a02),
        (1, 0): (a10, set_a10), (1, 1): (a11, set_a11), (1, 2): (a12, set_a12),
        (2, 0): (a20, set_a20), (2, 1): (a21, set_a21), (2, 2): (a22, set_a22),
    }

    def cambiar_tol(value):
        set_tol(value)
        if model is not None:
            model.tolerancia = value

    def cambiar_afinidad(i, j):
        def on_change(value):
            celdas[(i, j)][1](value)
            if model is not None:
                model.afinidad[i][j] = value
        return on_change

    sliders = [
        solara.SliderFloat(
            label=f"afinidad[{i+1}][{j+1}]" + (" (auto-aversión)" if i == j else ""),
            value=celdas[(i, j)][0],
            min=0.0, max=5.0, step=0.5,
            on_value=cambiar_afinidad(i, j),
        )
        for i in range(3) for j in range(3)
    ]

    return solara.Card(
        title="Controles en caliente (sin reset)",
        children=[
            solara.SliderFloat(label="Tolerancia", value=tol, min=0.0, max=8.0, step=0.5, on_value=cambiar_tol),
            solara.Markdown("**Matriz de afinidad** (aversión del tipo i hacia el tipo j)"),
            *sliders,
            solara.Markdown(
                "Pausa la simulación, mueve un slider y pulsa Step/Play: "
                "se aplica sobre la configuración espacial actual, sin reiniciar."
            ),
        ],
    )


model_params = {
    "n1": Slider("n1 (tipo 1)", 350, 0, 1500, 10),
    "n2": Slider("n2 (tipo 2)", 350, 0, 1500, 10),
    "n3": Slider("n3 (tipo 3)", 350, 0, 1500, 10),
    "N": Slider("N (ancho de la grilla)", 40, 5, 100, 1),
    "M": Slider("M (alto de la grilla)", 40, 5, 100, 1),
}


def crear_modelo(n1=350, n2=350, n3=350, N=40, M=40):
    return ModeloGeneral3(n1, n2, n3, N, M)


modelo_inicial = crear_modelo()

SpaceGraph = make_space_component(agent_portrayal)
PlotInsatisfaccion = make_plot_component(["Insatisfaccion_Tipo1", "Insatisfaccion_Tipo2", "Insatisfaccion_Tipo3"])
PlotProporciones = make_plot_component(["Prop_11", "Prop_22", "Prop_33", "Prop_12", "Prop_13", "Prop_23"])
PlotEntropia = make_plot_component("Entropia")

Page = SolaraViz(
    modelo_inicial,
    components=[SpaceGraph, PlotInsatisfaccion, PlotProporciones, PlotEntropia, InfoComponent, ControlesEnCaliente],
    model_params=model_params,
    name="Schelling General 3 — 3 poblaciones con matriz de afinidad",
)
