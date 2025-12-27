import sys

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.core.window import Window

from storage import load_config, save_config, load_presets, save_presets
from scheduler import is_sleep_time

# -------------------------------------------------
# PLATFORM DETECTION
# -------------------------------------------------
IS_ANDROID = sys.platform == "android"

# -------------------------------------------------
# ANDROID IMPORTS (SAFE GUARDED)
# -------------------------------------------------
if IS_ANDROID:
    from jnius import autoclass, PythonJavaClass, java_method

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
    NotificationBuilder = autoclass("android.app.Notification$Builder")
    NotificationChannel = autoclass("android.app.NotificationChannel")
    NotificationManager = autoclass("android.app.NotificationManager")
    TimePickerDialog = autoclass("android.app.TimePickerDialog")
    RingtoneManager = autoclass("android.media.RingtoneManager")
    Uri = autoclass("android.net.Uri")
    Intent = autoclass("android.content.Intent")
    Build = autoclass("android.os.Build")
else:
    PythonJavaClass = object
    def java_method(*args, **kwargs):
        def wrapper(fn): return fn
        return wrapper

# -------------------------------------------------
# UI
# -------------------------------------------------
Window.clearcolor = (0.08, 0.15, 0.25, 1)

KV = """
<RootUI>:
    orientation: "vertical"
    padding: 25
    spacing: 15

    Label:
        text: "💧 Water Reminder"
        font_size: "28sp"
        bold: True
        size_hint_y: None
        height: 50

    BoxLayout:
        orientation: "vertical"
        spacing: 10
        padding: 20
        canvas.before:
            Color:
                rgba: 0.15, 0.25, 0.4, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [20]

        Label:
            text: "Interval (minutes)"
        Slider:
            min: 15
            max: 120
            step: 15
            value: root.interval
            on_value: root.set_interval(int(self.value))
        Label:
            text: f"{root.interval} minutes"

        Label:
            text: "Sleep Time"
        BoxLayout:
            spacing: 10
            Button:
                text: root.sleep_start
                on_press: root.change_sleep_start()
            Button:
                text: root.sleep_end
                on_press: root.change_sleep_end()

        Label:
            text: "Presets"
        Spinner:
            id: preset_spinner
            text: "Select preset"
            values: root.preset_names
        BoxLayout:
            spacing: 5
            Button:
                text: "Save"
                on_press: root.save_preset()
            Button:
                text: "Load"
                on_press: root.load_preset()
            Button:
                text: "Delete"
                on_press: root.delete_preset()

    Button:
        text: "Choose Ringtone"
        on_press: root.pick_ringtone()

    Label:
        text: root.status_text

    Button:
        text: root.button_text
        size_hint_y: None
        height: 55
        on_press: root.toggle()
"""

# -------------------------------------------------
# ANDROID TIME PICKER CALLBACK
# -------------------------------------------------
class TimeSetListener(PythonJavaClass):
    __javainterfaces__ = ["android/app/TimePickerDialog$OnTimeSetListener"]
    __javacontext__ = "app"

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method("(Landroid/widget/TimePicker;II)V")
    def onTimeSet(self, view, hour, minute):
        self.callback(f"{hour:02d}:{minute:02d}")

