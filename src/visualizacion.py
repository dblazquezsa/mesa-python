"""Visualización interactiva del modelo de desplazamiento (Schelling, 3 tipos).

Uso como script standalone (abre una pestaña de navegador con play/pausa/paso):

    solara run src/visualizacion.py

Uso desde una celda de Jupyter/notebook:

    import sys
    sys.path.insert(0, "src")
    from visualizacion import Page
    Page

Controles disponibles:
- Panel "Model Parameters" (N1, N2, N3, width, height, tol): solo se aplican al
  pulsar "Reset", porque cambiarlos implica recrear los agentes y la grilla desde
  cero (no se puede cambiar el número de agentes de una simulación ya en marcha).
- Play / Step / Pause (arriba del todo): controlan la simulación en curso.
- Slider "Tolerancia (en caliente)": a diferencia del de "Model Parameters", este
  modifica `model.tolerance` directamente sobre la simulación en marcha, sin
  reiniciarla. Pausa la simulación, cambia el valor y dale a Step/Play para ver
  el efecto sobre la configuración espacial actual.
"""

import textwrap

import solara

from mesa.visualization import SolaraViz, Slider, make_space_component, make_plot_component
from mesa.visualization.utils import update_counter

from modelo import Modelo_Desplazamiento


def agent_portrayal(agent):
    color = {1: "tab:green", 0: "tab:orange", -1: "tab:red"}.get(agent.tipo, "gray")
    return {"color": color, "size": 50}


@solara.component
def InfoComponent(model):
    """Resumen del estado actual del modelo: pasos, equilibrio y medida de contacto."""
    update_counter.get()  # suscribe este componente a force_update() (ver ModelController)
    if model is None:
        return solara.Markdown("## Esperando inicio del modelo...")

    if model.in_equilibrium:
        status_text, status_color = "**EQUILIBRIO ALCANZADO**", "green"
    else:
        status_text, status_color = "En proceso...", "orange"

    header = "Tipo agente |  -1   |   0   |   1  "
    sep = "-" * len(header)
    rows = "\n".join(
        f"     {a:>2}     | " + " | ".join(f"{model.contact_measure[a][b]:.2f}" for b in [-1, 0, 1])
        for a in [-1, 0, 1]
    )
    contact_info = f"```\n{header}\n{sep}\n{rows}\n```"

    conteo = {t: sum(1 for a in model.agents if a.tipo == t) for t in [-1, 0, 1]}

    # dedent solo sobre la parte de indentación uniforme; contact_info se concatena
    # después porque sus propias líneas no comparten esa indentación (rompería dedent).
    texto = textwrap.dedent(f"""\
        **Estado del Modelo**

        - **Pasos hasta el equilibrio:** {model.steps_to_equilibrium}
        - **Contactos mismo tipo (proporción):** {model.same_type_contact_ratio:.3f}
        - **Estado:** <span style='color: {status_color}'>{status_text}</span>
        - **Tolerancia actual:** {model.tolerance}
        - **Agentes:** {model.num_agents} (tipo 1: {conteo[1]}, tipo 0: {conteo[0]}, tipo -1: {conteo[-1]})

        **Medida de contacto (proporciones):**
        """) + contact_info

    return solara.Card(
        title="Información del Modelo",
        children=[solara.Markdown(texto)],
    )


@solara.component
def ToleranceControl(model):
    """Slider que cambia `model.tolerance` sobre la marcha, sin reiniciar la simulación."""
    tol, set_tol = solara.use_state(float(model.tolerance) if model else 2.0)

    def on_change(value):
        set_tol(value)
        if model is not None:
            model.tolerance = value

    return solara.Card(
        title="Tolerancia en caliente (sin reset)",
        children=[
            solara.SliderFloat(
                label="Tolerancia",
                value=tol,
                min=0.0,
                max=8.0,
                step=0.5,
                on_value=on_change,
            ),
            solara.Markdown(
                "Pausa la simulación, mueve el slider y pulsa Step/Play: "
                "se aplica sobre la configuración espacial actual, sin reiniciar."
            ),
        ],
    )


model_params = {
    "N1": Slider("N1 (tipo +1)", 500, 0, 1500, 10),
    "N2": Slider("N2 (tipo 0 / neutro)", 500, 0, 1500, 10),
    "N3": Slider("N3 (tipo -1)", 500, 0, 1500, 10),
    "width": 40,
    "height": 40,
    "tol": Slider("Tolerancia inicial", 2.0, 0.0, 8.0, 0.5),
}


def crear_modelo(N1=500, N2=500, N3=500, width=40, height=40, tol=2.0):
    return Modelo_Desplazamiento(N1, N2, N3, width, height, tol)


modelo_inicial = crear_modelo()

SpaceGraph = make_space_component(agent_portrayal)
ContactPlot = make_plot_component("Same_Type_Contact_Ratio")

Page = SolaraViz(
    modelo_inicial,
    components=[SpaceGraph, ContactPlot, InfoComponent, ToleranceControl],
    model_params=model_params,
    name="Schelling — desplazamiento con 3 tipos",
)
