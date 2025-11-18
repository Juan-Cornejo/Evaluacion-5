from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

# Importar módulo de métricas externo
from metrics import MetricsManager


class CounterWidget(BoxLayout):
    count = NumericProperty(0)
    status_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=20, **kwargs)

        # Instancia del manejador de métricas
        self.metrics = MetricsManager()

        # --- UI ---
        self.lbl = Label(text=str(self.count), font_size='48sp')
        self.add_widget(self.lbl)

        # Botón principal
        self.btn = Button(text="Presionar", size_hint=(1, 0.3), font_size='20sp')
        self.btn.bind(on_release=self.on_press_button)
        self.add_widget(self.btn)

        # Botón reset
        self.reset_btn = Button(text="Reiniciar contador", size_hint=(1, 0.2))
        self.reset_btn.bind(on_release=self.on_reset)
        self.add_widget(self.reset_btn)

        # Label estado
        self.status = Label(text=self.status_text, size_hint=(1, 0.15), font_size='14sp')
        self.add_widget(self.status)

        self.session_clock_event = None

    # --- Sesión ---
    def start_session(self):
        self.metrics.start_session()
        self.session_clock_event = Clock.schedule_interval(self._update_elapsed, 1)

    def stop_session(self):
        self.metrics.end_session()
        if self.session_clock_event:
            self.session_clock_event.cancel()
            self.session_clock_event = None

    # Actualiza tiempo de sesión en pantalla
    def _update_elapsed(self, dt):
        if self.metrics.session_start:
            import time
            elapsed = int(time.time() - self.metrics.session_start)
            total = self.metrics.metrics.get("total_presses", 0)
            self.status_text = f"Tiempo de sesión: {elapsed}s | Pulsaciones totales: {total}"
            self.status.text = self.status_text

    # --- Eventos ---
    def on_press_button(self, instance):
        self.count += 1
        self.lbl.text = str(self.count)
        self.metrics.register_button_press()

    def on_reset(self, instance):
        self.count = 0
        self.lbl.text = str(self.count)
        self.metrics.register_reset()


class ContadorApp(App):
    def build(self):
        self.title = "Contador + Métricas (modular)"
        self.widget = CounterWidget()
        return self.widget

    def on_start(self):
        self.widget.start_session()

    def on_stop(self):
        self.widget.stop_session()


if __name__ == "__main__":
    ContadorApp().run()