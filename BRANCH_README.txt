short lived branch to give cocos sprites similar performance to pyglet sprites.
see details at:

    (english) : http://progcc-en.blogspot.com/2010/11/sprite-performance-in-cocos-and-pyglet.html
    (castellano) : http://progcc.blogspot.com/2010/11/performance-de-sprites-con-cocos-y.html

0.  base measures
    conditions: no apps running except opera browser with gmail, two explorer
    windows, this file opened in IDLE

    test version: wk_benchmark, revision
    >hg summary
    parent: 11:5d9cfbac0e52 tip
    The test code was derived from the tests linked in the blog; now has
    better support for parametrization and automatic data collection.
    Later I will create a public repository for this software.

    performance data, 3 runs each:
    
    sp_num = [50, 100, 250, 500, 750, 1000]
    # cocos base fps
    bcc1 = [190.99, 128.83, 61.84, 33.63, 22.83, 17.31 ]
    bcc2 = [193.85, 125.60, 62.92, 33.78, 23.05, 17.35 ]
    bcc3 = [200.94, 128.66, 63.16, 33.93, 23.19, 17.50 ]

    # pyglet base fps
    bpg1 = [277.27, 195.69, 100.89, 56.72, 39.06, 30.17]
    bpg2 = [279.45, 192.22, 101.10, 56.34, 38.94, 29.65]
    bpg3 = [280.12, 191.41,  99.99, 56.09, 39.00, 29.71]


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

    # needed soo that B getter-setter are called.
    # if using the lambda variant in A then we can spare this line to
    # the same effect.
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



So, lets try to eliminate lambdas in cocosnode.py, see if it is worth from a
performance POV, then look if some subclass needs to compensate for the change

1. apply only to x , y, 
sprites dont move, performance data:
[294.04562868598919, 210.49968441056549, 115.80268075475163, 67.490838791357845,
 47.037630668969683, 36.092639186021188]

numbers are near the pyglet ones.

2. apply only to position
sprites move
[218.36818385133762, 139.32775631094015, 68.184896609585664, 37.255746897565629,
 25.564523900737559, 19.381426040843117]
slightly better times

3. position, rotation, scale only
looks good
[216.25496566426636, 140.82113828637051, 69.627185133273713, 37.469568018575409,
 25.545817331133108, 19.491706791874407]
slightly better times (if the test changed rotation and scale in each frame the
time diferences should go up)

3.
So, lets examine cocos sprite.py to get rid of lambas in x, y.
it redefines setters for all the props, it does not rebind the property
lets eliminate lambas and add the property rebind in sprite
Simply adding
w = property( _get_w, _set_w)
in sprites.py don't work:
...
  File "D:\cocos_pristine\b_lambda\cocos\sprite.py", line 85, in <module>
    class Sprite( BatchableNode, pyglet.sprite.Sprite):
  File "D:\cocos_pristine\b_lambda\cocos\sprite.py", line 205, in Sprite
    x = property(_get_x, _set_x, doc="The x coordinate of the object")
NameError: name '_get_x' is not defined

Replacing _get_x -> self.get_x gives 'NameError: name 'self' is not defined'

Copying the getter from CocosNode works, and:

[206.49579486268505, 134.30847113014391, 65.013507505134541, 35.061074784665053,
 24.03420352144245, 18.106053139456826]

hmmm, barely noticeabelly

4. alternative in 3 to copyng the getters:

    w = property( cocosnode.CocosNode._get_w, _set_w)

works, and:
[205.32544270382397, 133.11523562105674, 65.317696981517386, 35.169177814207032,
 24.319011559931582, 18.292292042922231]
very near 3.

5. sprite.py uses CocosNode.get_local_transform; here we replace
self.rotation with self._rotation , should give a very small boost

6. replacing BatchableNode with cocosnode.CocosNode in the cocos sprite
getters setters
[206.5708367460185, 132.33029169842717, 64.896211540920945, 34.866130534491688,
23.795839944570126, 18.174577383844259]
about the same

7. replacing
cocosnode.CocosNode._set_w(self,a)
with
self._w = a
in properties of cocos sprites.py (except position)
 [210.40240806871765, 137.35088062879066, 66.946502677574969, 36.424776883214605,
 24.796184997616194, 18.836214339612823]
improves very little and we are not seting the flags about transform dirty
Revert this ones

8. replace in the props
        pyglet.sprite.Sprite._set_w(self, a)
        cocosnode.CocosNode._set_w(self,a)

with
        cocosnode.CocosNode._set_w(self,a)
        self._update_position()
[201.2265757216561, 127.25881525913073, 61.034463834539721, 32.640224612460294,
22.044722815752777, 16.815617113594804]
and
[200.78321493548475, 127.58978168974078, 61.505091043700517, 32.763003849603386,
 22.316811034336439, 16.779340727528634]
