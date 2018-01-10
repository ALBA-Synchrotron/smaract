# ------------------------------------------------------------------------------
# This file is part of smaract (https://github.com/ALBA-Synchrotron/smaract)
#
# Copyright 2008-2017 CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Distributed under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#
# You should have received a copy of the GNU General Public License
# along with smaract. If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------


import weakref
from constants import *


class SmaractBaseAxis(object):
    """
    Smaract Axis Base class. Contains the common Smaract ASCii API for any
    Smaract axis. The methods here implemented correspond to those
    at the axis level. The _send_cmd function wrappers the current controller
    _send_cmd method.
    """
    def __init__(self, ctrl, axis_nr=0):
        self._axis_nr = axis_nr
        ref = weakref.ref(ctrl)
        self._ctrl = ref()
        
    def _send_cmd(self, str_cmd, *pars):
        """
        Send command function used to retrieve controller information at the
        axis level.

        :param str_cmd: String command following the ASCii Smaract API.
        :param pars: optional parameters required by the command.
        :return: command answer.
        """
        str_cmd = "%s%d" % (str_cmd, self._axis_nr)
        cmd = "%s" % (str_cmd + "".join([",%d" % i for i in pars]))
        return self._ctrl.send_cmd(cmd)

    @property
    def safe_direction(self):
        """
        Gets the current configured safe direction.
        0: forward (FORWARD).
        1: backward (BACKWARD).
        Channel Type: Positioner.

        :return: either 0 or 1.

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GSD')
        direction = int(ans[-1])
        result = ['forward', 'backward'][direction]
        return result

    @safe_direction.setter
    def safe_direction(self, direction):
        """
        Sets the current configured safe direction.
        Channel Type: Positioner.

        :param direction: either forward(0) or backward(0).
        :return: None

        Documentation: MCS Manual section 3.2
        """
        direction = direction.lower()
        if direction == 'forward':
            value = 0
        elif direction == 'backward':
            value = 1
        else:
            raise ValueError('Read the help')
        self._send_cmd('SSD', value)

    @property
    def sensor_type(self):
        """
        Gets the type of sensor connected.
        Channel Type: Positioner.

        :return: Sensor code.

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GST')
        sensor_code = int(ans.rsplit(',', 1)[1])
        return self._ctrl.SENSOR_CODE[sensor_code]

    @property
    def position(self):
        """
        Gets the current position of a positioner.
        Channel Type: Positioner.

        :return: current positioner position.

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GP')
        return float(ans.split(',')[1])

    @property
    def state(self):
        """
        Get the current movement status of the positioner or end effector.
        Channel Type: Positioner, End Effector.

        :return: channel status code.

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GS')
        return int(ans.split(',')[1]) 

    @property
    def status(self):
        """
        Get the current state, state msg and status of the positioner

        :return: channel status code, state msg and status.

        Documentation: MCS Manual section 3.4
        """

        state_code = self.state 
        state_msg = Status.states_txt[state_code]
        status = Status.status_txt[state_code]
        return state_code, state_msg, status

    ############################################################################
    #                       Commands
    ############################################################################
    def move(self, position):
        """
        Abstract method
        :param position: absolute position
        :return:
        """
        raise NotImplemented('The method should be implement')

    def calibrate_sensor(self):
        """
        Increase the accuracy of the position calculation.
        Channel Type: Positioner.

        :return: None

        Documentation: MCS Manual section 3.3
        """
        self._send_cmd('CS')

    def find_reference_mark(self, direction, hold_time=0, auto_zero=0):
        """
        Move to a known physical position of the positioner. Many strategies can
        be applied by setting different direction values. The hold_time (ms)
        sets for how long the position is actively held. The auto_zero flag setz
        the position to zero after the mark is find.
        Channel Type: Positioner

        :param direction: any valid direction value.
        :param hold_time: held after find reference mark in ms.
        :param auto_zero: flag to reset the position to 0.
        :return: None

        Documentation: MCS Manual section 3.3
        """
        self._send_cmd('FRM', direction, hold_time, auto_zero)

    def move_step(self, steps, amplitude, frequency):
        """
        Open-loop command that performs a burst of steps.
        Channel Type: Positioner.

        :param steps: number and direction of steps.
        :param amplitude: steps amplitude (12-bit value, 0-100V).
        :param frequency: steps frequency.
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_steps_in_range(steps)
        is_amplitude_in_range(amplitude)
        is_frequency_in_range(frequency)
        self._send_cmd('MST', steps, amplitude, frequency)

    def stop(self):
        """
        Stops the ongoing motions of the positioner.
        Channel Type: Positioner.

        :return: None

        Documentation: MCS Manual section 3.3
        """
        self._send_cmd('S')


class SmaractSDCAxis(SmaractBaseAxis):
    """
    Specific class for SDC controllers.
    """
    @property
    def target_position(self):
        """
        Gets the current target position (working as slave).
        Channel Type: Positioner.

        :return: current target position.

        Documentation: SDC Manual section 3.4
        """
        ans = self._send_cmd('GTP')
        return float(ans.split(',')[1])

    @property
    def error_status(self):
        """
        Gets the latest error code.
        Channel Type: Positioner.

        :return: error code.

        Documentation: SDC Manual section 3.5
        """
        ans = self._send_cmd('GES')
        return int(ans.split(',')[1, 2])

    @property
    def error_queue(self):
        """
        Gets all error in queue.
        Channel Type: Positioner.

        :return: list with error list.

        Documentation: SDC Manual section 3.5
        """
        err_list = list()
        err, rem = self.error_status
        err_list.append(err)
        while rem != 0:
            err, rem = self.error_status
            err_list.append(err)
        return err_list

    @property
    def step_increment(self):
        """
        Get the eight step increments from the configuration table

        :return: [0..7] step increments

        Documentation: SDC Manual section 3.5
        """
        values = []
        for i in range(8):
            values.append(self.get_table_entry(TableIndex.SI, i))
        return values

    @step_increment.setter
    def step_increment(self, values):
        """
        Set the step increments to the configuration table. There are two
        possibilities to set the values:
        1) Give two values: [row, value]
        2) Give the eight values for all rows.
        :param values: [row,value] or [0..7 values]
        :return: None

        Documentation: SDC Manual section 3.5
        """
        if type(values) not in [tuple, list]:
            raise ValueError('The value should be a list/tuple. Read the help.')
        if len(values) == 2:
            self.set_table_entry(0, values[0], values[1])
        elif len(values) == 8:
            for row, value in enumerate(values):
                self.set_table_entry(TableIndex.SI, row, value)
        else:
            raise ValueError('The value is not correct. Read the help')

    @property
    def max_closed_loop_frequency(self):
        """
        Get the eight maximum closed loop frequency from the configuration table

        :return: [0..7] max_closed_loop_frequency

        Documentation: SDC Manual section 3.5
        """
        values = []
        for i in range(8):
            values.append(self.get_table_entry(TableIndex.MF, i))
        return values

    @max_closed_loop_frequency.setter
    def max_closed_loop_frequency(self, values):
        """
        Set the maximum closed loop frequency to the configuration table. There
        are two possibilities to set the values:
        1) Give two values: [row, value]
        2) Give the eight values for all rows.
        :param values: [row,value] or [0..7 values]
        :return: None

        Documentation: SDC Manual section 3.5
        """
        if type(values) not in [tuple, list]:
            raise ValueError(
                'The value should be a list/tuple. Read the help.')
        if len(values) == 2:
            self.set_table_entry(0, values[0], values[1])
        elif len(values) == 8:
            for row, value in enumerate(values):
                self.set_table_entry(TableIndex.MF, row, value)
        else:
            raise ValueError('The value is not correct. Read the help')

    ############################################################################
    #                       Commands
    ############################################################################
    def get_table_entry(self, table, row):
        """
        Gets the configuration table for the step-increment (0),
        max-closed-loop-frequency (1) and sensor-types-tables (2) fields.
        Channel Type: Positioner.

        :param table: any of the field codes.
        :param row: table entry.
        :return: entry value.

        Documentation: SDC Manual section 3.5
        """
        is_row_in_range(row)
        ans = self._send_cmd('GTE', table, row)
        return float(ans.split(',')[-1])

    def set_table_entry(self, table, row, value):
        """
        Sets a given table value entry specified by table and row.
        Channel Type: Positioner.

        :param table: any of the field codes.
        :param row: table entry.
        :param value: entry value
        :return: None

        Documentation: SDC Manual section 3.5
        """
        is_row_in_range(row)
        self._send_cmd('STE', table, row, int(value))


class SmaractMCSBaseAxis(SmaractBaseAxis):
    """
    Specific class for MCS controllers.
    """

    @property
    def channel_type(self):
        """
        Gets the type of channel.
        0: Positioner
        1: End Effector

        :return: channel type code

        Documentation: MCS Manual section 3.1
        """
        ans = self._send_cmd('GCT')
        ch_type = int(ans.split(',')[1])
        result = ['positioner', 'effector'][ch_type]
        return result

    @property
    def closed_loop_acc(self):
        """
        Gets acceleration value used for closed-loop commands.
        Channel Type: Positioner.

        :return: acceleration value.

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GCLA')
        return float(ans.split(',')[1])

    @closed_loop_acc.setter
    def closed_loop_acc(self, acceleration):
        """
        Sets acceleration value used for closed-loop commands.
        Channel Type: Positioner.

        :param acceleration: value
        :return: None

        Documentation: MCS Manual section 3.2
        """
        is_acceleration_in_range(acceleration)
        self._send_cmd('SCLA', acceleration)

    @property
    def closed_loop_vel(self):
        """
        Gets velocity value used for closed-loop commands.
        Channel Type: Positioner.

        :return: velocity value.

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GCLS')
        return float(ans.split(',')[1])

    @closed_loop_vel.setter
    def closed_loop_vel(self, velocity):
        """
        Sets velocity value used for closed-loop commands.
        Channel Type: Positioner.

        :param velocity: valocity value
        :return: None

        Documentation: MCS Manual section 3.2
        """
        is_velocity_in_range(velocity)
        self._send_cmd('SCLS', velocity)

    @property
    def scale(self):
        """
        Gets the current configured scale shift and if this is inverted.
        Channel Type: Positioner.

        :return: (scale shift, inverted flag)

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GSC')
        return [float(x) for x in ans.split(',')[-2:]]

    # TODO: analyze if it is enough with the channel properties.
    @scale.setter
    def scale(self, values):
        """
        Configures the logical scale of the positioner.
        Channel Type: Positioner.
        Inversion: 0: disabled, 1:enabled

        :param values: (scale shift, inverted flag)
        :return: None

        Documentation: MCS Manual section 3.2
        """
        if type(values) not in [tuple, list]:
            raise ValueError('The value should be a list/tuple read the help.')

        shift, inverted = values
        self._send_cmd('SSC', shift, inverted)

    @SmaractBaseAxis.sensor_type.setter
    def sensor_type(self, sensor_type):
        """
        Set the type of positioner attach to a channel.
        Channel Type: Positioner.

        :param sensor_type: sensor type code.
        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SST', sensor_type)

    @property
    def force(self):
        """
        Request the force measured by the sensor connected to the End Effector.
        Channel Type: End Effector.

        :return: force value in 1/10 uN

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GF')
        return float(ans.split(',')[-1])

    @property
    def gripper_opening(self):
        """
        Request the voltage currently applied to the gripper.
        Channel Type: End Effector.

        :return: voltage opening value in 1/100 Volts.

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GGO')
        return float(ans.split(',')[-1])

    @property
    def physical_position_known(self):
        """
        Returns whether the physical position is known.
        Channel Type: Positioner.

        :return: 0 (unknown) or 1 (known)

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GPPK')
        return int(ans.split(',')[1])

    @property
    def voltage_level(self):
        """
        Returns the voltage level which is currently applied to a positioner.
        Channel Type: Positioner.

        :return: 12-bit value (0-100 Volts)

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GVL')
        raw_data = float(ans.split(',')[-1])
        voltage = (raw_data * 100) / 4095
        return voltage

    @property
    def serial_number(self):
        """
        Retrieves the serial number of the channel.
        Channel Type: Positioner, End Effector.

        :return: serial number (hexadecimal).

        Documentation: MCS Manual section 3.5
        """
        return self._send_cmd('GSN')

    @property
    def firmware_version(self):
        """
        Retrieves the firmware version of the channel.
        Channel Type: Positioner, End Effector.

        :return: firmware version string code.

        Documentation: MCS Manual section 3.5
        """
        ans = self._send_cmd('GFV')
        _ver = ans.split(',')[1:]
        sc = "({0}){1}.{2}.{3}".format(*_ver[0:4])
        sg = "({0}){1}.{2}.{3}".format(*_ver[-4:])
        ret = "{0} - {1}".format(sc, sg)
        return ret

    @property
    def emergency_stop(self):
        """
        Read the emergency stop channel property.
        0: Normal (default)
        1: Restricted
        2: Disabled
        3: Auto Release

        :return: value

        Documentation: MCS Manual section 4.4
        """
        value = self.get_channel_property(ChannelProperties.EmergencyStop)

        return ['Normal', 'Restricted', 'Desabled', 'AutoRelease'][value]

    @emergency_stop.setter
    def emergency_stop(self, value):
        """
        Set the emergency stop channel property.
        0: Normal (default)
        1: Restricted
        2: Disabled
        3: AutoRelease

        :param value:
        :return:

        Documentation: MCS Manual section 4.4
        """
        value = value.lower()
        valid_values = ['normal', 'restricted', 'desabled', 'autorelease']
        if value not in valid_values:
            raise ValueError('Wrong value. Valid values: %r' % valid_values)
        idx = valid_values.index(value)
        self.set_channel_property(ChannelProperties.EmergencyStop, idx)

# TODO: Investigate why it raises error 157  
    # @property
#     def low_vibration(self):
#         """
#         Read the low vibration channel property.
#         0: Disabled (default)
#         1: Enabled
#         :return: value

