from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, ObjectProperty


class Application(Widget):
    manager = ObjectProperty(None)


class HeyApp(App):
    red = ListProperty((1.0, 0.549, 0.5294, 1.0))
    black = ListProperty((0.0, 0.0, 0.0, 1.0))
    green = ListProperty((0.365, 0.7333, 0.632, 1.0))
    white = ListProperty((1.0, 1.0, 1.0, 1.0))
    gray = ListProperty((0.102, 0.102, 0.102, 1.0))
    purple = ListProperty((0.4, 0.35, 0.647, 1.0))
    yellow = ListProperty((0.56, 0.588, 0.082, 1.0))

    def build(self):
        app = Application()
        return app

    def on_pause(self):
        return True


Builder.load_string("""
#:import FriendsScreen friendsscreen.FriendsScreen
#:import ScreenManager kivy.uix.screenmanager.ScreenManager

<Application>:
    manager: manager_id

    ScreenManager:
        id: manager_id
        size: root.size
        pos: root.pos
        canvas.before:
            Color:
                rgba: app.black
            Rectangle:
                size: self.size
                pos: self.pos

        FriendsScreen:
""")

if __name__ == '__main__':
    HeyApp().run()

