# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
'''Particle system'''

import random
import pyglet
from pyglet.gl import *
import math
import copy
import numpy
import ctypes

from cocosnode import CocosNode
from euclid import Point2

rand = lambda: random.random() * 2 - 1

# PointerToNumpy by Gary Herron
# from pyglet's user list
def PointerToNumpy(a, ptype=ctypes.c_float):
    a = numpy.ascontiguousarray(a)           # Probably a NO-OP, but perhaps not
    return a.ctypes.data_as(ctypes.POINTER(ptype)) # Ugly and undocumented! 

class Color( object ):
    def __init__( self, r,g,b,a ):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_array(self):
        return self.r, self.g, self.b, self.a


class ParticleSystem( CocosNode ):
    def __init__(self, total_particles, texture=None):
        super(ParticleSystem,self).__init__()

        self.id = 0

        #: is the particle system active ?
        self.active = True

        #: duration in seconds of the system. -1 is infinity
        self.duration = 0
        #: time elapsed since the start of the system (in seconds)
        self.elapsed = 0

        #: Gravity of the particles
        self.gravity = Point2(0.0, 0.0)

        #: position is from "superclass" CocosNode
        #: Position variance
        self.pos_var = Point2(0.0, 0.0)

        #: The angle (direction) of the particles measured in degrees
        self.angle = 0.0
        #: Angle variance measured in degrees;
        self.angle_var = 0.0

        #: The speed the particles will have.
        self.speed = 0.0
        #: The speed variance
        self.speed_var = 0.0

        #: Tangential acceleration
        self.tangential_accel = 0.0
        #: Tangential acceleration variance
        self.tangential_accel_var = 0.0

        #: Radial acceleration
        self.radial_accel = 0.0
        #: Radial acceleration variance
        self.radial_accel_var = 0.0

        #: Size of the particles
        self.size = 0.0
        #: Size variance
        self.size_var = 0.0

        #: Start color of the particles
        self.start_color = Color(0.0,0.0,0.0,0.0)
        #: Start color variance
        self.start_color_var = Color(0.0,0.0,0.0,0.0)
        #: End color of the particles
        self.end_color = Color(0.0,0.0,0.0,0.0)
        #: End color variance
        self.end_color_var = Color(0.0,0.0,0.0,0.0)

        #: Maximum particles
        self.total_particles = total_particles
        #: Count of particles
        self.particle_count = 0

        # particles
        # position x 2
        self.pas_pos = numpy.zeros( (self.total_particles, 2), numpy.float32 )
        # direction x 2
        self.pas_dir = numpy.zeros( (self.total_particles, 2), numpy.float32 )
        # rad accel x 1
        self.pas_rad = numpy.zeros( (self.total_particles, 1), numpy.float32 )
        # tan accel x 1
        self.pas_tan = numpy.zeros( (self.total_particles, 1), numpy.float32 )
        # gravity x 2
        self.pas_grav = numpy.zeros( (self.total_particles, 2), numpy.float32 )
        # colors x 4
        self.pas_color = numpy.zeros( (self.total_particles, 4), numpy.float32 )
        # delta colors x 4
        self.pas_delta_color = numpy.zeros( (self.total_particles, 4), numpy.float32 )
        # life x 1
        self.pas_life = numpy.zeros( (self.total_particles, 1), numpy.float32 )
        self.pas_life.fill(-1.0)
        # size x 1
        self.pas_size = numpy.zeros( (self.total_particles, 1), numpy.float32 )

        #: How many particles can be emitted per second
        self.emission_rate = 0
        self.emit_counter = 0
        
        #: How many seconds will the particle live
        self.life = 0
        #: Life variance
        self.life_var = 0


        # TEXTURE RELATED

        #: texture id of the particle
        if not texture:
            texture = pyglet.resource.image('fire.png').texture

        self.texture = texture

        self.schedule( self.step )

    def on_enter( self ):
        super( ParticleSystem, self).on_enter()
        self.add_particle()

    def draw( self ):
        glPushMatrix()
        self.transform()

        glPointSize( self.size )

        vtr = PointerToNumpy( self.pas_pos )
        color = PointerToNumpy( self.pas_color )

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id )

        glEnable(GL_POINT_SPRITE)
        glTexEnvi( GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE )

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2,GL_FLOAT,0,vtr)

        glEnableClientState(GL_COLOR_ARRAY);
        glColorPointer(4,GL_FLOAT,0,color);

        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE);

        glDrawArrays(GL_POINTS, 0, self.total_particles);

        glPopAttrib()

        # unbind
        glDisableClientState(GL_VERTEX_ARRAY);
        glDisableClientState(GL_COLOR_ARRAY);
        glDisable(GL_TEXTURE_2D);
        glDisable(GL_POINT_SPRITE);

        glPopMatrix()


    def step( self, delta ):
        if self.active:
            rate = 1.0 / self.emission_rate
            self.emit_counter += delta

