#!/usr/bin/env python

#############################################################################
##
## file :    SmaractMCSCtrl.py
##
## developers : ctbeamlines@cells.es
##
## copyleft :    Cells / Alba Synchrotron
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Sardana.
##
## This is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This software is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################

import PyTango
from sardana import State
from sardana.pool.controller import MotorController

MAX_VEL = 1e5
MAX_ACC = 1e-5
STEP_RES = 1


class SmaractMCSController(MotorController):
    """This class is the Tango Sardana motor controller for the Smaract MCS
    motor controller device. It is designed to work linked to the TangoDS
    PySmaract."""

    MaxDevice = 16

    class_prop = {'SmaractMCSDevName':
                      {'Type': 'PyTango.DevString',
                       'Description' : 'Device name of the Smaract MCS DS'}}

    attributeNames = ["motorstate"]

    motor_extra_attributes = {"MotorState":
                                  {'Type': 'PyTango.DevBoolean',
                                   'R/W Type': 'PyTango.READ'},}

    cs_extra_attributes = {}

    ctrl_extra_attributes = {}
    ctrl_extra_attributes.update(motor_extra_attributes)
    ctrl_extra_attributes.update(cs_extra_attributes)

    def __init__(self, inst, props, *args, **kwargs):
        MotorController.__init__(self, inst, props,  *args, **kwargs)
        self.smaractMCS = PyTango.DeviceProxy(self.SmaractMCSDevName)
        self.axesList = []
        self.startMultiple = {}
        self.positionMultiple = {}
        self.attributes = {}

    def AddDevice(self, axis):
        self._log.error("AddDevice entering...")
        self.axesList.append(axis)
        self.attributes[axis] = {"step_per_unit" : 1.0, "base_rate" : float(MAX_VEL)}
        self._log.error("AddDevice leaving...")

    def DeleteDevice(self, axis):
        self.axesList.remove(axis)
        self.attributes[axis] = None

    # def PreStateAll(self):
    #     for axis in self.axesList:
    #         self.attributes[axis] = {}

    def StateAll(self):
        """ Get State of all axes with just one command to the Smaract MCS
        Controller. """
        for axis in self.axesList:
            self.attributes[axis]["motorstate"] = \
                self.smaractMCS.command_inout("GetState", axis)

    def StateOne(self, axis):
        sm_state = self.smaractMCS.command_inout("GetState", axis)
        # state = self.attributes[axis]['motorstate']
        sm_status = self.smaractMCS.command_inout("GetStatus", axis)

#       STOPPED:
        if sm_state == 0:
            state = State.On
#       TARGETTING:
        elif sm_state == 4:
            state = State.Moving
        else:
            state = State.Init
        status = sm_status

        return state, status

    # def PreReadAll(self):
    #     self.positionMultiple = {}

    def ReadAll(self):
        for axis in self.axesList:
            self.positionMultiple[axis] = self.smaractMCS.command_inout("GetPosition", axis)/self.attributes[axis]["step_per_unit"]

    def ReadOne(self, axis):
        return self.positionMultiple[axis]
        #return self.smaractMCS.command_inout("GetPosition", axis-1)

    # def PreStartAll(self):
    #     self.startMultiple = {}

    # def PreStartOne(self, axis, position):
    #     self.startMultiple[axis] = position
    #     return True

    def StartOne(self, axis, position):
        position = position * self.attributes[axis]["step_per_unit"]
        self.smaractMCS.command_inout("MoveAbsolute",
                                      [int(axis), int(position)])

    def StartAll(self):
        for axis, position in self.startMultiple.items():
            self.StartOne(axis, position)

    def SetPar(self, axis, name, value):
        """ Set the standard pool motor parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        if name.lower() == "velocity":
            velocity = (value * self.attributes[axis]["step_per_unit"]
                        * STEP_RES)
            self.smaractMCS.command_inout("SetClosedLoopVelocity",
                                          [int(axis), int(velocity)])

        elif name.lower() == "acceleration":
            acceleration = (value * self.attributes[axis]["step_per_unit"]
                            * STEP_RES)
            self.smaractMCS.command_inout("SetClosedLoopAcceleration",
                                          [int(axis), int(acceleration)])

        elif name.lower() == "deceleration":
            self._log.debug('No deceleration set')

        elif name.lower() == "step_per_unit":
            self.attributes[axis]["step_per_unit"] = float(value)

        elif name.lower() == "base_rate":
            self._log.debug('No baserate set')

    def GetPar(self, axis, name):
        """ Get the standard pool motor parameters.
        @param axis to get the parameter
        @param name of the parameter to get the value
        @return the value of the parameter
        """
        if name.lower() == "max_velocity":
            return MAX_VEL

        elif name.lower() == "velocity":
            cl_velocity = self.smaractMCS.command_inout(
                "GetClosedLoopVelocity", int(axis))
            return float(cl_velocity
                         / self.attributes[axis]["step_per_unit"]
                         / STEP_RES)

        elif name.lower() == "acceleration":
            cl_acceleration = self.smaractMCS.command_inout(
                "GetClosedLoopAcceleration", int(axis))
            return float(cl_acceleration
                         / self.attributes[axis]["step_per_unit"]
                         / STEP_RES)

        elif name.lower() == "max_acceleration":
            return MAX_ACC

        elif name.lower() == "step_per_unit":
            return self.attributes[axis]["step_per_unit"]

        elif name.lower() == "base_rate":
            return self.attributes[axis]["base_rate"]
        else:
            return None

    def AbortOne(self, axis):
        self.smaractMCS.command_inout("Stop", axis)

    def DefinePosition(self, axis, value):
        pass

    def GetExtraAttributePar(self, axis, name):
        """ Get Pmac axis particular parameters.
        @param axis to get the parameter
        @param name of the parameter to retrive
        @return the value of the parameter
        """
        return self.attributes[axis][name]

    def SetExtraAttributePar(self, axis, name, value):
        """ Set Pmac axis particular parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        pass

    def SendToCtrl(self,cmd):
        """ Send custom native commands.
        @param string representing the command
        @return the result received
        """
        pass

