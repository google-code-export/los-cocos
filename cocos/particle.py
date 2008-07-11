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

from cocosnode import CocosNode
from euclid import Point2

rand = lambda: random.random() * 2 - 1

ALIVE = (1 << 0 )

class Color( object ):
    def __init__( self, r,g,b,a ):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_array(self):
        return self.r, self.g, self.b, self.a

class PointSpriteGroup( pyglet.sprite.SpriteGroup ):
    def set_state(self):
        super(PointSpriteGroup,self).set_state()
        glEnable( GL_POINT_SPRITE )
        glTexEnvi( GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE )

    def unset_state(self):
        glDisable( GL_POINT_SPRITE )
        super(PointSpriteGroup,self).unset_state()

class Particle( object ):
    def __init__(self):
        #: position of the particle, relative to the center of the system
        self.pos = Point2(0,0)
        #: direction of the particle
        self.dir = Point2(0,0)
        #: radial acceleration of the particle
        self.radial_accel = 0.0
        #: tangential acceleration of the particle
        self.tangential_accel = 0.0
        #: color of the particle
        self.color = Color(255,255,255,255)
        #: delta color of the particle
        self.delta_color = Color(0,0,0,0)
        #: size of the particle
        self.size = 1
        #: life of the particle
        self.life = 0
        #: flags of the particle (ALIVE, etc...)
        self.flags = 0

    def __str__(self):
        s ='pos:%s, dir:%s, life:%s, r:%s, t:%s, f:%s' % (self.pos, self.dir, self.life, self.radial_accel, self.tangential_accel, self.flags)
        return s

class ParticleSystem( CocosNode ):
    def __init__(self, total_particles, texture=None):
        super(ParticleSystem,self).__init__()

        self.id = 0
        self.flags = 0

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
        self.start_color = Color(255,255,255,255)
        #: Start color variance
        self.start_color_var = Color(255,255,255,255)
        #: End color of the particles
        self.end_color = Color(255,255,255,255)
        #: End color variance
        self.end_color_var = Color(255,255,255,255)

        #: array of particles
        self.particles = []
        for i in xrange( total_particles ):
            self.particles.append( Particle() )

        #: Maximum particles
        self.total_particles = total_particles
        #: Count of particles
        self.particle_count = 0

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

        self.batch = pyglet.graphics.Batch()
        self.group = PointSpriteGroup(self.texture, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE)
        self.vertex_list = self.batch.add( self.total_particles, GL_POINTS, self.group, "v2f/stream","c4f")

        ver = []
        for i in xrange(self.total_particles):
            ver.append(0)
            ver.append(0)

        self.vertex_list.vertices = ver
        self.vertex_list.colors = [255,255,255,255] * self.total_particles

        self.schedule( self.step )

    def on_enter( self ):
        super( ParticleSystem, self).on_enter()
        self.add_particle()

    def draw( self ):
        glPushMatrix()
        self.transform()

        glPointSize( self.size )
        self.batch.draw()

        glPopMatrix()


    def step( self, delta ):
        if self.active:
            rate = 1.0 / self.emission_rate
            self.emit_counter += delta

            while self.particle_count < self.total_particles and self.emit_counter > rate:
                self.add_particle()
                self.emit_counter -= rate

            self.elapsed += delta

            if self.duration != -1 and self.duration < self.elapsed:
                self.stop_system()

        self.update_particles( delta )

    def add_particle( self ):
        self.init_particle( self.particle_count )
        self.particle_count += 1

    def stop_system( self ):
        self.active = False
        self.elapsed= self.duration
        self.emit_counter = 0

    def reset_system( self ):
        self.elapsed= self.duration
        self.emit_counter = 0

    def update_particles( self, delta ):
        for idx in xrange(self.particle_count):
            p = self.particles[idx]
            if p.life > 0:

                # radial
                radial = Point2(0,0)
                if p.pos.x or p.pos.y:
                    radial = p.pos.normalized()
                tangential = radial.copy()
                radial *= p.radial_accel

                # tangential acceleration
                tangential = Point2( -tangential.y, tangential.x )
                tangential *= p.tangential_accel

                # (gravity + radial + tangential) * dt
                p.dir += ( radial + tangential + self.gravity ) * delta
                p.pos += (p.dir * delta)

                # color
                p.color.r += p.delta_color.r * delta
                p.color.g += p.delta_color.g * delta
                p.color.b += p.delta_color.b * delta
                p.color.a += p.delta_color.a * delta

                p.life -= delta

                # update vertex list
                self.vertex_list.vertices[ idx * 2 ] = p.pos.x
                self.vertex_list.vertices[ idx * 2 + 1 ] = p.pos.y
                self.vertex_list.colors[idx*4:idx*4+4] = p.color.to_array()

            # else
            elif p.flags == ALIVE:
                if idx != self.particle_count -1:
                    self.particles[ idx ] = copy.copy(self.particles[ self.particle_count -1 ])
                self.particles[ self.particle_count-1].flags = 0
                self.particle_count -= 1


    def init_particle( self, idx ):
        # position
#        p=self.particles[idx]
        p = Particle()

        p.pos.x = self.pos_var.x * rand()
        p.pos.y = self.pos_var.y * rand()

        # direction
        a = math.radians( self.angle + self.angle_var * rand() )
        v = Point2( math.cos( a ), math.sin( a ) )
        s = self.speed + self.speed_var * rand()
        p.dir = v * s

        # radial accel
        p.radial_accel = self.radial_accel + self.radial_accel_var * rand()

        # tangential accel
        p.tangential_accel = self.tangential_accel + self.tangential_accel_var * rand()
        
        # life
        p.life = self.life + self.life_var * rand()

        # Color
        # start
        sr = self.start_color.r + self.start_color_var.r * rand()
        sg = self.start_color.g + self.start_color_var.g * rand()
        sb = self.start_color.b + self.start_color_var.b * rand()
        sa = self.start_color.a + self.start_color_var.a * rand()

        p.color = Color(sr,sg,sb,sa)

        # end
        er = self.end_color.r + self.end_color_var.r * rand()
        eg = self.end_color.g + self.end_color_var.g * rand()
        eb = self.end_color.b + self.end_color_var.b * rand()
        ea = self.end_color.a + self.end_color_var.a * rand()

        p.delta_color.r = (er - sr) / p.life
        p.delta_color.g = (eg - sg) / p.life
        p.delta_color.b = (eb - sb) / p.life
        p.delta_color.a = (ea - sa) / p.life

        # size
        p.size = self.size + self.size_var * rand()

        # alive
        p.flags = ALIVE

        self.particles[ idx ] = p

class Fireworks( ParticleSystem ):
    def __init__( self ):
        super( Fireworks, self).__init__(500)

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

        self.texture = pyglet.resource.image("fire.png").get_texture()


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

        self.texture = pyglet.resource.image("fire.png").get_texture()

class Fire( ParticleSystem ):

    def __init__( self ):
        super( Fire, self).__init__(500)

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

        self.texture = pyglet.resource.image("fire.png").get_texture()

class Flower( ParticleSystem ):

    def __init__( self ):

        super( Flower, self).__init__(350)

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
        self.gravity.x = 0.
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

        self.texture = pyglet.resource.image("fire.png").get_texture()

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

        self.texture = pyglet.resource.image("fire.png").get_texture()

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

        self.texture = pyglet.resource.image("fire.png").get_texture()

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

        self.texture = pyglet.resource.image("fire.png").get_texture()
