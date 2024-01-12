import threading

from nicegui import app, ui

from config import Config
from main import run

config_instance = Config()


app.native.window_args["resizable"] = False
ui.colors(primary="#8DB45B")
ui.query("body").style(
    "background-color: #302E2B; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,Helvetica,Arial,sans-serif;"
)
ui.query("button").style("font-family: 'Montserrat', sans-serif;")
ui.dark_mode(True)
ui.add_head_html(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap');
</style>
"""
)


def toggle_game_running():
    config_instance.game_running = not config_instance.game_running
    if config_instance.game_running:
        game_thread = threading.Thread(target=run, args=(config_instance,))
        game_thread.start()
        start_button.props("color=red").set_text("Stop")
    else:
        start_button.props("color=primary").set_text("Start")


def on_time_control_change(e):
    config_instance.timecontrol = e.value.lower()


def on_color_change(e):
    config_instance.color = e.value[0].lower()


with ui.row().classes("w-full no-wrap justify-between"):
    select2 = ui.toggle(
        ["Rapid", "Blitz", "Bullet", "Puzzle"],
        value=config_instance.timecontrol.capitalize(),
        on_change=on_time_control_change,
    ).props("no-caps")
    select2 = ui.toggle(
        ["White", "Black"], on_change=on_color_change, value="White"
    ).props("no-caps")

with ui.footer(fixed=False).style("background-color: #21201D"):
    start_button = ui.button("Start", on_click=toggle_game_running).props("no-caps")
    ui.button("Apply", color="#32312F").props("no-caps")


with ui.grid(columns=2).classes("w-full no-wrap"):

    def limit_max(e):
        max_time_slider.value = max(min_time_slider.value, e.value)
        max_time_slider.update()
        tc = getattr(config_instance, config_instance.timecontrol)
        tc.max_time = max_time_slider.value

    def limit_min(e):
        min_time_slider.value = min(max_time_slider.value, e.value)
        min_time_slider.update()
        tc = getattr(config_instance, config_instance.timecontrol)
        tc.min_time = min_time_slider.value

    ui.label("Min Time:")
    ui.label("Max Time:")

    with ui.row().classes("w-1/2 no-wrap w-full"):
        min_time_slider = ui.slider(
            min=0.1, max=1, step=0.1, value=0.1, on_change=limit_min
        )
        ui.label().bind_text_from(min_time_slider, "value")

    with ui.row().classes("w-1/2 no-wrap w-full"):
        max_time_slider = ui.slider(
            min=0.1, max=15, step=0.1, value=6, on_change=limit_max
        )
        ui.label().bind_text_from(max_time_slider, "value")


def on_skill_level_change(e):
    tc = getattr(config_instance, config_instance.timecontrol)
    tc.skill_level = e.value


ui.label("Skill level:")
with ui.row().classes("w-full no-wrap"):
    skill_level = ui.slider(
        min=0, max=20, step=1, value=2, on_change=on_skill_level_change
    )
    ui.label().bind_text_from(skill_level, "value")

with ui.row():
    time_advantage = ui.number(
        label="Time advantage", value=20, step=5, min=0, max=50
    ).style("width: 90px")
    lines = ui.number(label="Anticipate lines", value=1, min=0, max=10).style(
        "width: 90px"
    )
    k = ui.number(label="K", value=0.15, min=0.05, step=0.05, max=1).style(
        "width: 90px"
    )
    randomness_factor = ui.number(
        label="Randomness Factor", value=0.15, min=0, step=0.05, max=1
    ).style("width: 115px")


ui.run(native=True, window_size=(500, 400), title="Board Destroyer")
