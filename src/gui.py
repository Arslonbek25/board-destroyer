from nicegui import ui, app

app.native.window_args["resizable"] = False
ui.colors(primary="#8DB45B", secondary="#fff", accent="#ff0000")
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

with ui.row().classes("w-full no-wrap justify-between"):
    select2 = ui.toggle(["Rapid", "Blitz", "Bullet", "Puzzle"], value="Blitz").props(
        "no-caps"
    )
    select2 = ui.toggle(["White", "Black"], value="White").props("no-caps")

with ui.footer(fixed=False).style("background-color: #21201D"):
    ui.button("Start").props("no-caps")
    ui.button("Apply", color="#32312F").props("no-caps")


with ui.grid(columns=2).classes("w-full no-wrap"):

    def update_max_time_slider_min(value):
        max_time_slider.value = max(min_time_slider.value, max_time_slider.value)

    ui.label("Min Time:")
    ui.label("Max Time:")

    with ui.row().classes("w-1/2 no-wrap w-full"):
        min_time_slider = ui.slider(min=0.1, max=1, step=0.1, value=0.1)
        ui.label().bind_text_from(min_time_slider, "value")

    with ui.row().classes("w-1/2 no-wrap w-full"):
        max_time_slider = ui.slider(
            min=0.1, max=15, step=0.1, value=6, on_change=update_max_time_slider_min
        )
        ui.label().bind_text_from(max_time_slider, "value")


ui.label("Skill level:")
with ui.row().classes("w-full no-wrap"):
    skill_level = ui.slider(min=0, max=20, step=1, value=2)
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
