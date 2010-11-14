short lived branch to give cocos sprites similar performance to pyglet sprites.
see details at:

    (english) : http://progcc-en.blogspot.com/2010/11/sprite-performance-in-cocos-and-pyglet.html
    (castellano) : http://progcc.blogspot.com/2010/11/performance-de-sprites-con-cocos-y.html

1. profiling with cProfile and playing with RunSnakeRun, a cProfile stats
   visualizer, sugest that some lambas in cocosnode.py eats a portion of
   performance.
   We have lambdas in:
       properties x, y, position, scale, rotation

    The usage pattern is the same:
        ( w a placeholder for the properties listed before )
        a) define CocosNode methods _get_w , _set_w
        b) define the property by
        w = property( _get_w, lambda self,p:self._set_w(p))

Why not
    w = property( _get_w, _set_w)
?

The only difference in behavior that I see is related to inheritance:

# --> begin script
class A(object):
    def set_x(self, x):
        print 'A setter'
        self._x = x

    def get_x(self):
        print 'A getter'
        return self._x

    x = property( get_x, set_x )

class B(A):
    def set_x(self, x):
        print 'B setter'
        self._x = x

    def get_x(self):
        #z = super(B,self).get_x() # como se espera esta linea llama get_x de A
        print 'B getter'
        return self._x

    # without this the A getter-setter are called
    # sin esto se llaman a los getters-setters de A
    x = property( get_x, set_x )

print 'set and print b.x'
b = B()
b.x = 22
print b.x

print '\nset and print a.x'
a = A()
a.x = 11
print a.x

# <- end script

Output with the second x = property commented out:
set and print b.x
A setter
A getter
22

set and print a.x
A setter
A getter
11

---
Output with the second x = property *not* commented out:

set and print b.x
B setter
B getter
22

set and print a.x
A setter
A getter
11
---

So, lets try to eliminate lambdas in cocosnode.py, then look if some
subclass needs to compensate for the change

