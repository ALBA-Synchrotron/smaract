#!/usr/bin/env python

################################################################################
#
# file :    SmaractMCSCtrl.py
#
# developers : ctbeamlines@cells.es
#
# copyleft :    Cells / Alba Synchrotron
#               Bellaterra
#               Spain
#
################################################################################
#
# This file is part of Sardana.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
################################################################################

import time
from smaract import SmaractMCSController, CommType
from sardana.pool.controller import MotorController, Type, Description, \
    Access, DataAccess, Memorize, Memorized

from sardana import State


HOME_LIN_SINGLE = 'home_linial_single'


class SmaractMCSController(MotorController):
    """This class is the Tango Sardana motor controller for the Smaract MCS
    motor controller device. It is designed to work linked to the TangoDS
    PySmaract."""

    MaxDevice = 16

    class_prop = {
        'CommType': {Type: str,
                     Description: 'Communication type: Serial, Tango, Socket'},

        # TODO: Analyze if there is another way to introduce the configuration
        'CommArgs': {Type: str,
                     Description: 'Communication arguments initialization '
                                  'separated by semicolons'},

    }

    ctrl_extra_attributes = {}

    axis_attributes = {
        'SafeDirection': {Type: str,
                          Description: 'Configure the safe direction: '
                                       'forward(0) or backward(1)',
                          Access: DataAccess.ReadWrite,
                          Memorized: Memorize,},
        'SensorType': {Type: str,
                       Description: 'Type of the sensor configured',
                       Access: DataAccess.ReadWrite,
                       Memorized: Memorized},
        'ChannelType': {Type: str,
                        Description: 'Channel type positioner(0), '
                                     'endeffector(1)',
                        Access: DataAccess.ReadWrite,
                        Memorized: Memorized},
        'Force': {Type: float,
                  Description: 'Force measured by the sensor value in 1/10 uN',
                  Access: DataAccess.ReadOnly},
        'GripperOpening': {Type: float,
                           Description: 'Current voltage applied to the '
                                        'gripper. Value in 1/100 Vols',
                           Access: DataAccess.ReadOnly},
        'VoltageLevel': {Type: float,
                         Description: 'Voltage applied to a positioner',
                         Access: DataAccess.ReadOnly},
        'SerialNumber': {Type: str,
                         Description: 'Serial number',
                         Access: DataAccess.ReadOnly},
        'FirmwareVersion': {Type: str,
                            Description: 'Firmware version',
                            Access: DataAccess.ReadOnly},
        'EmergencyStop': {Type: str,
                          Description: 'Emergency stop behaviour',
                          Access: DataAccess.ReadWrite,
                          Memorized: Memorize},
        'BroadcastStop': {Type: bool,
                          Description: 'Broadcast stop enabled',
                          Access: DataAccess.ReadWrite,
                          Memorized: Memorize},
        'ScaleInverted': {Type: bool,
                          Description: 'Scale inverted enabled',
                          Access: DataAccess.ReadWrite,
                          Memorize: Memorized},
        'ScaleOffset': {Type: long,
                        Description: 'Scale offset in steps',
                        Access: DataAccess.ReadWrite,
                        Memorize: Memorized},
        'ScaleLimits': {Type: [float],
                        Description: 'Scale limits.',
                        Access: DataAccess.ReadWrite,
                        Memorize: Memorized},

    }

    def __init__(self, inst, props, *args, **kwargs):
        MotorController.__init__(self, inst, props, *args, **kwargs)
        self.CommType = self.CommType.lower()
        if self.CommType == 'serial':
            comm_type = CommType.Serial
        elif self.CommType == 'tango':
            comm_type = CommType.SerialTango
        elif self.CommType == 'socket':
            comm_type = CommType.Socket
        else:
            raise ValueError('Communication type is not valid')
        args = self.CommArgs.split(';')
        self._mcs = SmaractMCSController(comm_type, *args)
        self._axes = {}
        self.MaxDevice = self._mcs.nchannels

    def AddDevice(self, axis):
        self._axes[axis] = {}
        self._axes[axis]['step_per_unit'] = 1.0
        self._axes[axis]['motor'] = self._mcs[axis-1]

    def DeleteDevice(self, axis):
        self._axes.pop(axis)

    def StateOne(self, axis):
        state_code, _, status = self._axes[axis]['motor'].status
        # TODO: use the Status class
        if state_code == 0:
            state = State.On
        elif state_code == 4:
            state = State.Moving
        else:
            state = State.Fault

        return state, status

    def ReadOne(self, axis):
        position = self._axes[axis]['motor'].position
        step_per_unit = self._axes[axis]['step_per_unit']
        return position/step_per_unit

    def StartOne(self, axis, position):
        position = position * self.attributes[axis]["step_per_unit"]
        self._axes[axis]['motor'].move(position)

    def SetPar(self, axis, name, value):
        """ Set the standard pool motor parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        name = name.lower()
        step_per_unit = self.attributes[axis]["step_per_unit"]

        if name == 'velocity':
            value = value * step_per_unit
            self._axes[axis]['motor'].closed_loop_vel = value
        elif name == 'acceleration':
            value = value * step_per_unit
            self._axes[axis]['motor'].closed_loop_acc = value
        elif name == 'step_per_unit':
            self._axes[axis]['step_per_unit'] = value
        else:
            self._log.debug('Parameter %s is not set' % name)

    def GetPar(self, axis, name):
        """ Get the standard pool motor parameters.
        @param axis to get the parameter
        @param name of the parameter to get the value
        @return the value of the parameter
        """
        name = name.lower()
        step_per_unit = self.attributes[axis]["step_per_unit"]
        if name == 'velocity':
            result = self._axes[axis]['motor'].close_loop_vel * step_per_unit
        elif name in ['acceleration', 'deceleration']:
            result = self._axes[axis]['motor'].close_loop_acc * step_per_unit
        elif name == 'step_per_unit':
            result = step_per_unit
        elif name == 'base_rate':
            result = 0
        else:
            result = None
        return result

    def AbortOne(self, axis):
        self._axes['motor'].stop()

    def GetAxisExtraPar(self, axis, name):
        """ Get Smaract axis particular parameters.
        @param axis to get the parameter
        @param name of the parameter to retrive
        @return the value of the parameter
        """
        name = name.lower()
        if name == 'safedirection':
            result = self._axes[axis]['motor'].safe_direction
        elif name == 'sensortype':
            result = self._axes[axis]['motor'].sensor_type
        elif name == 'channeltype':
            result = self._axes[axis]['motor'].channel_type
        elif name == 'force':
            result = self._axes[axis]['motor'].force
        elif name == 'gripperopening':
            result = self._axes[axis]['motor'].gripper_opening
        elif name == 'voltagelevel':
            result = self._axes[axis]['motor'].voltage_level
        elif name == 'serialnumber':
            result = self._axes[axis]['motor'].serial_number
        elif name == 'firmwareversion':
            result = self._axes[axis]['motor'].firmware_version
        elif name == 'emergencystop':
            result = self._axes[axis]['motor'].emergency_stop
        elif name == 'broadcaststop':
            result = self._axes[axis]['motor'].broadcast_stop
        elif name == 'scaleinverted':
            result = self._axes[axis]['motor'].scale_inverted
        elif name == 'scaleoffset':
            result = self._axes[axis]['motor'].scale_offset
        elif name == 'scalelimits':
            result = self._axes[axis]['motor'].position_limits
        else:
            raise ValueError('There is not %s attribute' % name)
        return result

    def SetAxisExtraPar(self, axis, name, value):
        """ Set Smaract axis particular parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        name = name.lower()
        if name == 'safedirection':
            self._axes[axis]['motor'].safe_direction = value
        elif name == 'sensortype':
            self._axes[axis]['motor'].sensor_type = value
        elif name == 'channeltype':
            self._axes[axis]['motor'].channel_type = value
        elif name == 'emergencystop':
            self._axes[axis]['motor'].emergency_stop = value
        elif name == 'broadcaststop':
            self._axes[axis]['motor'].broadcast_stop = value
        elif name == 'scaleinverted':
            self._axes[axis]['motor'].scale_inverted = value
        elif name == 'scaleoffset':
            self._axes[axis]['motor'].scale_offset = value
        elif name == 'scalelimits':
            self._axes[axis]['motor'].position_limits = value
        else:
            raise ValueError('There is not %s attribute' % name)

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

