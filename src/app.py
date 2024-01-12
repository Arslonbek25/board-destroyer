import threading

from nicegui import ui

from config import Config
from main import run


class BoardDestroyer:
    def __init__(self):
        self.config_instance = Config()
        self.config_instance.load()
        self.max_time_slider = None
        self.setup_ui()

    def setup_ui(self):
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

        with ui.row().classes("w-full no-wrap justify-between"):
            self.time_control_toggle = (
                ui.toggle(
                    ["Rapid", "Blitz", "Bullet", "Puzzle"], on_change=self.on_tc_change
                )
                .bind_value(
                    self.config_instance,
                    "time_control_name",
                    forward=lambda x: x.lower(),
                    backward=lambda x: x.capitalize(),
                )
                .props("no-caps")
            )
            self.color_toggle = ui.toggle(
                ["White", "Black"],
                value="White" if self.config_instance.color == "w" else "Black",
                on_change=self.on_color_change,
            ).props("no-caps")

        with ui.footer(fixed=False).style("background-color: #21201D"):
            self.start_button = ui.button(
                "Start", on_click=self.toggle_game_running
            ).props("no-caps")
            ui.button(
                "Save", color="#32312F", on_click=self.config_instance.save
            ).props("no-caps")

        self.create_time_control_sliders()
        self.create_skill_level_slider()
        self.create_extra_options()

    def create_time_control_sliders(self):
        with ui.grid(columns=2).classes("w-full no-wrap"):
            ui.label("Min Time:")
            ui.label("Max Time:")

            with ui.row().classes("w-1/2 no-wrap w-full"):
                self.min_time_slider = ui.slider(
                    min=0.1,
                    max=1,
                    step=0.1,
                    on_change=self.on_min_time_change,
                    value=self.config_instance.time_control.max_time,
                )
                ui.label().bind_text_from(self.min_time_slider, "value")

            with ui.row().classes("w-1/2 no-wrap w-full"):
                self.max_time_slider = ui.slider(
                    min=0.1,
                    max=15,
                    step=0.1,
                    on_change=self.on_max_time_change,
                    value=self.config_instance.time_control.max_time,
                )
                ui.label().bind_text_from(self.max_time_slider, "value")

    def create_skill_level_slider(self):
        ui.label("Skill level:")
        with ui.row().classes("w-full no-wrap"):
            self.skill_level_slider = ui.slider(
                min=0,
                max=20,
                step=1,
                on_change=self.on_skill_level_change,
                value=self.config_instance.time_control.skill_level,
            )
            ui.label().bind_text_from(self.skill_level_slider, "value")

    def create_extra_options(self):
        with ui.row():
            ui.number(
                label="Time advantage",
                value=20,
                step=5,
                min=0,
                max=50,
                on_change=self.on_time_advantage_change,
            ).style("width: 90px")
            ui.number(
                label="Anticipate lines",
                value=1,
                min=0,
                max=10,
                on_change=self.on_lines_change,
            ).style("width: 90px")
            ui.number(
                label="K",
                value=0.15,
                min=0.05,
                step=0.05,
                max=1,
                on_change=self.on_k_change,
            ).style("width: 90px")
            ui.number(
                label="Randomness Factor",
                value=0.15,
                min=0,
                step=0.05,
                max=1,
                on_change=self.on_randomness_factor_change,
            ).style("width: 115px")

    def toggle_game_running(self, e):
        self.config_instance.game_running = not self.config_instance.game_running
        if self.config_instance.game_running:
            threading.Thread(target=run, args=(self.config_instance,)).start()
            self.start_button.props("color=red").set_text("Stop")
        else:
            self.start_button.props("color=primary").set_text("Start")

    def on_tc_change(self, e):
        if self.max_time_slider:
            self.max_time_slider.value = self.config_instance.time_control.max_time
            self.min_time_slider.value = self.config_instance.time_control.min_time
            self.skill_level_slider.value = (
                self.config_instance.time_control.skill_level
            )

    def on_color_change(self, e):
        self.config_instance.color = e.value[0].lower()

    def on_min_time_change(self, e):
        self.config_instance.time_control.min_time = e.value
        self.min_time_slider.value = min(self.max_time_slider.value, e.value)

    def on_max_time_change(self, e):
        self.config_instance.time_control.max_time = e.value
        self.max_time_slider.value = max(self.min_time_slider.value, e.value)

    def on_skill_level_change(self, e):
        self.config_instance.time_control.skill_level = e.value

    def on_time_advantage_change(self, e):
        self.config_instance.time_advantage = e.value

    def on_lines_change(self, e):
        self.config_instance.lines = e.value

    def on_k_change(self, e):
        self.config_instance.k = e.value

    def on_randomness_factor_change(self, e):
        self.config_instance.randomness_factor = e.value


app = BoardDestroyer()
ui.run(native=True, window_size=(500, 400), title="Board Destroyer")
ui.run(native=True, window_size=(500, 400), title="Board Destroyer")