# -------------------------------------------------
# MAIN UI CLASS
# -------------------------------------------------
class RootUI(BoxLayout):
    interval = NumericProperty(30)
    sleep_start = StringProperty("23:00")
    sleep_end = StringProperty("07:00")
    ringtone_uri = StringProperty("DEFAULT")

    preset_names = ListProperty([])
    presets = []

    button_text = StringProperty("Start Reminder")
    status_text = StringProperty("Idle")

    event = None
    elapsed = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cfg = load_config()
        self.interval = cfg["interval"]
        self.sleep_start = cfg["sleep_start"]
        self.sleep_end = cfg["sleep_end"]
        self.ringtone_uri = cfg.get("ringtone", "DEFAULT")

        self.presets = load_presets()
        self.refresh_presets()

    # ---------------- CONFIG ----------------
    def save_all(self):
        save_config({
            "interval": self.interval,
            "sleep_start": self.sleep_start,
            "sleep_end": self.sleep_end,
            "ringtone": self.ringtone_uri
        })

    def set_interval(self, val):
        self.interval = val
        self.save_all()

    # ---------------- TIME PICKER ----------------
    def open_time_picker(self, callback):
        if not IS_ANDROID:
            self.status_text = "Time picker works on Android only"
            return

        dialog = TimePickerDialog(
            PythonActivity.mActivity,
            TimeSetListener(callback),
            23, 0, True
        )
        dialog.show()

    def change_sleep_start(self):
        self.open_time_picker(lambda t: setattr(self, "sleep_start", t))
        self.save_all()

    def change_sleep_end(self):
        self.open_time_picker(lambda t: setattr(self, "sleep_end", t))
        self.save_all()

    # ---------------- PRESETS ----------------
    def refresh_presets(self):
        self.preset_names = [p["name"] for p in self.presets]

    def save_preset(self):
        name = f"Preset {len(self.presets) + 1}"
        self.presets.append({
            "name": name,
            "interval": self.interval,
            "sleep_start": self.sleep_start,
            "sleep_end": self.sleep_end
        })
        save_presets(self.presets)
        self.refresh_presets()
        self.status_text = f"Saved {name}"

    def load_preset(self):
        name = self.ids.preset_spinner.text
        for p in self.presets:
            if p["name"] == name:
                self.interval = p["interval"]
                self.sleep_start = p["sleep_start"]
                self.sleep_end = p["sleep_end"]
                self.save_all()
                self.status_text = f"Loaded {name}"

    def delete_preset(self):
        name = self.ids.preset_spinner.text
        self.presets = [p for p in self.presets if p["name"] != name]
        save_presets(self.presets)
        self.refresh_presets()
        self.status_text = "Preset deleted"

    # ---------------- RINGTONE ----------------
    def pick_ringtone(self):
        if not IS_ANDROID:
            self.status_text = "Ringtone picker works on Android only"
            return

        intent = Intent(RingtoneManager.ACTION_RINGTONE_PICKER)
        intent.putExtra(RingtoneManager.EXTRA_RINGTONE_TYPE, RingtoneManager.TYPE_ALARM)
        PythonActivity.mActivity.startActivityForResult(intent, 200)

    # ---------------- NOTIFICATIONS ----------------
    def ensure_channel(self):
        if not IS_ANDROID or Build.VERSION.SDK_INT < 26:
            return

        manager = PythonActivity.mActivity.getSystemService(Context.NOTIFICATION_SERVICE)
        channel = NotificationChannel(
            "water",
            "Water Reminder",
            NotificationManager.IMPORTANCE_HIGH
        )
        manager.createNotificationChannel(channel)

    def notify(self):
        if not IS_ANDROID:
            print("Desktop reminder: Drink Water")
            return

        ctx = PythonActivity.mActivity
        manager = ctx.getSystemService(Context.NOTIFICATION_SERVICE)

        builder = NotificationBuilder(ctx, "water")
        builder.setContentTitle("💧 Drink Water")
        builder.setContentText("Time to hydrate!")
        builder.setSmallIcon(ctx.getApplicationInfo().icon)

        if self.ringtone_uri == "DEFAULT":
            builder.setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM))
        else:
            builder.setSound(Uri.parse(self.ringtone_uri))

        manager.notify(1, builder.build())

    # ---------------- TIMER ----------------
    def toggle(self):
        if self.event:
            self.event.cancel()
            self.event = None
            self.button_text = "Start Reminder"
            self.status_text = "Stopped"
        else:
            self.ensure_channel()
            self.elapsed = 0
            self.event = Clock.schedule_interval(self.tick, 60)
            self.button_text = "Stop Reminder"

    def tick(self, dt):
        if is_sleep_time(self.sleep_start, self.sleep_end):
            self.status_text = "Sleeping hours"
            return

        self.elapsed += 1
        remaining = self.interval - self.elapsed
        self.status_text = f"Next reminder in {remaining} min"

        if self.elapsed >= self.interval:
            self.notify()
            self.elapsed = 0

# -------------------------------------------------
# ACTIVITY RESULT (ANDROID)
# -------------------------------------------------
def on_activity_result(req, res, intent):
    if not IS_ANDROID or req != 200 or not intent:
        return

    uri = intent.getParcelableExtra(RingtoneManager.EXTRA_RINGTONE_PICKED_URI)
    if uri:
        root = App.get_running_app().root
        root.ringtone_uri = str(uri)
        root.save_all()

# -------------------------------------------------
# APP
# -------------------------------------------------
class WaterReminderApp(App):
    def build(self):
        if IS_ANDROID:
            PythonActivity.mActivity.bind(onActivityResult=on_activity_result)
        Builder.load_string(KV)
        return RootUI()

if __name__ == "__main__":
    WaterReminderApp().run()
