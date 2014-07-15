from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.modules import inspector
from kivy.core.window import Window
#import cProfile

from weakref import ref, proxy
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.layout import Layout
from kivy.properties import WeakListProperty
from kivy.weakreflist import WeakList
from scroller import Scroller
from kivy.properties import OptionProperty, DictProperty, BooleanProperty, ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from math import ceil, floor

class ListViewAdapter(object):
    data = ListProperty([])
    cached_views = DictProperty({})
    list_item = ObjectProperty(None)
    selection = WeakListProperty(WeakList())
    args_converter = ObjectProperty(None)
    selection_mode = OptionProperty('single', options=('None', 'single'))

    def __init__(self, **kwargs):
        self.register_event_type('on_selection_change')
        super(ListViewAdapter, self).__init__(**kwargs)

    def on_data(self, instance, value):
        instance.delete_cache()

        if len(instance.selection) > 0:
            instance.selection[:] = []

    def on_selection(self, instance, value):
        instance.dispatch('on_selection_change')

    def delete_cache(self, *args):
        self.cached_views.clear()
        self.container.canvas.clear()

    def get_count(self):
        return len(self.data)

    def get_data_item(self, index):
        if (0 <= index < self.get_count()):
            return self.data[index]

    def get_view(self, index):
        if index in self.cached_views:
            return self.cached_views[index]
        else:
            item_view = self.create_view(index)

            if item_view:
                self.cached_views[index] = item_view
                return item_view

    def create_view(self, index):
        item = self.get_data_item(index)

        if item is not None:
            item_args = self.args_converter(index, item)
            item_args['index'] = index
            return self.list_item(**item_args)

    def deselect_all(self, *args):
        selection = self.selection

        for each_view in xrange(len(selection)):
            selection.pop().is_selected = False

    def handle_selection(self, view, hold_dispatch=False, *args):
        if view in self.selection:
            self.deselect_item_view(view)
        elif self.selection_mode == 'single':
            self.deselect_all()
            self.select_item_view(view)
        if not hold_dispatch:
            self.dispatch('on_selection_change')

    def select_item_view(self, view):
        view.is_selected = True
        self.selection.append(view)

    def deselect_item_view(self, view):
        view.is_selected = False
        self.selection.remove(view)

    def on_selection_change(self, *args):
        pass

class ButtonRoot(Widget):
    text = StringProperty('')
    index = NumericProperty(None)
    aleft = BooleanProperty(False)
    font_size = NumericProperty(0)
    markup = BooleanProperty(False)
    shorten = BooleanProperty(False)
    state_color = ListProperty([1.0, 1.0, 1.0, 0.0])
    text_color = ListProperty([0.0, 0.824, 1.0, 1.0])

    def on_state(self, *args):
        pass

    def on_touch_down(self, touch):
        if not self.disabled:
            touch.grab(self)
            touch.ud[ref(self)] = True
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
            
    def cancel(self):
        self.state = 'normal'