#            if random.random() < 0.01:
#                delta += 0.5

            self.particle_count = sum( self.pas_life >= 0 )

            while self.particle_count < self.total_particles and self.emit_counter > rate:
                self.add_particle()
                self.emit_counter -= rate

            self.elapsed += delta

            if self.duration != -1 and self.duration < self.elapsed:
                self.stop_system()

        self.update_particles( delta )

    def add_particle( self ):
        self.init_particle()
        self.particle_count += 1

    def stop_system( self ):
        self.active = False
        self.elapsed= self.duration
        self.emit_counter = 0

    def reset_system( self ):
        self.elapsed= self.duration
        self.emit_counter = 0

    def update_particles( self, delta ):


        # radial: posx + posy
        norm = numpy.sqrt( self.pas_pos[:,0] ** 2 + self.pas_pos[:,1] ** 2 )
        # XXX prevent div by 0
        norm = numpy.select( [norm==0], [0.0000001], default=norm )
        posx = self.pas_pos[:,0] / norm
        posy = self.pas_pos[:,1] / norm

        radial = numpy.array( [posx, posy] )
        tangential = numpy.array( [-posy, posx] )

        # update dir
        radial = numpy.swapaxes(radial,0,1)
        radial *= self.pas_rad
        tangential = numpy.swapaxes(tangential,0,1)
        tangential *= self.pas_tan

        self.pas_dir +=  (tangential + radial + self.pas_grav) * delta

        # update pos with updated dir
        self.pas_pos += self.pas_dir * delta

        # life
        self.pas_life -= delta


        # color
        self.pas_color += self.pas_delta_color * delta

        # if life < 0, set alpha in 0
        self.pas_color[:,3] = numpy.select( [self.pas_life[:,0] < 0], [0], default=self.pas_color[:,3] )

#        print self.particles[0]
#        print self.pas[0,0:4]

    def init_particle( self ):
        # position
#        p=self.particles[idx]

        a = self.pas_life < 0
        idxs = a.nonzero()

        idx = -1

        if len(idxs[0]) > 0:
            idx = idxs[0][0] 
        else:
            raise Exception("No empty particle")

        # position
        self.pas_pos[idx][0] = self.pos_var.x * rand()
        self.pas_pos[idx][1] = self.pos_var.y * rand()


        a = math.radians( self.angle + self.angle_var * rand() )
        v = Point2( math.cos( a ), math.sin( a ) )
        s = self.speed + self.speed_var * rand()

        dir = v * s

        # direction
        self.pas_dir[idx][0] = dir.x
        self.pas_dir[idx][1] = dir.y

        # radial accel
        self.pas_rad[idx] = self.radial_accel + self.radial_accel_var * rand()


        # tangential accel
        self.pas_tan[idx] = self.tangential_accel + self.tangential_accel_var * rand()
        
        # life
        life = self.pas_life[idx] = self.life + self.life_var * rand()

        # Color
        # start
        sr = self.start_color.r + self.start_color_var.r * rand()
        sg = self.start_color.g + self.start_color_var.g * rand()
        sb = self.start_color.b + self.start_color_var.b * rand()
        sa = self.start_color.a + self.start_color_var.a * rand()

        self.pas_color[idx][0] = sr
        self.pas_color[idx][1] = sg
        self.pas_color[idx][2] = sb
        self.pas_color[idx][3] = sa

        # end
        er = self.end_color.r + self.end_color_var.r * rand()
        eg = self.end_color.g + self.end_color_var.g * rand()
        eb = self.end_color.b + self.end_color_var.b * rand()
        ea = self.end_color.a + self.end_color_var.a * rand()

        delta_color_r = (er - sr) / life
        delta_color_g = (eg - sg) / life
        delta_color_b = (eb - sb) / life
        delta_color_a = (ea - sa) / life

        self.pas_delta_color[idx][0] = delta_color_r
        self.pas_delta_color[idx][1] = delta_color_g
        self.pas_delta_color[idx][2] = delta_color_b
        self.pas_delta_color[idx][3] = delta_color_a

        # size
        self.pas_size[idx] = self.size + self.size_var * rand()

        # gravity
        self.pas_grav[idx][0] = self.gravity.x
        self.pas_grav[idx][1] = self.gravity.y


