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
import time
from sardana.pool.controller import MotorController

from sardana import State

MAX_VEL = 1e5
MAX_ACC = 1e-5
STEP_RES = 1

HOME_LIN_SINGLE = 'home_linial_single'


class SmaractMCSController(MotorController):
    """This class is the Tango Sardana motor controller for the Smaract MCS
    motor controller device. It is designed to work linked to the TangoDS
    PySmaract."""

    MaxDevice = 16

    class_prop = {'SmaractMCSDevName':
                      {'Type': 'PyTango.DevString',
                       'Description': 'Device name of the Smaract MCS DS'}}

    ctrl_extra_attributes = {}

    def __init__(self, inst, props, *args, **kwargs):

        try:
            MotorController.__init__(self, inst, props, *args, **kwargs)
            self.smaractMCS = PyTango.DeviceProxy(self.SmaractMCSDevName)
            self.axesList = []
            self.startMultiple = {}
            self.positionMultiple = {}
            self.attributes = {}

        except:
            self._log.error('Error when init')
            raise

    def AddDevice(self, axis):
        self._log.error("AddDevice entering...")
        self.axesList.append(axis)
        self.attributes[axis] = {"step_per_unit": 1.0,
                                 "base_rate": float(MAX_VEL)}

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
        known = self.smaractMCS.command_inout("GetPhysicalPositionKnown", axis)

        #       STOPPED:
        if sm_state == 0:
            state = State.On
        # TARGETTING:
        elif sm_state == 4:
            state = State.Moving
        else:
            state = State.Init
        status = sm_status

        if not known:
            state = State.Fault
            status = 'You MUST homing the detector first (smaract_mcs_homing).'

        return state, status

    # def PreReadAll(self):
    #     self.positionMultiple = {}

    def ReadAll(self):
        for axis in self.axesList:
            self.positionMultiple[axis] = (
                self.smaractMCS.command_inout("GetPosition", axis)
                / self.attributes[axis]["step_per_unit"])

    def ReadOne(self, axis):
        return self.positionMultiple[axis]

    # def PreStartAll(self):
    #     self.startMultiple = {}

    # def PreStartOne(self, axis, position):
    #     self.startMultiple[axis] = position
    #     return True

    def StartOne(self, axis, position):
        position = position * self.attributes[axis]["step_per_unit"]

        try:
            self.smaractMCS.command_inout("MoveAbsolute",
                                          [int(axis), int(position)])
        except Exception, e:
            self._log.error('Axis cannot be moved, %s' % str(e))
            raise

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
            velocity = float(value * self.attributes[axis]["step_per_unit"]
                             * STEP_RES)
            self.smaractMCS.command_inout("SetClosedLoopVelocity",
                                          [int(axis), int(velocity)])

        elif name.lower() == "acceleration":
            acceleration = float(value * self.attributes[axis]["step_per_unit"]
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

    def GetAxisExtraPar(self, axis, name):
        """ Get Smaract axis particular parameters.
        @param axis to get the parameter
        @param name of the parameter to retrive
        @return the value of the parameter
        """
        if name.lower() == "lowerlimit":
            lowerlimit, upperlimit = self.smaractMCS.command_inout(
                "GetPositionLimits", int(axis))
            self._log.debug('(*)lowerlimit=%s, upperlimit=%s' % (lowerlimit,
                                                                 upperlimit))
            return lowerlimit / self.attributes[axis]["step_per_unit"]

        elif name.lower() == "upperlimit":
            lowerlimit, upperlimit = self.smaractMCS.command_inout(
                "GetPositionLimits", int(axis))
            self._log.debug('lowerlimit=%s, (*)upperlimit=%s' % (lowerlimit,
                                                                 upperlimit))
            return upperlimit / self.attributes[axis]["step_per_unit"]
        else:
            return None

    def SetAxisExtraPar(self, axis, name, value):
        """ Set Smaract axis particular parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        if name.lower() == "lowerlimit":
            upperlimit = self.GetAxisExtraPar(axis, "upperlimit")
            upperlimit = upperlimit * self.attributes[axis]["step_per_unit"]
            value = value * self.attributes[axis]["step_per_unit"]
            self._log.debug('new lowerlimit=%s' % value)
            self.smaractMCS.command_inout("SetPositionLimits",
                                          [int(axis), int(value),
                                           int(upperlimit)])

        elif name.lower() == "upperlimit":
            lowerlimit = self.GetAxisExtraPar(axis, "lowerlimit")
            lowerlimit = lowerlimit * self.attributes[axis]["step_per_unit"]
            value = value * self.attributes[axis]["step_per_unit"]
            self._log.debug('new upperlimit=%s' % value)
            self.smaractMCS.command_inout("SetPositionLimits",
                                          [int(axis), int(lowerlimit),
                                           int(value)])

    def SendToCtrl(self, cmd):
        """ Send custom native commands.
        @param string representing the command
        @return the result received
        """
        mode = cmd.split(':')[0]

        # Prepare axis for homing single position mark mode
        if mode == HOME_LIN_SINGLE:

            axis, direction = cmd.split(':')[1].strip().split(' ')
            axis = int(axis)
            direction = int(direction)

            self._log.info('Starting %s for axis %s in direction %s' % (
            HOME_LIN_SINGLE, axis, direction))

            self.smaractMCS.command_inout("SetSafeDirection", [axis, direction])
            # TANGO8 version can wait for the command to finish
            # self.smaractMCS.command_inout("FindReferenceMark", axis, wait=True)
            # TANGO7 version needs a timesleep to let the command finish
            self.smaractMCS.command_inout("FindReferenceMark", axis)
            time.sleep(5)
            success = self.smaractMCS.command_inout("GetPhysicalPositionKnown",
                                                    axis)

            if success:
                self._log.info(
                    '%s has finished successfully.' % HOME_LIN_SINGLE)
                self._log.info('Configuring Smaract limits')
                # lower, upper = self.smaractMCS.get_property('limits')['lim_0'][0].split(',')
                limits_list = self.smaractMCS.get_property('limits')['limits'][
                    0].split(';')
                lower = limits_list[axis].split(",")[1]
                upper = limits_list[axis].split(",")[2]
                lower = long(lower)
                upper = long(upper)
                self.smaractMCS.command_inout("SetPositionLimits",
                                              [axis, lower, upper])
                limits = self.smaractMCS.command_inout("GetPositionLimits",
                                                       axis)
                self._log.info('Current limits: %s' % repr(limits))
                return 'READY'
            else:
                self._log.warning(
                    '%s failed:  no physical position known!' % HOME_LIN_SINGLE)
                return 'ERROR: No physical position known.'
        else:
            self._log.warning('Invalid homing mode requested.')
            return 'ERROR: Invalid homing mode requested.'

