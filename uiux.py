from weakref import ref
from buttons import HeyButton
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.properties import NumericProperty, ObjectProperty, OptionProperty


class Screen_(Screen):
    _anim = lambda *_: None
    _item = ObjectProperty(None)
    list_view = ObjectProperty(None)
    polestar = ObjectProperty(lambda : None)

    def __init__(self, **kwargs):
        self.register_event_type('on_delete')
        self.register_event_type('on_status_bar')
        self.register_event_type('on_screen_change')
        super(Screen_, self).__init__(**kwargs)
        
    def on_list_view(self, instance, value):
        if value:
            instance._item.screen = instance.proxy_ref
            instance._item.listview = value

    def on_touch_down(self, touch):
        if self._anim() is None:
            polestar = self.polestar()

            if polestar:
                touch.push()
                touch.apply_transform_2d(self.to_local)
                ret = polestar.dispatch('on_touch_down', touch)
                touch.pop()

                if not ret:
                    self.polestar = lambda : None
                return ret

            else:
                return super(Screen_, self).on_touch_down(touch)

    def on_screen_change(self, destination, kwargs, transition=None):
        transition = transition or SlideTransition
        manager =  self.manager
        transition = transition(**kwargs)
        manager.transition = transition
        manager.current = destination

    def on_delete(self, *args):
        pass

    def on_status_bar(self, *args):
        pass


class SentPopup(Widget):

    def on_touch_down(self, *args):
        return False


class ActionWidget(Widget):
    button = ObjectProperty(None)
    state = OptionProperty('ready', options=('ready', 'set', 'go'))

    def on_state(self, instance, state):
        if ((state == 'set') and (len(self.children) == 1)):
            _pos = self.right, self.y
            hey = HeyButton(text='Hey', font_name='oswald.bold.ttf', opacity=0, pos=_pos)
            heyy = HeyButton(text='Heyy', font_name='oswald.bold.ttf', opacity=0, pos=_pos)
            heyyy = HeyButton(text='Heyyy', font_name='oswald.bold.ttf', opacity=0, pos=_pos)
            add_widget = lambda a, w: self.add_widget(w)

            def _on_start1(a, w):
                self.add_widget(hey)
                anim1 = Animation(opacity=1,
                                  center_x=(self.width/6.0),
                                  y=self.y,
                                  t='out_expo',
                                  duration=0.4)
                anim1.bind(on_start=_on_start2)
                hey._anim = ref(anim1)
                anim1.start(hey)

            def _on_start2(a, fw):
                self.add_widget(heyy)
                anim2 = Animation(opacity=1,
                                  center_x=self.center_x,
                                  y=self.y,
                                  t='out_expo',
                                  duration=0.4)
                anim2.bind(on_start=_on_start3)
                heyy._anim = ref(anim2)
                anim2.start(heyy)
                
            def _on_start3(a, w):
                anim3 = Animation(opacity=1,
                                  center_x=(self.width*(5.0/6)),
                                  y=self.y,
                                  t='out_expo',
                                  duration=0.4)
                anim3.bind(on_start=add_widget)
                hey._anim = ref(anim3)
                anim3.start(heyyy)

            anim = Animation(top=self.top, t='out_expo', duration=0.4)
            anim.bind(on_start=_on_start1)
            self.button._anim = ref(anim)
            anim.start(self.button)

        elif ((state == 'ready') and (len(self.children) > 1)):
            remove_widget = lambda a, w: self.remove_widget(w)

            def _on_start(a, w):
                for x in self.children[:]:
                    if x is not w.__self__:
                        _anim = Animation(opacity=0, t='out_expo', duration=0.4)
                        _anim.bind(on_complete=remove_widget)
                        x._anim = ref(_anim)
                        _anim.start(x)

            anim = Animation(y=self.y, t='out_expo', duration=0.4)
            anim.bind(on_start=_on_start)
            self.button._anim = ref(anim)            
            anim.start(self.button)

        elif state == 'go':
            viewer = self.parent.parent

            def _on_start(a, w):
                for x in self.children[:]:
                    x._anim = ref(a)
                viewer.add_widget(w)
            
            def _on_complete(a, w):
                viewer.remove_widget(w)
                if self.state == 'go':
                    self.state = 'set'

            anim = Animation(opacity=0, duration=2.0)
            anim.bind(on_start=_on_start, on_complete=_on_complete)
            anim.start(SentPopup())

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return super(ActionWidget, self).on_touch_down(touch)


Builder.load_string("""
#:import ActionsButton buttons.ActionsButton

<SentPopup>:
    opacity: 0.5
    size_hint: 0.45, None
    height: self.width
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    canvas.before:
        Color:
            rgba: app.black
        Rectangle:
            size: self.size
            pos: self.pos

    Label:
        text: 'O'
        font_size: root.height*0.7
        font_name: 'heydings_icons.ttf'
        center_x: root.center_x
        top: root.top
    Label:
        text: 'Sent'
        y: root.y
        center_x: root.center_x
        font_size: root.height*0.45
        font_name: 'Walkway Bold.ttf'


<ActionWidget>:
    button: button_id
    size_hint: 0.5, 0.5
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    canvas:
        Color:
            rgb: app.purple
        Rectangle:
            pos: self.pos
            size: self.size
    ActionsButton:
        id: button_id
        text: 'Truth'
        size: root.size[0], 0.5*root.size[1]
        pos: root.pos
        aleft: True
""")