class Fireworks( ParticleSystem ):
    def __init__( self ):
        super( Fireworks, self).__init__(4000)

        # duration
        self.duration = -1

        # gravity
        self.gravity.x = 0
        self.gravity.y = -90

        # angle
        self.angle = 90
        self.angle_var = 20

        # radial
        self.radial_accel = 0
        self.radial_accel_var = 0

        # speed of particles
        self.speed = 180
        self.speed_var = 50

        # emitter position
        self.x = 320
        self.y = 160

        # life of particles
        self.life = 3.5
        self.life_var = 1

        # emits per frame
        self.emission_rate = self.total_particles / self.life

        # color of particles
        self.start_color.r = 0.5
        self.start_color.g = 0.5
        self.start_color.b = 0.5
        self.start_color.a = 1.0
        self.start_color_var.r = 0.5
        self.start_color_var.g = 0.5
        self.start_color_var.b = 0.5
        self.start_color_var.a = 0.1
        self.end_color.r = 0.1
        self.end_color.g = 0.1
        self.end_color.b = 0.1
        self.end_color.a = 0.2
        self.end_color_var.r = 0.1
        self.end_color_var.g = 0.1
        self.end_color_var.b = 0.1
        self.end_color_var.a = 0.2

        # size, in pixels
        self.size = 8.0
        self.size_var = 2.0


class Explosion( ParticleSystem ):
    def __init__( self ):
        super( Explosion, self).__init__(700)

        # duration
        self.duration = 0.1

        # gravity
        self.gravity.x = 0
        self.gravity.y = -90.0

        # angle
        self.angle = 90.0
        self.angle_var = 360.0

        # radial
        self.radial_accel = 0
        self.radial_accel_var = 0

        # speed of particles
        self.speed = 70.0
        self.speed_var = 40.0

        # emitter position
        self.x = 320.0
        self.y = 240.0
        self.pos_var.x = 0
        self.pos_var.y = 0

        # life of particles
        self.life = 5.0
        self.life_var = 2.0

        # emits per frame
        self.emission_rate = self.total_particles / self.duration

        # color of particles
        self.start_color.r = 0.7
        self.start_color.g = 0.2
        self.start_color.b = 0.1
        self.start_color.a = 1.0
        self.start_color_var.r = 0.5
        self.start_color_var.g = 0.5
        self.start_color_var.b = 0.5
        self.start_color_var.a = 0.0
        self.end_color.r = 0.5
        self.end_color.g = 0.5
        self.end_color.b = 0.5
        self.end_color.a = 0.0
        self.end_color_var.r = 0.5
        self.end_color_var.g = 0.5
        self.end_color_var.b = 0.5
        self.end_color_var.a = 0.0

        # size, in pixels
        self.size = 15.0
        self.size_var = 10.0