#         Documentation: MCS Manual section 4.4
#         """
#         return self.get_channel_property(ChannelProperties.LowVibration)

#     @low_vibration.setter
#     def low_vibration(self, value):
#         """
#         Set the low vibration channel property.
#         0: Disabled (default)
#         1: Enabled

#         :param value:
#         :return:

#         Documentation: MCS Manual section 4.4
#         """
#         self.set_channel_property(ChannelProperties.LowVibration, value)

    @property
    def broadcast_stop(self):
        """
        Read the broadcast stop channel property.
        0: Disabled (default)
        1: Enabled
        :return: value

        Documentation: MCS Manual section 4.4
        """

        return bool(self.get_channel_property(ChannelProperties.BroadcastStop))

    @broadcast_stop.setter
    def broadcast_stop(self, value):
        """
        Set the broadcast stop channel property.
        0: Disabled (default)
        1: Enabled

        :param value:
        :return:

        Documentation: MCS Manual section 4.4
        """
        self.set_channel_property(ChannelProperties.BroadcastStop, int(value))

    @property
    def scale_inverted(self):
        """
        Read the scale inverted channel property.
        0: Normal (default)
        1: Inverted
        :return: value

        Documentation: MCS Manual section 4.4
        """
        return bool(self.get_channel_property(
            ChannelProperties.SensorScaleInverted))

    @scale_inverted.setter
    def scale_inverted(self, value):
        """
        Set the scale inverted channel property.
        0: Normal (default)
        1: Inverted

        :param value:
        :return:

        Documentation: MCS Manual section 4.4
        """
        self.set_channel_property(ChannelProperties.SensorScaleInverted,
                                  int(value))

    @property
    def scale_offset(self):
        """
        Read the scale offset stop channel property.
        :return: value

        Documentation: MCS Manual section 4.4
        """
        return self.get_channel_property(ChannelProperties.SensorScaleOffset)

    @scale_offset.setter
    def scale_offset(self, value):
        """
        Set the scale offset stop channel property.

        :param value:
        :return:

        Documentation: MCS Manual section 4.4
        """
        self.set_channel_property(ChannelProperties.SensorScaleOffset, value)

    ############################################################################
    #                       Commands
    ############################################################################
    def get_capture_buffer(self, buffer_idx):
        """
        Retrieves the contents of the capture buffer.
        Channel Type: Positioner.

        :param buffer_idx: buffer index for the selected channel.
        :return: (buffer index, data-1, data-2, ..., data-n)

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GB', buffer_idx)
        return [float(x) for x in ans.split(',')[2:]]

    def get_feature_permissions(self, byte_idx):
        """
        Retrieve the current feature permissions of a channel.
        Channel Type: Positioner, End Effector.

        :param byte_idx: feature byte targeted.
        :return: feature permissions size or feature bit code.

        Documentation: MCS Manual section 3.5
        """
        _ans = self._send_cmd('GFP', 255)
        n_feat_perm_bytes = _ans.split(',')[-1]
        if byte_idx <= n_feat_perm_bytes:
            ans = self._send_cmd('FP', byte_idx)
            return bin(ans.split(',')[-1])[-1]
        else:
            return -1

    def get_channel_property(self, key):
        """
        Retrieves a configuration value from a channel specified by key.
        Channel Type: Positioner.

        :param key: key value.
        :return: value retrieved.

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GCP', key)
        return int(ans.split(',')[-1])

    def get_end_effector_type(self):
        """
        Gets the current End Effector configuration specified by: type, param1
        and param2.
        Channel Type: End Effector.

        :return:

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GEET')
        return [int(x) for x in ans.split(',')[-3:]]

    def set_accumulate_rel_pos(self, enable=1):
        """
        Accumulate relative position command if is issued before finishing the
        movement. The total movement is the sum of the relative movements.
        Channel Type: Positioner.

        :param enable: 0 (no accumulation) 1 (accumulation).
        :return:

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SARP', enable)

    def set_closed_loop_max_freq(self, frequency):
        """
        Sets frequency value used for closed-loop commands.
        Channel Type: Positioner.

        :param frequency: value
        :return: None

        Documentation: MCS Manual section 3.2
        """
        is_frequency_in_range(frequency)
        self._send_cmd('SCLF', frequency)

    def set_channel_property(self, key, value):
        """
        Sets a given configuration value from a channel specified by key.
        Channel Type: Positioner.

        :param key: property key
        :param value: property value
        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SCP', key, value)

    def set_end_effector_type(self, eff_type, p1, p2):
        """
        Set a given configuration for an End Effector channel.
        Channel Type: End Effector.

        :param eff_type: effector type code.
        :param p1: parameter 1.
        :param p2: parameter 2.
        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SEET', eff_type, p1, p2)

    def set_position(self, position):
        """
        Defines current position with value position. For a rotatory positioner
        the revolution is implicitly 0.
        Channel Type: Positioner.

        :param position: value
        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SP', position)

    def set_report_on_complete(self, enable):
        """
        Report the completion of the last movement command.
        Channel Type: Positioner, End Effector.

        :param enable: 0 (no report) 1 (report).
        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SRC', enable)

    def set_report_on_triggered(self, enable):
        """
        Report when a movement command from the command queue has been
        triggered.
        Channel Type: Positioner.

        :param enable: 0 (no report) 1 (report).
        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SRT', enable)

    def set_step_while_scan(self, enable=1):
        """
        Enable/disable the execution of steps while holding a position after a
        closed-loop command. NOT IMPLEMENTED FOR ALL SMARACT CONTROLLERS!
        Channel Type: Positioner.

        :param enable: 0 (forbid steps) or 1 (allow steps).
        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SSW', enable)

    def set_zero_force(self):
        """
        Set the force measured to zero i.e. apply a tare.
        Channel Type: End Effector.

        :return: None

        Documentation: MCS Manual section 3.2
        """
        self._send_cmd('SZF')

    def append_triggered_command(self, trigger_source):
        """
        Append a trigger command to the queue for later execution.
        The command is only available with asynchronous communication.
        Channel Type: Positioner.

        :param trigger_source: trigger source code
        :return: None

        Documentation: MCS Manual section 3.3
        """
        self._send_cmd('ATC', trigger_source)

    def clean_triggered_command_queue(self):
        """
        Cancels ALL commands and epties the command queue.
        The command is only available with asynchronous communication.
        Channel Type: Positioner.

        :return: None

        Documentation: MCS Manual section 3.3
        """
        self._send_cmd('CTCQ')

    def move_gripper_force_absolute(self, force, speed, hold_time=0):
        """
        Command to grab an object with a constant force.
        Channel Type: End Effector

        :param force: force value
        :param speed: gripper open/close velocity
        :param hold_time: NOT IMPLEMENTED YET, set to 0.
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_force_in_range(force)
        is_speed_in_range(speed)
        is_hold_time_in_range(hold_time)
        self._send_cmd('MGFA', force, speed, hold_time)

    def move_gripper_opening_absolute(self, opening, speed):
        """
        Command to open/close the gripper. The opening value specifies how much
        the gripper gets closed. A value of 0 equals to gripper open.
        Channel Type: End Effector

        :param opening: target voltage to specify open/close condition.
        :param speed: gripper open/close velocity
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_opening_in_range(opening)
        is_speed_in_range(speed)
        self._send_cmd('MGOA', opening, speed)

    def move_gripper_opening_relative(self, opening, speed):
        """
        Command to open/close the gripper. The opening value specifies how much
        the gripper gets closed. A value of 0 equals to gripper open. This value
        is specified as a relative value.
        Channel Type: End Effector

        :param opening: target voltage to specify open/close condition.
        :param speed: gripper open/close velocity
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_opening_relative_in_range(opening)
        is_speed_in_range(speed)
        self._send_cmd('MGOR', opening, speed)

    def move_scan_absolute(self, target, scan_speed):
        """
        Perform a scanning movement of the positioner to a target scan position.
        Channel Type: Positioner.

        :param target: target scan position (12-bit value range).
        :param scan_speed: scan velocity
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_target_in_range(target)
        is_scan_speed_in_range(scan_speed)
        self._send_cmd('MSCA', target, scan_speed)

    def move_scan_relative(self, target, scan_speed):
        """
        Perform a relative scanning movement of the positioner to a target scan
        position.
        Channel Type: Positioner.

        :param target: target scan position (12-bit value range).
        :param scan_speed: scan velocity
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_target_relative_in_range(target)
        is_scan_speed_in_range(scan_speed)
        self._send_cmd('MSCR', target, scan_speed)


class SmaractMCSAngularAxis(SmaractMCSBaseAxis):
    """
    Specific class for MCS controllers Rotatory Sensors.
    """
    @property
    def position(self):
        """
        Gets the current position of a positioner.
        Channel Type: Positioner.

        :return: current positioner position in degree.

        Documentation: MCS Manual section 3.4
        """
        ans = self._send_cmd('GA')
        angle, revolution = [float(x) for x in ans.split(',')[-2:]]
        position = (revolution * TURN) + angle
        return position

    @property
    def position_limits(self):
        """
        Gets the travel range limit currently configured for the channel.
        Channel Type: Positioner.

        :return: (min position, max_position)

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GAL')
        # Answer (minAngle, minRev, maxAngle, maxRev)
        values = [float(x) for x in ans.split(',')[-4:]]
        min_angle = (values[1] * TURN) + values[0]
        max_angle = (values[3] * TURN) + values[2]
        return [min_angle, max_angle]

    @position_limits.setter
    def position_limits(self, limits):
        """
        Sets the travel range limit currently configured.
        Channel Type: Positioner.

        :param limits: (min_position, max_position)
        :return: None

        Documentation: MCS Manual section 3.2
        """
        if type(limits) not in [tuple, list]:
            raise ValueError('The value should be a list/tuple read the help.')

        values = []
        for limit in limits:
            angle, revolutions = self._angle_rev(limit)
            values.append(angle)  # angle
            values.append(revolutions)  # revolution
        self._send_cmd('SAL', *values)

    ############################################################################
    #                       Commands
    ############################################################################
    def move(self, position, hold_time=0):
        """
        Move method. The units are micro-degrees and milliseconds.
        :param relative_pos: the position is the absolute total angle
        :return:
        """
        angle, revolutions = self._angle_rev(position)
        hold_time = int(hold_time)
        self.move_angle_absolute(angle, revolutions, hold_time)

    def _angle_rev(self, position):
        sign = 0
        if position < 0:
            sign = -1
        angle = int(position % TURN)
        revolutions = int(position / TURN) + sign
        return angle, revolutions

    def move_angle_absolute(self, angle, rev, hold_time=0):
        """
        Instructs the positioner to turn to a specific angle value.
        The units are micro-degree and millisecond
        Channel Type: Positioner.

        :param angle: target angle.
        :param rev: number of turns.
        :param hold_time: hold the movement for this amount of time in ms.
        :return: None

        Documentation: MCS Manual section 3.2
        """
        is_angle_in_range(angle)
        is_revolution_in_range(rev)
        is_hold_time_in_range(hold_time)
        self._send_cmd('MAA', angle, rev, hold_time)

    def move_angle_relative(self, angle, rev, hold_time=0):
        """
        Instructs the positioner to turn to an angle relative to its current
        position.
        The units are micro-degree and millisecond
        Channel Type: Positioner.

        :param angle: angle increment.
        :param rev: turns increment.
        :param hold_time: hold the movement for this amount of time in ms.
        :return: None

        Documentation: MCS Manual section 3.2
        """
        is_angle_relative_in_range(angle)
        is_revolution_in_range(rev)
        is_hold_time_in_range(hold_time)
        self._send_cmd('MAR', angle, rev, hold_time)