we lose a bit from 3.

9. en cocosnode.py, prop position change
        self.x, self.y = x,y
to
        self._x = x
        self._y = y
[243.35991812721926, 183.19512904391129, 96.11161106612505, 53.693453546986078,
37.277618517983569, 28.321603538110502]
wheee! much better
additional runs
[265.10653784654556, 181.51742390850771, 95.694040051925441, 53.368310923605421,
 37.112011985287879, 28.54995825632291]
[264.64155983056935, 182.47568395779234, 95.281922640136827, 53.421225868100251,
 37.106671699317438, 28.358927204471467]

10. copy cocosnode.py to "Copia de cocosnode.py", revert all cocos (svn revert . -R)
to trunk and apply only the change in 9.
high fps but sprites dont move
hmmm. pyglet uses the lambda style both for getter and setter 


11. lets define the setters in cocos sprite without calling any property setter
in both cocosnode nor pyglet sprite; that should be the max gain in cutting
property overhead
sprites move,
[267.51585432698954, 184.09189284721785, 97.989612471025765, 54.5990983439888, 3
8.341489028332155, 29.296550989331539]
[247.50540297465244, 186.90390280017823, 98.673997270211913, 55.787429600138424,
 38.311327498728247, 29.354195319685864]
[263.62161156064809, 188.10170298885342, 99.282605610627343, 55.034909987270893,
 38.135864014881392, 29.448550069022467]

12. and then over 11 eliminate lambdas in cocosnode and rebind the props in
cocos sprite
[265.81608404708254, 187.7608546077463, 99.243281062593013, 55.623499058305363,
38.289863872062746, 29.392568117109363]
[273.06598526472976, 188.54320637048841, 100.71152822603773, 56.083016988765365,
 39.067920932654374, 29.928690422059773]
[272.4301581903523, 187.96538185872757, 99.636077372575926, 55.838245300506699,
38.587103643659091, 29.645419671233984]

13. over 12.
    in cocosnode get_local_transform replace
    self.rotation -> self._rotation
    self.transform_anchor_x -> self._transform_anchor_x
    self.transform_anchor_y -> self._transform_anchor_y

[273.61285228361481, 183.54835677361038, 99.925204307926535, 56.158204488240152,
 39.123557179878247, 29.974100000521609]
[264.06079438038012, 188.89916420863551, 99.845230076552582, 56.288570634568771,
 38.899149611212579, 29.702831994092222]
[267.40286950626808, 185.12734883883047, 99.740777318873086, 55.769331916236069,
 38.949470526926191, 29.862979254790581]
only a bit better
-------------

Best of three stats:

# pyglet base
bpg =  [280.12, 195.69, 101.09999999999999, 56.719999999999999, 39.060000000000002, 30.170000000000002]
# cocos base
bcc =  [200.94, 128.83000000000001, 63.159999999999997, 33.93, 23.190000000000001, 17.5]
# cocos try 9
cc09 = [265.10653784654556, 183.19512904391129, 96.11161106612505, 53.693453546986078, 37.277618517983569, 28.54995825632291]
# cocos try 11
cc11 = [267.51585432698954, 188.10170298885342, 99.282605610627343, 55.787429600138424, 38.341489028332155, 29.448550069022467]
# cocos try 12
cc12 = [273.06598526472976, 188.54320637048841, 100.71152822603773, 56.083016988765365, 39.067920932654374, 29.928690422059773]
# cocos try 13
cc13 = [273.61285228361481, 188.89916420863551, 99.925204307926535, 56.288570634568771, 39.123557179878247, 29.974100000521609]


-------------

Solution min property overhead (ie 13):

PROS:
    much faster than cocos trunk, very near pyglet performance

    code in cocos sprite.py easier to follow: properties dont call the base
    classes getters - setters, the explicit g/setters shows at once what
    happens when a property is set.

CONS:
    Code in cocos sprites need to follow changes in pyglet sprites and
    cocosnode.py (this is a cocos maintainer problem)

    The 'overridable style for properties' (using lambdas) is left aside.
    It was used in cocos trunk, (some user code can be incompatible)
    it is used in pyglet sprites. ( will be unexpected for pyglet users)
    Mitigating this, overriding the properties getters/setters is unusual
    in user code.

-------------

Alternative:

I think the bulk of performance loss is not the lambda call overhead, but that
in the cascading calls somewhere _update_position() is called more than one
time, probably in cocosnode _set_position



    
-------------
Para sprites que cambian mucho las properties en cada frame:
poner un set de dirties en el batch y antes del draw llamar a undirty para cada
elemento del set ?

Si usan un estilo mvc donde el sprite del view se actualiza solo una vez por
frame casi no hace falta, aunque alli hay que ver si podemos poner un method
alternativo que actualize todas las props necesarias pero llame a
update_position solo una vez

-------------

