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
'''Pre-defined Particle Systems'''


from particle import ParticleSystem
from euclid import Point2

class Fireworks( ParticleSystem ):
    def __init__( self ):
        super( Fireworks, self).__init__(3000)

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
        self.size = 40.0
        self.size_var = 00.0


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