class Fire( ParticleSystem ):

    def __init__( self ):
        super( Fire, self).__init__(250)

        # duration
        self.duration = -1

        # gravity
        self.gravity.x = 0.
        self.gravity.y = 0.0

        # angle
        self.angle = 90.0
        self.angle_var = 20.0

        # radial
        self.radial_accel = 0
        self.radial_accel_var = 0

        # speed of particles
        self.speed = 70.0
        self.speed_var = 40.0

        # emitter position
        self.x = 320.0
        self.y = 0.0
        self.pos_var.x = 40
        self.pos_var.y = 20

        # life of particles
        self.life = 2.0
        self.life_var = 1.0

        # emits per frame
        self.emission_rate = self.total_particles / self.life

        # color of particles
        self.start_color.r = 0.76
        self.start_color.g = 0.25
        self.start_color.b = 0.12
        self.start_color.a = 1.0
        self.start_color_var.r = 0.0
        self.start_color_var.g = 0.0
        self.start_color_var.b = 0.0
        self.start_color_var.a = 0.0
        self.end_color.r = 0.0
        self.end_color.g = 0.0
        self.end_color.b = 0.0
        self.end_color.a = 1.0
        self.end_color_var.r = 0.0
        self.end_color_var.g = 0.0
        self.end_color_var.b = 0.0
        self.end_color_var.a = 0.0

        # size, in pixels
        self.size = 100.0
        self.size_var = 10.0


class Flower( ParticleSystem ):

    def __init__( self ):

        super( Flower, self).__init__(500)

        # duration
        self.duration = -1

        # gravity
        self.gravity.x = 0.
        self.gravity.y = 0.0

        # angle
        self.angle = 90.0
        self.angle_var = 360.0

        # speed of particles
        self.speed = 80.0
        self.speed_var = 10.0

        # radial
        self.radial_accel = -60
        self.radial_accel_var = 0

        # tangential
        self.tangential_accel = 15.0
        self.tangential_accel_var = 0.0


        # emitter position
        self.x = 320.0
        self.y = 240.0
        self.pos_var.x = 0
        self.pos_var.y = 0

        # life of particles
        self.life = 4.0
        self.life_var = 1.0

        # emits per frame
        self.emission_rate = self.total_particles / self.life

        # color of particles
        self.start_color.r = 0.5
        self.start_color.g = 0.5
        self.start_color.b = 0.5
        self.start_color.a = 1.0
        self.start_color_var.r = 0.5
        self.start_color_var.g = 0.5
        self.start_color_var.b = 0.5
        self.start_color_var.a = 0.0
        self.end_color.r = 0.0
        self.end_color.g = 0.0
        self.end_color.b = 0.0
        self.end_color.a = 1.0
        self.end_color_var.r = 0.0
        self.end_color_var.g = 0.0
        self.end_color_var.b = 0.0
        self.end_color_var.a = 0.0

        # size, in pixels
        self.size = 30.0
        self.size_var = 0.0

class Sun( ParticleSystem ):

    def __init__( self ):
        super( Sun, self).__init__(350)

        # duration
        self.duration = -1

        # gravity
        self.gravity.x = 0.0
        self.gravity.y = 0.0

        # angle
        self.angle = 90.0
        self.angle_var = 360.0

        # speed of particles
        self.speed = 20.0
        self.speed_var = 5.0

        # radial
        self.radial_accel = 0
        self.radial_accel_var = 0

        # tangential
        self.tangential_accel = 0.0
        self.tangential_accel_var = 0.0


        # emitter position
        self.x = 320.0
        self.y = 240.0
        self.pos_var.x = 0
        self.pos_var.y = 0

        # life of particles
        self.life = 1.0
        self.life_var = 0.5

        # emits per frame
        self.emission_rate = self.total_particles / self.life

        # color of particles
        self.start_color.r = 0.75
        self.start_color.g = 0.25
        self.start_color.b = 0.12
        self.start_color.a = 1.0
        self.start_color_var.r = 0.0
        self.start_color_var.g = 0.0
        self.start_color_var.b = 0.0
        self.start_color_var.a = 0.0
        self.end_color.r = 0.0
        self.end_color.g = 0.0
        self.end_color.b = 0.0
        self.end_color.a = 1.0
        self.end_color_var.r = 0.0
        self.end_color_var.g = 0.0
        self.end_color_var.b = 0.0
        self.end_color_var.a = 0.0

        # size, in pixels
        self.size = 30.0
        self.size_var = 10.0


