# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math

import pyglet
from pyglet.window import key

import cocos
from cocos import tiles

class CarSprite(cocos.sprite.Sprite):
    speed = 0
    def update(self, dt):
        # handle input and move the car
        self.rotation += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        speed = self.speed
        speed += (keyboard[key.UP] - keyboard[key.DOWN]) * 50
        if speed > 200: speed = 200
        if speed < -100: speed = -100
        self.speed = speed
        r = math.radians(self.rotation)
        s = dt * speed
        self.x += math.sin(r) * s
        self.y += math.cos(r) * s
        manager.set_focus(self.x, self.y)

        
        
if __name__ == "__main__":
    from cocos.director import director
    director.init(width=600, height=300)

    car_layer = tiles.ScrollableLayer()
    car = CarSprite('car.png')
    car.schedule(car.update)
    car_layer.add(car)

    manager = tiles.ScrollingManager()
    test_layer = tiles.load('road-map.xml')['map0']
    manager.append(test_layer)
    manager.append(car_layer)

    main_scene = cocos.scene.Scene(test_layer, car_layer)
    
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    director.run(main_scene)
