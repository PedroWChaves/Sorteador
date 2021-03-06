from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.textfield import MDTextField
from kivymd.uix.filemanager import MDFileManager
from kivymd.color_definitions import colors
#from kivymd.uix.pickers import MDColorPicker

from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout

import random as r
import time as t

from dialogs import *
from files import *

# CLASSES BASE
class MyTextField(MDTextField):
    def on_text(self, instance, text):
        if text == "":
            Clock.schedule_once(lambda x: self.text_focus(instance), 0)

    def text_focus(self, instance):
        instance.focus = True

class MDCardElev(MDCard, FakeRectangularElevationBehavior):
    pass

class TabNumero(FloatLayout, MDTabsBase):
    num_tab = NumericProperty()
    minimum = StringProperty("1")
    maximum = StringProperty("100")
    sorteado = StringProperty("")

class TabLista(FloatLayout, MDTabsBase):
    num_tab = NumericProperty()
    lista = ListProperty([])
    sorteado = StringProperty("")

class TabDado(FloatLayout, MDTabsBase):
    num_tab = NumericProperty()
    sorteado = StringProperty("dice-multiple")

class ConfigurationItems(MDList):
    pass

class MeuPerfilList(MDList):
    pass

class Sorteador(MDApp):
    FILE = "configs.json"

    # VARIAVEIS GLOBAIS
    dialog = None
    num_tabs = 0
    nav_content = "perfil"

    # DECORATOR
    def autosave(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)

            if self.data["configs"]["autosave"]:
                save_json(self.data, self.path, self.FILE)

        return wrapper


    # INICIALIZA????O, FINALIZA????O E REINICIALIZA????O
    def build(self):
        self.path = self.user_data_dir + "/"
        self.data, self.load_error = load_json(self.path, self.FILE)
        if not self.load_error: check_json_file(self)

        self.theme_cls.primary_palette = self.data['configs']['color']
        self.theme_cls.primary_hue = self.data['configs']['color_hue']
        self.theme_cls.accent_palette = self.data['configs']['accent']
        self.theme_cls.accent_hue = self.data['configs']['accent_hue']
        self.theme_cls.theme_style = self.data['configs']['theme']
        self.ultimos = self.data["ultimos"].copy()

        Window.bind(on_request_close=self.on_request_close)
        Window.softinput_mode = "below_target" # TESTAR
        Window.keyboard_padding = 5 # TESTAR
        if platform == "win":
            Window.size = (337.5, 600)

        return Builder.load_file('design.kv')


    def on_start(self):
        self.menu = self.start_menu(items={
            "Numero": "numeric", 
            "Lista": "format-list-bulleted", 
            "Dado": "dice-6",
            }
        )

        self.create_file_manager()
        self.load_tabs()

        if self.load_error:
            self.open_dialog(file_error_dialog, self.load_error)

        del self.load_error


    def on_request_close(self, *args, **kwargs):
        save_json(self.data, self.path, self.FILE)
        return False


    def exit(self, *args):
        save_json(self.data, self.path, self.FILE)
        self.stop()


    def restart_app(self):
        self.data, _ = load_json(self.path, self.FILE)
        self.ultimos = self.data["ultimos"].copy()

        self.theme_cls.primary_palette = self.data['configs']['color']
        self.theme_cls.primary_hue = self.data['configs']['color_hue']
        self.theme_cls.accent_palette = self.data['configs']['accent']
        self.theme_cls.accent_hue = self.data['configs']['accent_hue']
        self.theme_cls.theme_style = self.data['configs']['theme']

        for tab in self.root.ids.tab_master.get_tab_list():
            self.root.ids.tab_master.remove_widget(tab)

        self.load_tabs()
        self.toggle_nav_drawer()


    # APP
    def save_file(self, *args):
        save_json(*args)

        snackbar = Snackbar(
            text = '   Arquivo salvo com sucesso!',
            size_hint_y = 0.1,
            duration = 1
        )
        snackbar.open()


    def reset_file(self, *args):
        reset_json(*args)
        self.close_dialog()


    def load_tabs(self):
        self.num_tabs = 0

        for tab in self.data["tabs"]:
            tipo = tab["tipo"]

            if tipo == "Numero":
                self.root.ids.tab_master.add_widget(
                    TabNumero(
                        num_tab=self.num_tabs,
                        title=tab["title"],
                        minimum=tab["minimum"],
                        maximum=tab["maximum"],
                        sorteado=tab["sorteado"]
                    )
                )

            elif tipo == "Lista":
                self.root.ids.tab_master.add_widget(
                    TabLista(
                        num_tab=self.num_tabs,
                        title=tab["title"],
                        lista=tab["lista"],
                        sorteado=tab["sorteado"]
                    )
                )

            elif tipo == "Dado":
                self.root.ids.tab_master.add_widget(
                    TabDado(
                        num_tab=self.num_tabs,
                        title=tab["title"],
                        sorteado=tab["sorteado"]
                    )
                )

            self.num_tabs +=1


    def toggle_nav_drawer(self, *args):
        self.root.ids.nav_drawer.set_state("toggle")
        if self.nav_content != "perfil":
            self.show_meu_perfil()


    def show_meu_perfil(self, *args):
        self.root.ids.list_holder.clear_widgets()
        self.root.ids.list_holder.add_widget(MeuPerfilList())

        button = self.root.ids.nav_drawer.children[0]
        self.root.ids.nav_drawer.remove_widget(button)

        self.nav_content = "perfil"


    def show_last_sorteios(self, *args):
        self.root.ids.list_holder.clear_widgets()
        self.root.ids.list_holder.add_widget(MDList(padding=10))

        for sorteio in self.ultimos:
            self.root.ids.list_holder.children[0].add_widget(
                TwoLineListItem(
                    text=sorteio[0],
                    secondary_text=sorteio[1]
                )
            )

        self.root.ids.nav_drawer.add_widget(
            MDRaisedButton(
                text="VOLTAR",
                md_bg_color=self.theme_cls.primary_color,
                font_size="14dp",
                size_hint=(1, 0.075),
                on_release=self.show_meu_perfil
            )
        )

        self.nav_content = "sorteios"


    def show_configurations(self, *args):
        self.root.ids.list_holder.clear_widgets()
        self.root.ids.list_holder.add_widget(MDList(padding=10))

        self.root.ids.list_holder.children[0].add_widget(ConfigurationItems())

        self.root.ids.nav_drawer.add_widget(
            MDRaisedButton(
                text="VOLTAR",
                md_bg_color=self.theme_cls.primary_color,
                font_size="14dp",
                size_hint=(1, 0.075),
                on_release=self.show_meu_perfil
            )
        )

        self.nav_content = "configs"

    # personaliza????o
    '''
    def set_primary_color(self, obj, color_type, color):
        new_color = self.get_selected_color(obj)

        self.theme_cls.primary_palette = new_color[0]
        self.theme_cls.primary_hue = new_color[1]
        self.data['configs']['color'] = new_color[0]
        self.data['configs']['color_hue'] = new_color[1]
        
    def set_accent_color(self, obj, color_type, color):
        new_color = self.get_selected_color(obj)

        self.theme_cls.accent_palette = new_color[0]
        self.theme_cls.accent_hue = new_color[1]
        self.data['configs']['accent'] = new_color[0]
        self.data['configs']['accent_hue'] = new_color[1] 
    '''
    @autosave
    def swap_colors(self):
        color1 = self.data['configs']['color']
        hue1 = self.data['configs']['color_hue']

        color2 = self.data['configs']['accent']
        hue2 = self.data['configs']['accent_hue']

        self.theme_cls.primary_palette = color2
        self.theme_cls.primary_hue = hue2
        self.data['configs']['color'] = color2
        self.data['configs']['color_hue'] = hue2

        self.theme_cls.accent_palette = color1
        self.theme_cls.accent_hue = hue1
        self.data['configs']['accent'] = color1
        self.data['configs']['accent_hue'] = hue1 


    @autosave
    def change_theme(self, *args):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            self.data['configs']['theme'] = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
            self.data['configs']['theme'] = "Light"


    @autosave
    def change_profile(self, icon, text):
        self.root.ids.avatar.icon = icon
        self.data["configs"]["profile"] = icon
        self.root.ids.avatar_text.text = text
        self.snackbar.dismiss()


    # DIALOGS
    def open_dialog(self, func, *args): # abre dialogs padroes
        if not self.dialog:
            self.dialog = func(self.get_running_app(), *args)
            self.dialog.open()


    def close_dialog(self, *args): # fecha dialogs e reseta pra "None"
        self.dialog.dismiss()
        self.dialog = None


    def close_and_open_dialog(self, func, *args):
        if self.dialog:
            self.close_dialog()

        self.dialog = func(self.get_running_app(), *args)
        self.dialog.open()


    # MENU
    def start_menu(self, items):
        menu = MDDropdownMenu(
            items = [
                {
                    "text": list(items.keys())[i],
                    "viewclass": "MenuItem",
                    "icon": list(items.values())[i],
                    "on_release": lambda x=list(items.keys())[i]: self.menu_callback(x, self.menu.caller),
                } for i in range(len(items))
            ],
            width_mult=2.5,
            max_height="147dp",
            background_color=self.theme_cls.bg_light,
            radius=["2dp"],
            position="bottom",
        )

        return menu


    def menu_bind(self, button):
        self.menu.caller = button
        self.menu.open()


    def menu_callback(self, item, obj):
        self.menu.dismiss()
        self.menu.caller.text = item


    # FILE MANAGER
    def create_file_manager(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
        )


    def open_file_manager(self, select_func):
        self.file_manager.show(self.path)
        self.file_manager.select_path=select_func


    def exit_file_manager(self, *args):
        self.file_manager.close()


    def rename_file(self, file):
        self.open_dialog(
            confirmation_dialog,
            "Ao selecionar um arquivo ele ser?? usado para carregar os dados",
            self.rename_file_confirm,
            file)


    def rename_file_confirm(self, file):
        file_path_list = file.split("/")

        if len(file_path_list) == 2:
            file_path = file_path_list[0] + "/"
            file_name = file_path_list[1]
        else:
            file_name = file_path_list.pop()
            file_path = "/".join(file_path_list) + "/"

        if file_name != self.FILE:
            rename_json(file_path, file_name, self.FILE)

        self.close_dialog()
        self.exit_file_manager()
        self.restart_app()


    def delete_file(self, file):
        self.open_dialog(
            confirmation_dialog,
            f"Voc?? realmente deseja excluir o arquivo?\n\n{file}",
            self.delete_file_confirm,
            file)


    def delete_file_confirm(self, file):
        delete_json(file, "")

        self.close_dialog()
        self.exit_file_manager()


    # COLOR PICKER
    '''
    def open_color_picker(self, palette):
        color_picker = MDColorPicker(
            size_hint=(0.9, 0.9),
            text_button_ok='Selecionar',
            text_button_cancel='Cancelar',
            type_color='HEX',
            )
        color_picker.open()

        if palette == "primary":
            color_picker.bind(on_release=self.set_primary_color,)
        elif palette == "accent":
            color_picker.bind(on_release=self.set_accent_color,)  

    def get_selected_color(self, obj):
        for color in colors:
            for hue in colors[color]:
                if colors[color][hue] == obj.selected_color.upper()[1:7]:
                    return (color, hue)
    '''


    # EASTER EGGS
    @autosave
    def easter_egg(self):
        self.snackbar = Snackbar(
            text='Te amo muito!',
            size_hint_y = 0.1,
            buttons = [
                MDFlatButton(
                    text="num te amo",
                    pos_hint = {"center_y": 0.5, "right": 1},
                    theme_text_color="Custom",
                    text_color="white",
                    on_release=lambda x: self.change_profile("emoticon-sad", "Sabia que vc ia apertar nesse"),
                ),
                MDRaisedButton(
                    text="tbm te amo xuxu",
                    pos_hint = {"center_y": 0.5, "right": 1},
                    on_release=lambda x: self.change_profile("emoticon-excited", "Yeeeey"),
                ),
            ]
        )
        self.snackbar.open()


    # CALLBACKS
    @autosave
    def add_tab(self, obj):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids

        tipo = dialog.tipo_sorteador.text
        title = dialog.new_tab_name.text if dialog.new_tab_name.text else f"Aba {self.num_tabs+1}"
        
        if tipo == "Numero":
            self.root.ids.tab_master.add_widget(TabNumero(title=title, num_tab=self.num_tabs))
            self.data["tabs"].append(
                {
                "title": title,
                "tipo": tipo,
                "minimum": "1",
                "maximum": "100",
                "sorteado": ""
                }
            )

        elif tipo == "Lista":
            self.root.ids.tab_master.add_widget(TabLista(title=title, num_tab=self.num_tabs))
            self.data["tabs"].append(
                {
                "title": title,
                "tipo": tipo,
                "lista": [],
                "sorteado": ""
                }
            )

        elif tipo == "Dado":
            self.root.ids.tab_master.add_widget(TabDado(title=title, num_tab=self.num_tabs))
            self.data["tabs"].append(
                {
                "title": title,
                "tipo": tipo,
                "sorteado": "dice-multiple"
                }
            )

        self.num_tabs +=1
        self.close_dialog()
        self.root.ids.nav_drawer.set_state("toggle")
        Clock.schedule_once(self.change_tab, 0.1)


    @autosave
    def remove_tab(self, *args):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids
        to_remove = dialog.selecionado.text
        index = 0

        for x, tab in enumerate(reversed(dialog.list_manager.children)):
            if tab.text == to_remove:
                dialog.list_manager.remove_widget(tab)
                index = x
                break

        self.data["tabs"].pop(index)

        for tab in self.root.ids.tab_master.get_tab_list():
            self.root.ids.tab_master.remove_widget(tab)

        self.load_tabs()

        dialog.selecionado.text = "Selecione para Remover"

        self.close_dialog()
        self.root.ids.nav_drawer.set_state("toggle")


    def change_tab(self, *args):
        tabs = self.root.ids.tab_master.get_tab_list()
        self.root.ids.tab_master.switch_tab(tabs[-1])


    def save_as_file(self, *args):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids

        name = dialog.new_file_name.text if dialog.new_file_name.text else f"{self.FILE[:-5]} - backup"
        save_json(self.data, self.path, name + ".json")

        self.close_dialog()


    @autosave
    def set_time_format(self, *args):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids
        if not dialog.new_file_name.text:
            return

        self.data["configs"]["time_format"] = dialog.new_file_name.text

        self.close_dialog()


    @autosave
    def edit_meus_sorteios(self, *args):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids
        if not dialog.num_sorteios.text:
            return

        self.data["ultimos"] = self.data["ultimos"][:int(dialog.num_sorteios.text)]
        self.data["configs"]["num_meus_sorteios"] = dialog.num_sorteios.text

        self.close_dialog() 


    @autosave
    def edit_autosave(self, *args):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids

        self.data["configs"]["autosave"] = dialog.checkbox.active

        self.close_dialog() 


    @autosave
    def add_sorteio_json(self, tab, sorteio):
        tab_json = self.data["tabs"][tab.num_tab]
        tab_json["sorteado"] = sorteio
        tab_title = tab_json["title"]

        # texto de cima no item meus sorteios
        if tab_json["tipo"] == "Numero":
            sorteio += f": {tab_json['minimum']} - {tab_json['maximum']}"

        # texto debaixo no item meus sorteios
        current_time = t.strftime(self.data["configs"]["time_format"], t.localtime())
        if len(tab_title) > 14:
            secondary_text = f"{tab_title[:14]}... {current_time}"
        else:
            secondary_text = f"{tab_title}: {current_time}"

        self.ultimos.insert(0, [sorteio, secondary_text])

        # adiciona sorteio no json
        self.data["ultimos"].insert(0, (sorteio, secondary_text))

        # remove ultimo sorteio no json caso tenha excedido
        if len(self.data["ultimos"]) > int(self.data["configs"]["num_meus_sorteios"]):
            self.data["ultimos"].pop()


    @autosave
    def sortear_numero(self, tab):
        numbers = tab.ids.numbers_text.text.split(" ")
        minimum = int(numbers[1])
        maximum = int(numbers[3]) + 1

        sorteio = str(r.randrange(minimum, maximum))
        tab.ids.sorteado.text = sorteio
        self.add_sorteio_json(tab, sorteio)


    @autosave
    def sortear_lista(self, tab):
        try:
            sorteio = r.choice(tab.lista)
        except IndexError:
            sorteio = "Nenhum Item Adicionado"

        tab.ids.sorteado.text = sorteio
        self.add_sorteio_json(tab, sorteio)


    @autosave
    def sortear_dado(self, tab):
        sorteio = f"dice-{r.randrange(1, 7)}"

        tab.ids.sorteado.icon = sorteio
        self.add_sorteio_json(tab, sorteio)


    @autosave
    def edit_numbers(self, obj):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids
        minimum = dialog.minimum.text
        maximum = dialog.maximum.text

        obj.ids.numbers_text.text = f"De {minimum} a {maximum}"
        self.data["tabs"][obj.num_tab]["minimum"] = minimum
        self.data["tabs"][obj.num_tab]["maximum"] = maximum

        self.close_dialog()


    @autosave
    def edit_lista(self, obj):
        items = self.dialog.ids.spacer_top_box.children[0].ids.itens_lista.children
        list_items = [item.text for item in reversed(items)]

        obj.lista = list_items
        self.data["tabs"][obj.num_tab]["lista"] = list_items

        self.close_dialog()


    def text_handle(self, *args):
        for arg in args:
            print(arg)


    '''
    def color_picked(self, color_name, hue, color):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids

        dialog.colors_tab.background_color = color

        print(dialog.picked_color)

    def primary_color(self, *args):
        print(*args)

        self.theme_cls.primary_palette = color
        self.theme_cls.primary_hue = hue
        self.data['configs']['color'] = color
        self.data['configs']['color_hue'] = hue
    '''


    


if __name__ == "__main__":
    r.seed(t.time())
    Sorteador().run()
