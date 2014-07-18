from weakref import ref
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.effects.dampedscroll import DampedScrollEffect
from kivy.properties import AliasProperty, ListProperty, NumericProperty, ObjectProperty, OptionProperty

class ScrollerEffect(DampedScrollEffect):
    min_velocity = NumericProperty(10)
    _parent = ObjectProperty(None)
    max = NumericProperty(0)
    
    def _get_target_widget(self):
        if self._parent:
            return self._parent._viewport()

    target_widget = AliasProperty(_get_target_widget, None)
    
    def _get_min(self):
        if self.target_widget:
            return -(self.target_widget.size[1] - self._parent.height)
        else:
            return 0
        
    min = AliasProperty(_get_min, None)
    
    def on_scroll(self, instance, value):
        vp = instance.target_widget

        if vp:
            parent = instance._parent
            sh = vp.height - parent.height

            if sh >= 1:
                sy = value/float(sh)
                
                if parent.scroll_y == -sy:
                    parent._trigger_layout()
                else:
                    parent.scroll_y = -sy

            if ((not instance.is_manual) and ((abs(instance.velocity) <= instance.min_velocity) or (not value))):
                parent.mode = 'normal'

    def cancel(self):
        self.is_manual = False
        self.velocity = 0
        self._parent.mode = 'normal'

class StencilLayout(FloatLayout):
    pass

class Scroller(StencilLayout):
    scroll_distance = NumericProperty('10dp')
    scroll_y = NumericProperty(1.0)
    bar_color = ListProperty([0.7, 0.7, 0.7, 0.9])
    bar_width = NumericProperty('2dp')
    bar_margin = NumericProperty(0)
    _viewport = ObjectProperty(lambda : None)
    bar_alpha = NumericProperty(1.0)
    mode = OptionProperty('normal', options=('down', 'normal', 'scrolling'))

    def _get_vbar(self):
        # must return (y, height) in %
        # calculate the viewport size / Scroller size %
        ret = (0, 1.)

        if self._viewport():
            vh = self._viewport().height
            h = self.height
            
            if vh > h:
                ph = max(0.01, h / float(vh))
                sy = min(1.0, max(0.0, self.scroll_y))
                py = (1. - ph) * sy
                ret = (py, ph)

        return ret

    vbar = AliasProperty(_get_vbar, None, bind=('scroll_y', '_viewport'))

    def __init__(self, **kwargs):
        self.effect_y = ScrollerEffect(_parent=self.proxy_ref, round_value=False)
        super(Scroller, self).__init__(**kwargs)
        self.bind(scroll_y=self._trigger_layout)

    def do_layout(self, *args):
        if 1 not in self.size:
            vp = self._viewport()

            if vp:
                x, y = self.pos
                w, h = self.size
                vp.w, vp.x = w, x

                if vp.height > self.height:
                    sh = vp.height - h
                    vp.y = y - self.scroll_y * sh
                else:
                    vp.y = (y + h) - vp.height
                    self.scroll_y = 1.0
                  
    def on_height(self, instance, *args):
        self.effect_y.value = self.effect_y.min * self.scroll_y

    def on_touch_down(self, touch):        
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self.effect_y.start(touch.y)

            if self.mode == 'normal':
                self.mode = 'down'
                return super(Scroller, self).on_touch_down(touch)
            elif self.mode == 'scrolling':
                return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            
            if self.mode == 'down':
                ret = super(Scroller, self).on_touch_move(touch)
                
                if ret:
                    touch.ungrab(self)
                    self.effect_y.cancel()
                    return True
                elif abs(touch.dy) > self.scroll_distance:
                    l = len(touch.grab_list)

                    if l > 1:
                        NoneType = type(None)

                        for i, j in enumerate(touch.grab_list[:]):
                            item = j()

                            if type(item) not in (NoneType, Scroller):
                                touch.ungrab(item)
                                item.cancel()
                                touch.grab_list.insert(i, lambda : None)

                    if self._viewport().height > self.height:
                        self.mode = 'scrolling'

            if self.mode == 'scrolling':
                self.effect_y.update(touch.y)
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)

            if self.mode == 'down':
                self.effect_y.cancel()
            elif self.mode == 'scrolling':
                self.effect_y.stop(touch.y)
                self.effect_y.on_scroll(self.effect_y, self.effect_y.scroll)
            return True

        return super(Scroller, self).on_touch_up(touch)

    def add_widget(self, widget, index=0):
        if self._viewport():
            raise Exception('Scroller accept only one widget')
        super(Scroller, self).add_widget(widget, index)
        widget.unbind(pos=self._trigger_layout,
                      pos_hint=self._trigger_layout)
        widget.bind(height=self.on_height)
        self._viewport = ref(widget)
        self._trigger_layout()

    def remove_widget(self, widget):
        super(Scroller, self).remove_widget(widget)
        if widget is self._viewport():
            self._viewport = lambda : None

Builder.load_string("""
<StencilLayout>:
    canvas.before:
        StencilPush
        Rectangle:
            pos: self.pos
            size: self.size
        StencilUse
    canvas.after:
        StencilUnUse
        Rectangle:
            pos: self.pos
            size: self.size
        StencilPop

<Scroller>:
    canvas.after:
        Color:
            rgba: self.bar_color[:3] + [self.bar_color[3] * self.bar_alpha]
        Rectangle:
            pos: self.right - self.bar_width - self.bar_margin, self.y + self.height * self.vbar[0]
            size: self.bar_width, self.height * self.vbar[1]
""")
