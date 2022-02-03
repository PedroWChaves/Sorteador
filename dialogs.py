from kivymd.uix.tab import MDTabsBase
from kivymd.uix.card import MDCard
from kivymd.uix.list import TwoLineListItem, OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.color_definitions import colors

from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
#from kivy.utils import get_color_from_hex

from main import Sorteador as App

class InputMenuItem(MDCard):
    pass

class MenuItem(OneLineIconListItem):
    icon = StringProperty()


class CancelButton(MDFlatButton):
    pass

class OkayButton(MDRaisedButton):
    pass


class AddTabContent(BoxLayout):
    pass

class RemoveTabContent(BoxLayout):
    pass

class EditNumbersContent(BoxLayout):
    minimum = StringProperty()
    maximum = StringProperty()

class EditListaContent(BoxLayout):
    lista = StringProperty("")

class SaveAsContent(BoxLayout):
    pass

class TimeFormatContent(BoxLayout):
    pass


def delete_dialog(obj):
    App.get_running_app().dialog = None

def file_error_dialog(app, error):
    dialog = MDDialog(
        title="Erro no Arquivo JSON",
        text=f'Não foi possível encontrar ou carregar o arquivo "{app.FILE}", um novo será gerado\n\n{error}',
    )

    return dialog

def add_tab_dialog(app):
    dialog = MDDialog(
        title = "Adicionar Sorteador:",
        type = "custom",
        content_cls = AddTabContent(),
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=app.add_tab),
        ],
        on_dismiss = delete_dialog,
    )

    return dialog

def remove_tab_dialog(app):
    dialog = MDDialog(
        title = "Remover Sorteador:",
        type = "custom",
        content_cls = RemoveTabContent(),
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=app.remove_tab),
        ],
        on_dismiss = delete_dialog,
    )

    dialog_list = dialog.ids.spacer_top_box.children[0].ids.list_manager

    for i, tab in enumerate(app.data["tabs"]):
        dialog_list.add_widget(
            TwoLineListItem(
                text = tab["title"],
                secondary_text = tab["tipo"],
                on_release= select_to_remove
                )
            )

    return dialog

def select_to_remove(obj):
    app = App.get_running_app()
    app.dialog.ids.spacer_top_box.children[0].ids.selecionado.text = obj.text

def confirmation_dialog(app, text, confirm_action, *args):
    dialog = MDDialog(
        title = "Cofirmação",
        text = text,
        type = "alert",
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=lambda x: confirm_action(*args)),
        ],
        on_dismiss = delete_dialog,
    )

    return dialog

def save_as_dialog(app):
    dialog = MDDialog(
        title = "Salvar Como:",
        type = "custom",
        content_cls = SaveAsContent(),
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=app.save_as_file),
        ],
        on_dismiss = delete_dialog,
    )

    return dialog




def edit_numbers_dialog(app, obj):
    numbers = obj.ids.numbers_text.text.split(" ")
    minimum = numbers[1]
    maximum = numbers[3]

    dialog = MDDialog(
        title = "Editar Sorteador:",
        type = "custom",
        content_cls = EditNumbersContent(minimum=minimum, maximum=maximum),
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=lambda x: app.edit_numbers(obj)),
        ],
        on_dismiss = delete_dialog,
    )

    return dialog

def edit_lista_dialog(app, obj):
    dialog = MDDialog(
        title = "Editar Sorteador:",
        type = "custom",
        content_cls = EditListaContent(),
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=lambda x: app.edit_lista(obj)),
        ],
        on_dismiss = delete_dialog,
    )

    for item in obj.lista:
        dialog.ids.spacer_top_box.children[0].ids.itens_lista.add_widget(
            MenuItem(
                text=item,
                icon="close",
            )
        )

    return dialog

def remove_item_lista(item):
    app = App.get_running_app()
    app.dialog.ids.spacer_top_box.children[0].ids.itens_lista.remove_widget(item)

def add_item_lista(item):
    if not item.text:
        return

    app = App.get_running_app()
    app.dialog.ids.spacer_top_box.children[0].ids.itens_lista.add_widget(
        MenuItem(text=item.text, icon="close")
        )
    item.text = ""

def time_format_dialog(app, *args):
    dialog = MDDialog(
        title = "Selecionar Formato:",
        type = "custom",
        content_cls = TimeFormatContent(),
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=app.set_time_format),
        ],
        on_dismiss = delete_dialog,
    )

    return dialog







'''
class MyColorPicker(BoxLayout):
    initial_color = ListProperty()
    picked_color = ListProperty([])


class ColorTab(BoxLayout, MDTabsBase):
    color = StringProperty()
    hues = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #"md_bg_color": get_color_from_hex(colors[tab_text][value_color])

        for hue in self.hues:
            self.add_widget(
                ColorItem(
                    text = hue,
                    color_name = self.color,
                    bg_color = get_color_from_hex(colors[self.color][hue])
                    )
            )

class ColorItem(MDRaisedButton):
    text = StringProperty()
    color_name = StringProperty()
    bg_color = ListProperty()


def color_picker_dialog(app, color):
    dialog = MDDialog(
        title = "Selecione a cor:",
        type = "custom",
        content_cls = MyColorPicker(initial_color = color),
        buttons=[
            CancelButton(on_release=app.close_dialog),
            OkayButton(on_release=app.close_dialog),
        ],
        on_dismiss = delete_dialog,
    )

    colors_tab = dialog.ids.spacer_top_box.children[0].ids.colors_tab

    for color in colors:
        colors_tab.add_widget(
            ColorTab(
                color = color,
                hues = colors[color]
            )
        )


    return dialog


kv = """
<MyColorPicker>:
    id: color_picker
    height: "450dp"
    size_hint: (0.9, None)
    orientation: "horizontal"

    MDTabs:
        id: colors_tab
        tab_bar_height: "50dp"
        background_color: root.initial_color

<ColorTab>:
    title: root.color
    orientation: "vertical"

<ColorItem>:
    text: root.text
    md_bg_color: root.bg_color
    size_hint: (1, 1)
    on_release: app.color_picked(root.color_name, root.text, root.bg_color)
"""

'''