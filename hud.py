from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.menu import Menu, MenuItem, BOTTOM, CENTER, RIGHT

from toolbar import *

from cocos.director import director

TOP_BAR_HEIGHT = 32
BOTTOM_BAR_HEIGHT = 32

class LayerMenu(Menu):
    def __init__(self, hud):
        super(LayerMenu, self).__init__()
        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT
        self.font_item['font_size'] = 12
        self.font_item_selected['font_size'] = 14

        self.labels = [i.label for i in hud.editor.layers.get_children() if hasattr(i, 'label')]
        self.items = [MenuItem(i, self.on_quit) for i in self.labels]
        self.create_menu(self.items)
        self.hud = hud

    def on_quit(self):
        self.hud.showingLayerMenu = False
        self.hud.add(self.hud.layerNameLabel)
        self.hud.remove(self)
        self.hud.editor.set_current_layer (self.selected_index)
        self.hud.update()

class HUDLayer(Layer):
    is_event_handler = True
    def __init__(self, editor):
        super(HUDLayer, self).__init__()
        atts = dict(color=(255,255,255,255), font_size=14,
                anchor_x='right', anchor_y='bottom')
        x, y = director.get_window_size()
        self.hud_x = x - 5
        self.hud_y = y - 20
        self.pointerLabel = Label('0,0', position=(self.hud_x, self.hud_y),
                                  **atts)
        self.add(self.pointerLabel, z=1)
        self.layerNameLabel = Label(editor.current_layer.label,
                                    position=(self.hud_x - 140, self.hud_y), **atts)
        self.add(self.layerNameLabel, z=1)
        self.editor = editor
        self.showingLayerMenu = False

        translucent = ColorLayer( 64,64,64,192, x, TOP_BAR_HEIGHT)
        translucent.position = (0,y-TOP_BAR_HEIGHT)
        self.add( translucent )

        translucent = ColorLayer( 64,64,64,192, x, BOTTOM_BAR_HEIGHT)
        translucent.position = (0,0)
        self.add( translucent )


    def update(self):
        x, y = self.editor.layers.pointer_to_world(*self.editor.mouse_position)
        self.pointerLabel.element.text = "%d,%d" % (x,y)
        self.layerNameLabel.element.text = self.editor.current_layer.label

    def on_mouse_press(self, x, y, button, modifiers):
        X, Y = self.layerNameLabel.position
        if X - 70 < x < X and Y < y < Y + 20:
            if not self.showingLayerMenu:
                self.remove(self.layerNameLabel)
                self.layerMenu = LayerMenu(self)
                self.layerMenu.position = -140, 0
                self.add(self.layerMenu)
                self.showingLayerMenu = True