class Clickable(ButtonRoot):
    state = OptionProperty('normal', options=('normal', 'down'))

    def __init__(self, **kwargs):
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        self._press_ = Clock.create_trigger(self._trigger_press, 0.0) #instant-touch problem
        self._release_ = Clock.create_trigger(self._trigger_release, .15)        
        super(Clickable, self).__init__(**kwargs)

    def _trigger_press(self, dt):
        if ((self.state == 'normal') and not self.disabled):
            self.state = 'down'
            self.dispatch('on_press')
        else:
            return False

    def _trigger_release(self, dt):
        if self.state == 'normal':
            self.dispatch('on_release')
        else:
            return False

    def on_touch_down(self, touch):
        if self.state == 'normal':
            sup = super(ButtonRoot, self).on_touch_down(touch)

            if sup:
                return sup
            else:
                self._press_()

        return super(Clickable, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            assert(ref(self) in touch.ud)

            if self.state == 'down':
                self._release_()
                self.state = 'normal'
            elif self.state == 'normal':
                touch.ungrab(self)
                return super(ButtonRoot, self).on_touch_up(touch)

        return super(Clickable, self).on_touch_up(touch)

    def on_press(self):
        pass

    def on_release(self):
        pass
    
    def cancel(self):
        Clock.unschedule(self._trigger_press)
        super(Clickable, self).cancel()

class Button_(Clickable):
    _anim = lambda *_ : None
    state = OptionProperty('normal', options=('down', 'normal'))

    def __init__(self, **kwargs):
        super(Button_, self).__init__(**kwargs)
        self._press_ = Clock.create_trigger(self._trigger_press, 0)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        elif self._anim() is not None:
            return True
        else:
            return super(Button_, self).on_touch_down(touch)

class MyButton(Button_):

    def on_release(self):
        self.parent.state = 'set'

class Item(Label):
    pass

class MyWidget(Widget):
    button = ObjectProperty(None)
    state = OptionProperty('ready', options=('ready', 'set', 'go'))

    def on_state(self, instance, state):
        if ((state == 'set') and (len(self.children) == 1)):
            _pos = self.right, self.y
            hey = Button_(text='Hey', opacity=0, pos=_pos)
            heyy = Button_(text='Heyy', opacity=0, pos=_pos)
            heyyy = Button_(text='Heyyy', opacity=0, pos=_pos)
            add_widget = lambda a, w: self.add_widget(w)

            def _on_start1(a, w):
                self.add_widget(hey)
                anim1 = Animation(opacity=1, pos=self.pos, t='out_expo', duration=0.4)
                anim1.bind(on_start=_on_start2)
                hey._anim = ref(anim1)
                anim1.start(hey)

            def _on_start2(a, fw):
                self.add_widget(heyy)
                anim2 = Animation(opacity=1, center_x=self.center_x, t='out_expo', duration=0.4)
                anim2.bind(on_start=_on_start3)
                heyy._anim = ref(anim2)
                anim2.start(heyy)
                
            def _on_start3(a, w):
                anim3 = Animation(opacity=1, right=self.right, y=self.y, t='out_expo', duration=0.4)
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
            """remove_widget = lambda a, w: self.get_parent_window().remove_widget(w)
            popup = Popup(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                          size_hint=(0.45, 0.45))
            self.get_parent_window().add_widget(popup)
            anim = Animation(opacity=0, t='out_expo', duration=0.4)
            anim.bind(on_complete=remove_widget)
            for x in self.children[:]:
                x._anim = ref(anim)
            anim.start(popup)"""
            print 'helga'

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return super(MyWidget, self).on_touch_down(touch)

class ListContainerLayout(Layout):
    spacing = NumericProperty(0)
    padding = NumericProperty(0)
    widget = ObjectProperty(None)
    children = WeakListProperty(WeakList())

    def __init__(self, **kwargs):
        super(ListContainerLayout, self).__init__(**kwargs)
        self.bind(children=self._trigger_layout,
                  pos=self._trigger_layout,
                  pos_hint=self._trigger_layout,
                  size_hint=self._trigger_layout,
                  size=self._trigger_layout)

    def do_layout(self, *args):
        if 1 not in self.size:
            x, y = self.pos
            w, h = self.size
            spacing = self.spacing
            place = (y + h) - self.padding
            widget = self.widget
            widget.parent.state = 'ready'
            widget.text = ''
            widget_y = widget.y

            for c in reversed(self.children[:]):
                c.width = w
                c.x = x
                c.top = place
                place -= (c.height + spacing)

                if widget_y <= c.center_y:
                    widget.text = c.text

class DNDListView(Widget, ListViewAdapter):
    container = ObjectProperty(None)
    row_height = NumericProperty(None)
    _sizes = DictProperty({})
    _wstart = NumericProperty(0)
    _wend = NumericProperty(-1)
    _i_offset = NumericProperty(0)
    spacing = NumericProperty(1)
    count = NumericProperty(10)
    placeholder = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self._trigger_populate = Clock.create_trigger(self._do_layout, -1)
        super(DNDListView, self).__init__(**kwargs)
        self.bind(pos=self._trigger_populate,
                  size=self._trigger_populate)

    def on_data(self, instance, value):
        super(DNDListView, self).on_data(instance, value)
        instance._do_layout()

    def _scroll(self, scroll_y):
        if self.row_height:
            self._scroll_y = scroll_y
            scroll_y = 1 - min(1, max(scroll_y, 0))
            mstart = (self.container.height - self.height) * scroll_y
            mend = mstart + self.height

            # convert distance to index
            rh = self.row_height
            istart = int(ceil(mstart / rh))
            iend = int(floor(mend / rh))

            istart = max(0, istart - 1)
            iend = max(0, iend - 1)

            istart -= self._i_offset
            iend += self._i_offset

            if istart < self._wstart:
                rstart = max(0, istart - self.count)
                self.populate(rstart, iend)
                self._wstart = rstart
                self._wend = iend
            elif iend > self._wend:
                self.populate(istart, iend + self.count)
                self._wstart = istart
                self._wend = iend + self.count

    def _do_layout(self, *args):
        self._sizes.clear()
        self.populate()

    def on__sizes(self, instance, value):
        if value:
            container = instance.container
            instance.row_height = rh = next(value.itervalues(), 0) #since they're all the same
            container.height = ((rh + instance.spacing) * instance.get_count()) + (self.height - rh)

    def populate(self, istart=None, iend=None):
        container = self.container
        get_view = self.get_view
        rh = self.row_height
        sizes = self._sizes
        d = {}
        
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view
        container.clear_widgets()
        container.padding = 0

        # guess only ?
        if iend <> -1:
            spacing = self.spacing
            fh = 0

            # fill with a "padding"
            for x in xrange(istart):
                fh += sizes[x]+spacing if x in sizes else rh+spacing
            container.padding = fh

            # now fill with real item_view
            index = istart
            while index <= iend:
                item_view = get_view(index)

                if item_view is None:
                    break
                else:
                    d[index] = item_view.height
                    container.add_widget(item_view)
                index += 1

        else:
            available_height = self.height
            real_height = index = count = 0

            while available_height > 0:
                item_view = get_view(index)

                if item_view is None:
                    break
                else:
                    d[index] = item_view.height
                    index += 1
                    count += 1
                    container.add_widget(item_view)
                    available_height -= item_view.height
                    real_height += item_view.height
            #self.count = count

        self._sizes.update(d)

class Viewer(Screen):
    _item = ObjectProperty(proxy(Item))
    data = ListProperty(['Amanda Hugginkiss',
                         'Ivana Tinkle',
                         'Hugh Jass',
                         'Anita Bath',
                         'Maya Buttreeks',
                         'I.P. Freely',
                         'Al Coholic',
                         'Seymour Butts',
                         'Homer Sexual',
                         'Mike Rotch'])

    def _args_converter(self, row_index, an_obj):
        return {'text': an_obj,
                'size_hint_y': None}

class TestApp(App):
    blue = ListProperty((0.0, 0.824, 1.0, 1.0))
    white = ListProperty((1.0, 1.0, 1.0, 1.0))

    def build(self):
        app = Viewer()
        inspector.create_inspector(Window, app)
        return app

Builder.load_string("""
<ButtonRoot>:
    label: label_id
    layout: layout_id

    FloatLayout:
        id: layout_id
        size: root.size
        pos: root.pos
        canvas.before:
            Color:
                rgba: root.state_color
            Rectangle:
                size: self.size
                pos: self.pos

        Label:
            id: label_id
            text: root.text
            size_hint: 1, 1
            pos_hint: {'x': 0, 'y': 0}
            font_size: root.font_size
            shorten: root.shorten
            color: root.text_color
            markup: root.markup
            disabled_color: self.color
            text_size: (self.size[0]-(0.1*self.size[0]), None) if root.aleft else (None, None)

<Button_>:
    state_color: app.white if self.state=='down' else app.blue
    text_color: app.white
    font_size: self.height*0.3

<MyButton>:
    font_size: self.height*0.421875

<Item>:
    text_size: self.size[0]-(0.1*self.size[0]), None
    font_size: 28

<MyWidget>:
    button: button_id
    size_hint: 0.5, 0.5
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    canvas:
        Color:
            rgb: app.blue
        Rectangle:
            pos: self.pos
            size: self.size
    MyButton:
        id: button_id
        text: 'Truth'
        size: root.size[0], 0.5*root.size[1]
        pos: root.pos
        aleft: True
        
<DNDListView>:
    container: container_id

    MyWidget:
        id: widget_id
        size: root.size[0], (1.0/3)*root.size[1]
        top: root.top
        x: root.x
    Scroller:
        pos: root.pos
        size: root.size[0], (2.0/3)*root.size[1]
        on_scroll_y: root._scroll(args[1])

        ListContainerLayout:
            id: container_id
            x: root.x
            width: root.width
            spacing: root.spacing
            widget: widget_id.button

<Viewer>:
    name: 'My Screen'
    list_view: list_view_id

    Widget:
        size_hint: 1, 0.1127
        pos_hint:{'top': 1, 'x': 0}
        canvas.before:
            Color:
                rgba: app.blue
            Rectangle:
                size: self.size
                pos: self.pos

    DNDListView:
        id: list_view_id
        selection_mode: 'None'
        list_item: root._item
        args_converter: root._args_converter
        size_hint: 1, .8
        pos_hint: {'top': 0.8873}
        data: root.data


""")

if __name__ == '__main__':
    TestApp().run()