class Spiral( ParticleSystem ):

    def __init__( self ):
        super( Spiral, self).__init__(500)

        # duration
        self.duration = -1

        # gravity
        self.gravity.x = 0.0
        self.gravity.y = 0.0

        # angle
        self.angle = 90.0
        self.angle_var = 0.0

        # speed of particles
        self.speed = 150.0
        self.speed_var = 0.0

        # radial
        self.radial_accel = -380
        self.radial_accel_var = 0

        # tangential
        self.tangential_accel = 45.0
        self.tangential_accel_var = 0.0

        # emitter position
        self.x = 320.0
        self.y = 240.0
        self.pos_var.x = 0
        self.pos_var.y = 0

        # life of particles
        self.life = 12.0
        self.life_var = 0.0

        # emits per frame
        self.emission_rate = self.total_particles / self.life

        # color of particles
        self.start_color.r = 0.5
        self.start_color.g = 0.5
        self.start_color.b = 0.5
        self.start_color.a = 1.0
        self.start_color_var.r = 0.5
        self.start_color_var.g = 0.5
        self.start_color_var.b = 0.5
        self.start_color_var.a = 0.0
        self.end_color.r = 0.5
        self.end_color.g = 0.5
        self.end_color.b = 0.5
        self.end_color.a = 1.0
        self.end_color_var.r = 0.5
        self.end_color_var.g = 0.5
        self.end_color_var.b = 0.5
        self.end_color_var.a = 0.0

        # size, in pixels
        self.size = 20.0
        self.size_var = 10.0


class Meteor( ParticleSystem ):

    def __init__( self ):
        super( Meteor, self).__init__(150)

        # duration
        self.duration = -1

        # gravity
        self.gravity.x = -200.0
        self.gravity.y = 200.0

        # angle
        self.angle = 90.0
        self.angle_var = 360.0

        # speed of particles
        self.speed = 15.0
        self.speed_var = 5.0

        # radial
        self.radial_accel = 0
        self.radial_accel_var = 0

        # tangential
        self.tangential_accel = 0.0
        self.tangential_accel_var = 0.0


        # emitter position
        self.x = 320.0
        self.y = 240.0
        self.pos_var.x = 0
        self.pos_var.y = 0

        # life of particles
        self.life = 2.0
        self.life_var = 1.0

        # size, in pixels
        self.size = 60.0
        self.size_var = 10.0

        # emits per frame
        self.emission_rate = self.total_particles / self.life

        # color of particles
        self.start_color.r = 0.2
        self.start_color.g = 0.7
        self.start_color.b = 0.7
        self.start_color.a = 1.0
        self.start_color_var.r = 0.0
        self.start_color_var.g = 0.0
        self.start_color_var.b = 0.0
        self.start_color_var.a = 0.2
        self.end_color.r = 0.0
        self.end_color.g = 0.0
        self.end_color.b = 0.0
        self.end_color.a = 1.0
        self.end_color_var.r = 0.0
        self.end_color_var.g = 0.0
        self.end_color_var.b = 0.0
        self.end_color_var.a = 0.0


class Galaxy( ParticleSystem ):

    def __init__( self ):
        super( Galaxy, self).__init__(200)

        # duration
        self.duration = -1

        # gravity
        self.gravity.x = 0.0
        self.gravity.y = 0.0

        # angle
        self.angle = 90.0
        self.angle_var = 360.0

        # speed of particles
        self.speed = 60.0
        self.speed_var = 10.0

        # radial
        self.radial_accel = -80.0
        self.radial_accel_var = 0

        # tangential
        self.tangential_accel = 80.0
        self.tangential_accel_var = 0.0


        # emitter position
        self.x = 320.0
        self.y = 240.0
        self.pos_var.x = 0
        self.pos_var.y = 0

        # life of particles
        self.life = 4.0
        self.life_var = 1.0

        # size, in pixels
        self.size = 37.0
        self.size_var = 10.0

        # emits per frame
        self.emission_rate = self.total_particles / self.life

        # color of particles
        self.start_color.r = 0.12
        self.start_color.g = 0.25
        self.start_color.b = 0.76
        self.start_color.a = 1.0
        self.start_color_var.r = 0.0
        self.start_color_var.g = 0.0
        self.start_color_var.b = 0.0
        self.start_color_var.a = 0.0
        self.end_color.r = 0.0
        self.end_color.g = 0.0
        self.end_color.b = 0.0
        self.end_color.a = 1.0
        self.end_color_var.r = 0.0
        self.end_color_var.g = 0.0
        self.end_color_var.b = 0.0
        self.end_color_var.a = 0.0
