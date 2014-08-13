from weakref import ref
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, OptionProperty, StringProperty


class ButtonRoot(Widget):
    text = StringProperty('')
    index = NumericProperty(None)
    aleft = BooleanProperty(False)
    font_size = NumericProperty(0)
    markup = BooleanProperty(False)
    shorten = BooleanProperty(False)
    font_name = StringProperty('Walkway Bold.ttf')
    state_color = ListProperty([1.0, 1.0, 1.0, 0.0])
    text_color = ListProperty([1.0, 1.0, 1.0, 1.0])

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


class HeyButton(Clickable):
    _anim = lambda *_ : None
    state = OptionProperty('normal', options=('down', 'normal'))

    def __init__(self, **kwargs):
        super(HeyButton, self).__init__(**kwargs)
        self._press_ = Clock.create_trigger(self._trigger_press, 0)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        elif self._anim() is not None:
            return True
        else:
            return super(HeyButton, self).on_touch_down(touch)

    def on_release(self):
        self.parent.state = 'go'


class ActionButton(HeyButton):
    font_name = StringProperty('oswald.bold.ttf')

    def on_touch_down(self, touch):
        if self.text:
            return super(ActionButton, self).on_touch_down(touch)

    def on_release(self):
        self.parent.state = 'set'


class Deletable(ButtonRoot):
    state = OptionProperty('normal', options=('delete', 'normal'))
    delete_button = lambda *_: None
    screen = ObjectProperty(None)
    _anim = lambda *_: None

    def __init__(self, **kwargs):
        self.register_event_type('on_delete_out')
        super(Deletable, self).__init__(**kwargs)

    def on_state(self, instance, value):
        if ((value <> 'delete') and instance.delete_button()):
            #instance.unbind(right=instance.delete_button.right, y=instance.delete_button.y)
            instance.dispatch('on_delete_out', instance.layout)
            instance.screen.polestar = lambda : None
        elif value == 'delete':
            deletebutton = DeleteButton(size=(instance.size[1], instance.size[1]),
                                        pos=((instance.right-instance.size[1]), instance.pos[1]),
                                        button=instance.proxy_ref)
            instance.add_widget(deletebutton, 1)
            instance.delete_button = ref(deletebutton)
            #instance.bind(right=deletebutton.right, y=deletebutton.y)
            instance.screen.polestar = ref(instance)
        super(Deletable, self).on_state(instance, value)

    def on_touch_down(self, touch):
        if self._anim() is not None:
            return True
        elif self.state == 'delete':
            sup = super(ButtonRoot, self).on_touch_down(touch)

            if not sup:
                self.state = 'normal'
            return True

        else:
            return super(Deletable, self).on_touch_down(touch)

    def on_touch_move(self, touch):

        if touch.grab_current is self:
            assert(ref(self) in touch.ud)

            if self.state in ('down', 'normal'):
                sup = super(ButtonRoot, self).on_touch_move(touch)

                if sup:
                    touch.ungrab(self)
                    return sup
                elif ((touch.dx < -20) and not self.delete_button()):
                    self.state = 'delete'

            if self.state == 'delete':
                new_pos = max(self.delete_button().x, min((self.layout.right+touch.dx), self.right))
                self.layout.right = new_pos
                return True
        
        elif ((self.state == 'delete') or (self.state in ('down', 'normal') and self.collide_point(*touch.pos) and ((touch.dx < -20) and not self.delete_button()))):
            return True
        return super(Deletable, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            assert(ref(self) in touch.ud)

            if self.state == 'delete':
                touch.ungrab(self)
                sup = super(ButtonRoot, self).on_touch_up(touch)

                if sup:
                    return sup
                else:
                    layout = self.layout
                    db = self.delete_button()

                    if (layout.right < db.center_x):
                        _anim = Animation(right=db.x, t='out_quad', d=0.2)
                        self._anim = ref(_anim)
                        _anim.start(layout.proxy_ref)
                    else:
                        self.state = 'normal'
                    return True

        return super(Deletable, self).on_touch_up(touch)

    def on_delete_out(self, layout, *args):

        def _do_release(a, widget):
            parent = widget.parent
            parent.remove_widget(parent.delete_button())
            parent.delete_button = lambda : None
        
        _anim = Animation(right=self.right, t='out_quad', d=0.2)
        _anim.bind(on_complete=_do_release)
        self._anim = ref(_anim)
        _anim.start(layout.proxy_ref)


class DeleteButton(Clickable):
    button = ObjectProperty(None, allownone=True)
    state = OptionProperty('normal', options=('down', 'normal'))

    def __init__(self, **kwargs):
        super(DeleteButton, self).__init__(**kwargs)
        self._press_ = Clock.create_trigger(self._trigger_press, 0)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return super(DeleteButton, self).on_touch_down(touch)

    def on_press(self):
        self.button.screen.dispatch('on_delete', self.button)


class Item(Deletable, Clickable):
    state = OptionProperty('normal', options=('delete', 'down', 'normal'))
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return super(Item, self).on_touch_down(touch)


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
            font_name: root.font_name
            shorten: root.shorten
            color: root.text_color
            markup: root.markup
            disabled_color: self.color
            text_size: (self.size[0]-(0.1*self.size[0]), None) if root.aleft else (None, None)


<HeyButton>:
    state_color: app.purple
    text_color: app.yellow if self.state=='down' else app.white
    font_size: self.height*0.3


<ActionButton>:
    font_size: self.height*0.421875


<DeleteButton>:
    text: 'Block'
    width: self.height
    font_size: self.height*0.7
    state_color: app.red
    canvas.before:
        Color:
            rgba: app.black
        Line:
            points: self.x, self.top-1, self.right, self.top-1
            width: 1.0

<Item>:
    aleft: True
    font_size: 28
    state_color: app.gray
    font_name: 'Walkway Bold.ttf'
    canvas.after:
        Color:
            rgba: app.black
        Line:
            points: root.x, root.y, root.right, root.y
            width: 1

""")