class SmaractMCSLinearAxis(SmaractMCSBaseAxis):
    """
    Specific class for MCS controllers Linear Sensors.
    """
    @property
    def position_limits(self):
        """
        Gets the travel range limit currently configured for a linear channel.
        Channel Type: Positioner.

        :return: (min position, max_position)

        Documentation: MCS Manual section 3.2
        """
        ans = self._send_cmd('GPL')
        return [float(x) for x in ans.split(',')[-2:]]

    @position_limits.setter
    def position_limits(self, limits):
        """
        Sets the travel range limit currently configured for a linear channel.
        Channel Type: Positioner.

        :param limits: (min position, max_position)
        :return: None

        Documentation: MCS Manual section 3.2
        """
        if type(limits) not in [tuple, list]:
            raise ValueError('The value should be a list/tuple read the help.')

        min_pos, max_pos = limits
        self._send_cmd('SPL', min_pos, max_pos)

    ############################################################################
    #                       Commands
    ############################################################################
    def move(self, position, hold_time=0):
        """
        Move method
        :param position: the position is the absolute total angle
        :return:
        """
        hold_time = int(hold_time)
        self.move_position_absolute(position, hold_time)

    def move_position_absolute(self, position, hold_time=0):
        """
        Instructs the positioner to move to a specific position value.
        Channel Type: Positioner.

        :param position: target position
        :param hold_time: hold the movement for this amount of time in ms.
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_hold_time_in_range(hold_time)
        self._send_cmd('MPA', position, hold_time)

    def move_position_relative(self, position, hold_time=0):
        """
        Instructs the positioner to move to a specific value relative to its
        current position..
        Channel Type: Positioner.

        :param position: position increment
        :param hold_time: hold the movement for this amount of time in ms.
        :return: None

        Documentation: MCS Manual section 3.3
        """
        is_hold_time_in_range(hold_time)
        self._send_cmd('MPR', position, hold_time)
