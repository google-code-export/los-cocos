#
# Python Interpreter
# 95% of the code from 'Bruce: the presentation tool' by Richard Jones
# http://code.google.com/p/bruce-tpt/
#
#
import sys
import os
import code

import pyglet
from pyglet import graphics
from pyglet import text
from pyglet.text import caret, document, layout

import cocos
from base_layers import Layer

__all__ = ['PythonInterpreterLayer']

class Output:
    def __init__(self, display, realstdout):
        self.out = display
        self.realstdout = realstdout
        self.data = ''

    def write(self, data):
        self.out(data)

class MyInterpreter(code.InteractiveInterpreter):
    def __init__(self, locals, display):
        self.write = display
        code.InteractiveInterpreter.__init__(self, locals=locals)

    def execute(self, input):
        old_stdout = sys.stdout
        sys.stdout = Output(self.write, old_stdout)
        more = self.runsource(input)
        sys.stdout = old_stdout
        return more

class PythonInterpreterLayer(Layer):
    '''Runs an interactive Python interpreter.
    '''

    cfg = {'code.font_name':'Courier New',
            'code.font_size':12,
            'code.color':(200,200,200,255),
            'caret.color':(200,200,200)
            }

    name = 'py'

    prompt = ">>> "
    prompt_more = "... "

    def __init__(self):
        super(PythonInterpreterLayer, self).__init__()

        self.content = self.prompt
        self.interpreter = MyInterpreter(locals(), self._write)

        self.current_input = []

        self.history = ['']
        self.history_pos = 0

#        assert self.cfg['auto'] is False, 'not implemented yet'

    def on_enter(self):
        super(PythonInterpreterLayer, self).on_enter()

        vw,vh = cocos.director.director.get_window_size()

        # format the code
        self.document = document.FormattedDocument(self.content)
        self.document.set_style(0, len(self.document.text), {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })

        self.batch = graphics.Batch()

        # generate the document
        self.layout = layout.IncrementalTextLayout(self.document,
            vw, vh, multiline=True, batch=self.batch)
        self.layout.valign = 'top'

        self.caret = caret.Caret(self.layout, color=self.cfg['caret.color'] )
        self.caret.on_activate()

        self.on_resize(vw, vh)

        self.start_of_line = len(self.document.text)

    def on_resize(self, vw, vh):
        self.viewport_width, self.viewport_height = vw, vh

        self.layout.begin_update()
        self.layout.height = vh
        self.layout.x = 2
        self.layout.width = vw - 4
        self.layout.y = vh
        self.layout.end_update()
        self.caret.position = len(self.document.text)

    def on_exit(self):
        self.content = self.document.text
        self.document = None
        self.title_label = None
        self.layout = None
        self.batch = None
        self.caret = None

    doing_more = False
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            return self.caret.on_text('\t')
        elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.NUM_ENTER):
            # write the newline
            self._write('\n')

            line = self.document.text[self.start_of_line:]
            if line == 'help()':
                line = 'print "help() not supported, sorry!"'
            self.current_input.append(line)
            self.history_pos = len(self.history)
            if line.strip():
                self.history[self.history_pos-1] = line.strip()
                self.history.append('')
            more = self.interpreter.execute('\n'.join(self.current_input))
            if self.doing_more and not line.strip():
                self.doing_more = False
            more = more or self.doing_more
            if not more:
                self.current_input = []
                self._write(self.prompt)
            else:
                self.doing_more = True
                self._write(self.prompt_more)
            self.start_of_line = len(self.document.text)
            self.caret.position = len(self.document.text)
        elif symbol == pyglet.window.key.SPACE:
            pass
        else:
            return pyglet.event.EVENT_UNHANDLED
        return pyglet.event.EVENT_HANDLED

    def on_text(self, symbol):
        # squash carriage return - we already handle them above
        if symbol == '\r':
            return pyglet.event.EVENT_HANDLED

        self._scroll_to_bottom()
        return self.caret.on_text(symbol)

    def on_text_motion(self, motion):
        at_sol = self.caret.position == self.start_of_line

        if motion == pyglet.window.key.MOTION_UP:
            # move backward in history, storing the current line of input
            # if we're at the very end of time
            line = self.document.text[self.start_of_line:]
            if self.history_pos == len(self.history)-1:
                self.history[self.history_pos] = line
            self.history_pos = max(0, self.history_pos-1)
            self.document.delete_text(self.start_of_line,
                len(self.document.text))
            self._write(self.history[self.history_pos])
            self.caret.position = len(self.document.text)
        elif motion == pyglet.window.key.MOTION_DOWN:
            # move forward in the history
            self.history_pos = min(len(self.history)-1, self.history_pos+1)
            self.document.delete_text(self.start_of_line,
                len(self.document.text))
            self._write(self.history[self.history_pos])
            self.caret.position = len(self.document.text)
        elif motion == pyglet.window.key.MOTION_BACKSPACE:
            # can't delete the prompt
            if not at_sol:
                return self.caret.on_text_motion(motion)
        elif motion == pyglet.window.key.MOTION_LEFT:
            # can't move back beyond start of line
            if not at_sol:
                return self.caret.on_text_motion(motion)
        elif motion == pyglet.window.key.MOTION_PREVIOUS_WORD:
            # can't move back word beyond start of line
            if not at_sol:
                return self.caret.on_text_motion(motion)
        else:
            return self.caret.on_text_motion(motion)
        return pyglet.event.EVENT_HANDLED

    def _write(self, s):
        self.document.insert_text(len(self.document.text), s, {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        # on key press always move the view to the bottom of the screen
        if self.layout.height < self.layout.content_height:
            self.layout.valign = 'bottom'
            self.layout.y = 0
            self.layout.view_y = 0
        if self.caret.position < self.start_of_line:
            self.caret.position = len(self.document.text)

    def on_draw(self):
        self.batch.draw()
