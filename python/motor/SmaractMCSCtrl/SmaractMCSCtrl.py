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
from smaract import SmaractMCSController, CommType, Status, Direction
from sardana.pool.controller import MotorController, Type, Description, \
    Access, DataAccess, Memorize, Memorized

from sardana import State


HOMING = 'homing'
CALIBRATION = 'calibration'


class SmaractMCSCtrl(MotorController):
    """This class is the Tango Sardana motor controller for the Smaract MCS
    motor controller device. It only exposes the API for the positioners
    channel type.

    Controller units for the angular positioner:

        position: micro-degrees / step_per_unit
        velocity: (micro-degree / step_per_unit) / s
        time: s
        acceleration (time): s

    """

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
        'Safe_Direction': {Type: str,
                           Description: 'Configure the safe direction: '
                                        'forward(0) or backward(1)',
                           Access: DataAccess.ReadWrite,
                           Memorized: Memorize},
        'Sensor_Type': {Type: str,
                        Description: 'Type of the sensor configured',
                        Access: DataAccess.ReadWrite,
                        Memorized: Memorized},
        'Channel_Type': {Type: str,
                         Description: 'Channel type positioner(0), '
                                      'endeffector(1)',
                         Access: DataAccess.ReadOnly,
                         Memorized: Memorized},
        #
        # TODO: These are only valid for end effector channel type
        #
        # 'Force': {Type: float,
        #           Description: 'Force measured by the sensor value in 1/10 uN',
        #           Access: DataAccess.ReadOnly},
        # 'Gripper_Opening': {Type: float,
        #                     Description: 'Current voltage applied to the '
        #                                  'gripper. Value in 1/100 Vols',
        #                    Access: DataAccess.ReadOnly},
        #
        'Voltage_Level': {Type: float,
                          Description: 'Voltage applied to a positioner',
                          Access: DataAccess.ReadOnly},
        'Serial_Number': {Type: str,
                          Description: 'Serial number',
                          Access: DataAccess.ReadOnly},
        'Firmware_Version': {Type: str,
                             Description: 'Firmware version',
                             Access: DataAccess.ReadOnly},
        'Emergency_Stop': {Type: str,
                           Description: 'Emergency stop behaviour',
                           Access: DataAccess.ReadWrite,
                           Memorized: Memorize},
        'Broadcast_Stop': {Type: bool,
                           Description: 'Broadcast stop enabled',
                           Access: DataAccess.ReadWrite,
                           Memorized: Memorize},
        'Physical_Position_Known': {Type: bool,
                                    Description: 'Physical position is known',
                                    Access: DataAccess.ReadOnly},
        'Scale_Inverted': {Type: bool,
                           Description: 'Scale inverted enabled',
                           Access: DataAccess.ReadWrite,
                           Memorize: Memorized},
        'Scale_Offset': {Type: long,
                         Description: 'Scale offset in steps',
                         Access: DataAccess.ReadWrite,
                         Memorize: Memorized},
        'Positioner_Limits': {Type: [float],
                         Description: 'Scale limits.',
                         Access: DataAccess.ReadWrite,
                         Memorize: Memorized},
        'Hold_Time': {Type: float,
                      Description: 'Hold time after end movement',
                      Access: DataAccess.ReadWrite,
                      Memorized: Memorize},
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
        try:
            self._mcs = SmaractMCSController(comm_type, *args)
        except Exception as e:
            self._log.error(e)
        self._axes = {}
        # TODO: Review when MaxDevice bug is fixed
        # SmaractMCSCtrl.MaxDevice = self._mcs.nchannels
        self.MaxDevice = self._mcs.nchannels

    def AddDevice(self, axis):
        # TODO: The raise exception is ignored.
        # Issue 637 reported to sardana
        if axis <= 0:
            msg = "Axis MUST be greater than 0."
            raise ValueError(msg)
        self._axes[axis] = {}
        self._axes[axis]['step_per_unit'] = 1.0
        self._axes[axis]['motor'] = self._mcs[axis-1]
        self._axes[axis]['hold_time'] = 0.

    def DeleteDevice(self, axis):
        self._axes.pop(axis)

    def StateOne(self, axis):
        state_code, _, status = self._axes[axis]['motor'].status

        if state_code in [Status.STOPPED, Status.HOLDING, Status.WAITING]:
            state = State.On
        elif state_code in [Status.STEPPING, Status.SCANNING, Status.TARGETING,
                            Status.CALIBRATING, Status.HOMING]:
            state = State.Moving
        elif state_code in [Status.LOCKED]:
            state = State.Disable
        else:
            state = State.Fault

        return state, status

    def ReadOne(self, axis):
        position = self._axes[axis]['motor'].position
        step_per_unit = self._axes[axis]['step_per_unit']
        return position/step_per_unit

    def StartOne(self, axis, position):
        position = position * self._axes[axis]["step_per_unit"]
        hold_time = self._axes[axis]["hold_time"]
        self._log.debug('velocity %s' % self._axes[axis]['motor'].closed_loop_vel)
        self._log.debug("position %s" % position)
        self._log.debug("hold_time %s" % hold_time)
        self._axes[axis]['motor'].move(position, hold_time)

    def SetPar(self, axis, name, value):
        """ Set the standard pool motor parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        name = name.lower()
        step_per_unit = self._axes[axis]["step_per_unit"]

        if name == 'velocity':
            value = value * step_per_unit
            self._axes[axis]['motor'].closed_loop_vel = value
        elif name in ['acceleration', 'deceleration']:
            vel = self._axes[axis]['motor'].closed_loop_vel / step_per_unit
            value = vel / (value * 1e3)
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
        step_per_unit = self._axes[axis]["step_per_unit"]
        if name == 'velocity':
            result = self._axes[axis]['motor'].closed_loop_vel / step_per_unit
        elif name in ['acceleration', 'deceleration']:
            acc = self._axes[axis]['motor'].closed_loop_acc / step_per_unit
            value = self._axes[axis]['motor'].closed_loop_vel / (acc*1e3)
            result = value / step_per_unit
        elif name == 'step_per_unit':
            result = step_per_unit
        elif name == 'base_rate':
            result = 0
        else:
            result = None
        return result

    def AbortOne(self, axis):
        self._axes[axis]['motor'].stop()

    def GetAxisExtraPar(self, axis, name):
        """ Get Smaract axis particular parameters.
        @param axis to get the parameter
        @param name of the parameter to retrive
        @return the value of the parameter
        """
        name = name.lower()
        step_per_unit = self._axes[axis]["step_per_unit"]
        if name == 'safe_direction':
            result = self._axes[axis]['motor'].safe_direction
        elif name == 'sensor_type':
            result = self._axes[axis]['motor'].sensor_type
        elif name == 'channel_type':
            result = self._axes[axis]['motor'].channel_type
        elif name == 'force':
            result = self._axes[axis]['motor'].force
        elif name == 'gripper_opening':
            result = self._axes[axis]['motor'].gripper_opening
        elif name == 'voltage_level':
            result = self._axes[axis]['motor'].voltage_level
        elif name == 'serial_number':
            result = self._axes[axis]['motor'].serial_number
        elif name == 'firmware_version':
            result = self._axes[axis]['motor'].firmware_version
        elif name == 'emergency_stop':
            result = self._axes[axis]['motor'].emergency_stop
        elif name == 'broadcast_stop':
            result = self._axes[axis]['motor'].broadcast_stop
        elif name == 'physical_position_known':
            result = self._axes[axis]['motor'].physical_position_known
        elif name == 'scale_inverted':
            result = self._axes[axis]['motor'].scale_inverted / step_per_unit
        elif name == 'scale_offset':
            result = self._axes[axis]['motor'].scale_offset
        elif name == 'positioner_limits':
            values = self._axes[axis]['motor'].position_limits
            result = [x/step_per_unit for x in values]
        elif name == 'hold_time':
            result = self._axes[axis]['hold_time'] / 1e3
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
        step_per_unit = self._axes[axis]["step_per_unit"]
        if name == 'safe_direction':
            self._axes[axis]['motor'].safe_direction = value
        elif name == 'sensor_type':
            self._axes[axis]['motor'].sensor_type = value
        elif name == 'channel_type':
            self._axes[axis]['motor'].channel_type = value
        elif name == 'emergency_stop':
            self._axes[axis]['motor'].emergency_stop = value
        elif name == 'broadcast_stop':
            self._axes[axis]['motor'].broadcast_stop = value
        elif name == 'scale_inverted':
            self._axes[axis]['motor'].scale_inverted = value * step_per_unit
        elif name == 'scale_offset':
            self._axes[axis]['motor'].scale_offset = value
        elif name == 'positioner_limits':
            values = [x * step_per_unit for x in value]
            # Convert from nparray to list
            self._axes[axis]['motor'].position_limits = values
        elif name == 'hold_time':
            self._axes[axis]['hold_time'] = value * 1e3
        else:
            raise ValueError('There is not %s attribute' % name)

    def SendToCtrl(self, cmd):
        """
        Send custom native commands. The cmd is a space separated string
        containing the command information. Parsing this string one gets
        the command name and the following are the arguments for the given
        command i.e.command_name, [arg1, arg2...]

        When these methods are invoqued
        :param cmd: string
        :return: string (MANDATORY to avoid OMNI ORB exception)
        """
        # Get the process to send
        mode = cmd.split(' ')[0].lower()
        args = cmd.strip().split(' ')[1:]

        if mode == HOMING:
            try:
                if len(args) == 2:
                    axis, direction = args
                    axis = int(axis)
                    direction = int(direction)
                else:
                    raise ValueError('Invalid number of arguments')
            except Exception as e:
                self._log.error(e)

            self._log.info('Starting homing for axis %s in direction id %s' %
                           (axis, direction))
            try:
                self._axes[axis]['motor'].find_reference_mark(direction, 0, 1)
            except Exception as e:
                self._log.error(e)

            # Mandatory to let the system to update internals
            time.sleep(0.3)
            success = self._axes[axis]['motor'].physical_position_known

            if success:
                msg = 'Homing axis %s has finished. ' % axis
                msg += 'Proceed to setup the Smaract limits (if necessary)'
                self._log.info(msg)
                return msg
            else:
                return 'ERROR: No physical position known.'
        elif mode == CALIBRATION:
            try:
                if len(args) == 1:
                    axis = args[0]
                    axis = int(axis)
                else:
                    raise ValueError('Invalid number of arguments')
            except Exception as e:
                self._log.error(e)

            self._log.info('Calibrating sensor/axis %s' % axis)
            try:
                self._axes[axis]['motor'].calibrate_sensor
            except Exception as e:
                self._log.error(e)
            return 'Calibration finished.'
        else:
            self._log.warning('Invalid command')
            return 'ERROR: Invalid command requested.'
