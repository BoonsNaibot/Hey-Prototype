from buttons import Item
from uiux import Screen_
from weakref import proxy
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty


class FriendsScreen(Screen_):
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
    

Builder.load_string("""
#:import Label kivy.uix.label.Label
#:import SpecialListView listviews.SpecialListView


<FriendsScreen>:
    name: 'Friends Screen'
    list_view: list_view_id

    Widget:
        size_hint: 1, 0.1127
        pos_hint:{'top': 1, 'x': 0}
        canvas.before:
            Color:
                rgba: app.purple
            Rectangle:
                size: self.size
                pos: self.pos

    SpecialListView:
        id: list_view_id
        selection_mode: 'None'
        list_item: root._item
        args_converter: root._args_converter
        size_hint: 1, .8
        pos_hint: {'top': 0.8873}
        data: root.data
    Label:
        pos_hint: {'center_x': (1.0/3.0), 'y': 0}
        font_name: 'heydings_icons.ttf'
        font_size: self.height*0.7
        size_hint: 0.0625, 0.086
        color: app.white
        opacity: 0.5
        text: 'y'
    Label:
        pos_hint: {'center_x': (2.0/3.0), 'y': 0}
        font_name: 'heydings_icons.ttf'
        font_size: self.height*0.7
        size_hint: 0.0625, 0.086
        color: app.green
        text: 'A'
""")
