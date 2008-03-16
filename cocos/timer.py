

__all__ = ['Timer']

from pyglet import font
import director



class Timer(object):
    def __init__(self):

        x,y = director.director.get_window_size()
        x -= 140
        y -= 48

        self.running = True
        self.down = True

        font.add_directory('.')
        aFont = font.load( 'DS-Digital Bold', 48, bold=True )
        self.label = font.Text( aFont, '00:00', x=x,y=y)
        self.reset()
        
    def reset(self):
        self.time = 60 * 5
        self.label.color = (0.5, 0.5, 0.5, 0.5)

    def step(self, dt):
        if self.running:
            if self.down:
                self.time -= dt
            else:
                self.time += dt

            if self.time < 4:
                self.down = False

            m, s = divmod(self.time, 60)
            self.label.text = '%02d:%02d' % (m, s)
            if self.time < 30:
                self.label.color = (1.0,0.0,0.0,0.5)
            self.label.draw()
