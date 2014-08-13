from math import ceil, floor
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from adapter import ListViewAdapter
from kivy.properties import DictProperty, NumericProperty, ObjectProperty, WeakListProperty


class ListContainerLayout(Layout):
    spacing = NumericProperty(0)
    padding = NumericProperty(0)
    widget = ObjectProperty(None)
    children = WeakListProperty([])

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

class SpecialListView(Widget, ListViewAdapter):
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
        super(SpecialListView, self).__init__(**kwargs)
        self.bind(pos=self._trigger_populate,
                  size=self._trigger_populate)

    def on_data(self, instance, value):
        super(SpecialListView, self).on_data(instance, value)
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
        
            self.count = count
        self._sizes.update(d)
        
Builder.load_string("""
#:import Scroller scroller.Scroller
#:import ActionWidget uiux.ActionWidget

<SpecialListView>:
    container: container_id

    ActionWidget:
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
            canvas.before:
                Color:
                    rgba: app.gray
                Rectangle:
                    size: self.size
                    pos: self.pos
""")
