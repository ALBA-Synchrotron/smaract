import weakref
from .constants import *


class SmaractBaseAxis(object):
    """
    Smaract Axis Base class. Contains the common Smaract ASCii API for any
    Smaract axis. The methods here implemented correspond to those
    at the axis level. The _send_cmd function wrappers the current controller
    _send_cmd method.
    """
    def __init__(self, parent, axis_nr=0):
        self._axis_nr = axis_nr
        self._parent = weakref.ref(parent)

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
        return self._parent.send_cmd(cmd)

    # 3.2 - Configuration commands
    # -------------------------------------------------------------------------
    def get_safe_direction(self):
        """
        Gets the current configured safe direction.
        0: forward (FORWARD).
        1: backward (BACKWARD).
        Channel Type: Positioner.

        :return: either 0 or 1.
        """
        ans = self._send_cmd('GSD')
        return int(ans[-1])

    def set_safe_direction(self, direction):
        """
        Sets the current configured safe direction.
        Channel Type: Positioner.

        :param direction: either 0 (forward) or 1 (backward).
        :return: None
        """
        self._send_cmd('SSD', direction)

    def get_sensor_type(self):
        """
        Gets the type of sensor connected.
        Channel Type: Positioner.

        :return: Sensor code.
        """
        ans = self._send_cmd('GST')
        sensor_code = int(ans.rsplit(',', 1)[1])
        return self._parent.SENSOR_CODE[sensor_code]

    # 3.3 - Movement controls commands
    # -------------------------------------------------------------------------
    def calibrate_sensor(self):
        """
        Increase the accuracy of the position calculation.
        Channel Type: Positioner.

        :return: None
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
        """
        self._send_cmd('S')

    # 3.4 - Positioner feedback commands
    # -------------------------------------------------------------------------
    def get_position(self):
        """
        Gets the current position of a positioner.
        Channel Type: Positioner.

        :return: current positioner position.
        """
        ans = self._send_cmd('GP')
        return float(ans.split(',')[1])

    def get_status(self):
        """
        Get the current movement status of the positioner or end effector.
        Channel Type: Positioner, End Effector.

        :return: channel status code.
        """
        ans = self._send_cmd('GS')
        return int(ans.split(',')[1])


class SmaractSDCAxis(SmaractBaseAxis):
    """
    Specific class for SDC controllers.
    """

    # 3.4 - Positioner feedback commands
    # -------------------------------------------------------------------------
    def get_target_position(self):
        """
        Gets the current target position (working as slave).
        Channel Type: Positioner.

        :return: current target position.
        """
        ans = self._send_cmd('GTP')
        return float(ans.split(',')[1])

    # 3.5 - Miscellaneous commands
    # -------------------------------------------------------------------------
    def get_error_status(self):
        """
        Gets the latest error code.
        Channel Type: Positioner.

        :return: error code.
        """
        ans = self._send_cmd('GES')
        return int(ans.split(',')[1, 2])

    def get_error_queue(self):
        """
        Gets all error in queue.
        Channel Type: Positioner.

        :return: list with error list.
        """
        err_list = list()
        err, rem = self.get_error_status()
        err_list.append(err)
        while rem != 0:
            err, rem = self.get_error_status()
            err_list.append(err)
        return err_list

    def get_table_entry(self, table, row):
        """
        Gets the configuration table for the step-increment (0),
        max-closed-loop-frequency (1) and sensor-types-tables (2) fields.
        Channel Type: Positioner.

        :param table: any of the field codes.
        :param row: table entry.
        :return: entry value.
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
        """
        is_row_in_range(row)
        self._send_cmd('STE', table, row, int(value))


class SmaractMCSBaseAxis(SmaractBaseAxis):
    """
    Specific class for MCS controllers.
    """

    # 3.1 - Initialization commands
    # -------------------------------------------------------------------------
    def get_channel_type(self):
        """
        Gets the type of channel.
        0: Positioner
        1: End Effector

        :return: channel type code
        """
        ans = self._send_cmd('GCT')
        return float(ans.split(',')[1])

    # 3.2 - Configuration commands
    # -------------------------------------------------------------------------
    def get_closed_loop_acc(self):
        """
        Gets acceleration value used for closed-loop commands.
        Channel Type: Positioner.

        :return: acceleration value.
        """
        ans = self._send_cmd('GCLA')
        return float(ans.split(',')[1])

    def get_closed_loop_vel(self):
        """
        Gets velocity value used for closed-loop commands.
        Channel Type: Positioner.

        :return: velocity value.
        """
        ans = self._send_cmd('GCLS')
        return float(ans.split(',')[1])

    def get_channel_property(self, key):
        """
        Retrieves a configuration value from a channel specified by key.
        Channel Type: Positioner.

        :param key: key value.
        :return: value retrieved.
        """
        ans = self._send_cmd('GCLS', key)
        return int(ans.split(',')[-1])

    def get_end_effector_type(self):
        """
        Gets the current End Effector configuration specified by: type, param1
        and param2.
        Channel Type: End Effector.

        :return:
        """
        ans = self._send_cmd('GEET')
        return [int(x) for x in ans.split(',')[-3:]]

    def get_scale(self):
        """
        Gets the current configured scale shift and if this is inverted.
        Channel Type: Positioner.

        :return: (scale shift, inverted flag)
        """
        ans = self._send_cmd('GSC')
        return [float(x) for x in ans.split(',')[-2:]]

    def set_accumulate_rel_pos(self, enable=1):
        """
        Accumulate relative position command if is issued before finishing the
        movement. The total movement is the sum of the relative movements.
        Channel Type: Positioner.

        :param enable: 0 (no accumulation) 1 (accumulation).
        :return:
        """
        self._send_cmd('SARP', enable)

    def set_closed_loop_acc(self, acceleration):
        """
        Sets acceleration value used for closed-loop commands.
        Channel Type: Positioner.

        :param acceleration: value
        :return: None
        """
        is_acceleration_in_range(acceleration)
        self._send_cmd(('SCLA', acceleration))

    def set_closed_loop_max_freq(self, frequency):
        """
        Sets frequency value used for closed-loop commands.
        Channel Type: Positioner.

        :param frequency: value
        :return: None
        """
        is_frequency_in_range(frequency)
        self._send_cmd('SCLF', frequency)

    def set_closed_loop_vel(self, velocity):
        """
        Sets velocity value used for closed-loop commands.
        Channel Type: Positioner.

        :param velocity: valocity value
        :return: None
        """
        is_velocity_in_range(velocity)
        self._send_cmd(('SCLS', velocity))

    def set_channel_property(self, key, value):
        """
        Sets a given configuration value from a channel specified by key.
        Channel Type: Positioner.

        :param key: property key
        :param value: property value
        :return: None
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
        """
        self._send_cmd('SEET', eff_type, p1, p2)

    def set_position(self, position):
        """
        Defines current position with value position. For a rotatory positioner
        the revolution is implicitly 0.
        Channel Type: Positioner.

        :param position: value
        :return: None
        """
        self._send_cmd('SP', position)

    def set_report_on_complete(self, enable):
        """
        Report the completion of the last movement command.
        Channel Type: Positioner, End Effector.

        :param enable: 0 (no report) 1 (report).
        :return: None
        """
        self._send_cmd('SRC', enable)

    def set_report_on_triggered(self, enable):
        """
        Report when a movement command from the command queue has been
        triggered.
        Channel Type: Positioner.

        :param enable: 0 (no report) 1 (report).
        :return: None
        """
        self._send_cmd('SRT', enable)

    def set_scale(self, shift, inverted):
        """
        Configures the logical scale of the positioner.
        Channel Type: Positioner.

        :param shift: relative shift to the physical scale.
        :param inverted: scale inversion (0: disabled, 1:enabled).
        :return: None
        """
        self._send_cmd('SSC', shift, inverted)

    def set_sensor_type(self, sensor_type):
        """
        Set the type of positioner attach to a channel.
        Channel Type: Positioner.

        :param sensor_type: sensor type code.
        :return: None
        """
        self._send_cmd('SST', sensor_type)

    def set_step_while_scan(self, enable=1):
        """
        Enable/disable the execution of steps while holding a position after a
        closed-loop command. NOT IMPLEMENTED FOR ALL SMARACT CONTROLLERS!
        Channel Type: Positioner.

        :param enable: 0 (forbid steps) or 1 (allow steps).
        :return: None
        """
        self._send_cmd('SSW', enable)

    def set_zero_force(self):
        """
        Set the force measured to zero i.e. apply a tare.
        Channel Type: End Effector.

        :return: None
        """
        self._send_cmd('SZF')

    # 3.2 - Movement control commands
    # -------------------------------------------------------------------------
    def append_triggered_command(self, trigger_source):
        """
        Append a trigger command to the queue for later execution.
        The command is only available with asynchronous communication.
        Channel Type: Positioner.

        :param trigger_source: trigger source code
        :return: None
        """
        self._send_cmd('ATC', trigger_source)

    def clean_triggered_command_queue(self):
        """
        Cancels ALL commands and epties the command queue.
        The command is only available with asynchronous communication.
        Channel Type: Positioner.

        :return: None
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
        """
        is_opening_relative_in_range(opening)
        is_speed_in_range(speed)
        self._send_cmd('MGOA', opening, speed)

    def move_scan_absolute(self, target, scan_speed):
        """
        Perform a scanning movement of the positioner to a target scan position.
        Channel Type: Positioner.

        :param target: target scan position (12-bit value range).
        :param scan_speed: scan velocity
        :return: None
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
        """
        is_target_relative_in_range(target)
        is_scan_speed_in_range(scan_speed)
        self._send_cmd('MSCR', target, scan_speed)

    # 3.4 - Positioner feedback commands
    # -------------------------------------------------------------------------
    def get_capture_buffer(self, buffer_idx):
        """
        Retrieves the contents of the capture buffer.
        Channel Type: Positioner.

        :param buffer_idx: buffer index for the selected channel.
        :return: (buffer index, data-1, data-2, ..., data-n)
        """
        ans = self._send_cmd('GB', buffer_idx)
        return [float(x) for x in ans.split(',')[2:]]

    def get_force(self):
        """
        Request the force measured by the sensor connected to the End Effector.
        Channel Type: End Effector.

        :return: force value in 1/10 uN
        """
        ans = self._send_cmd('GF')
        return float(ans.split(',')[-1])

    def get_gripper_opening(self):
        """
        Request the voltage currently applied to the gripper.
        Channel Type: End Effector.

        :return: voltage opening value in 1/100 Volts.
        """
        ans = self._send_cmd('GGO')
        return float(ans.split(',')[-1])

    def get_physical_position_known(self):
        """
        Returns whether the physical position is known.
        Channel Type: Positioner.

        :return: 0 (unknown) or 1 (known)
        """
        ans = self._send_cmd('GPPK')
        return int(ans.split(',')[1])

    def get_voltage_level(self):
        """
        Returns the voltage level which is currently applied to a positioner.
        Channel Type: Positioner.

        :return: 12-bit value (0-100 Volts)
        """
        ans = self._send_cmd('GVL')
        return float(ans.split(',')[-1])

    # 3.5 - Miscellaneous commands
    # -------------------------------------------------------------------------
    def get_serial_number(self):
        """
        Retrieves the serial number of the channel.
        Channel Type: Positioner, End Effector.

        :return: serial number (hexadecimal).
        """
        self._send_cmd('GSN')

    def get_firmware_version(self):
        """
        Retrieves the firmware version of the channel.
        Channel Type: Positioner, End Effector.

        :return: firmware version string code.
        """
        ans = self._send_cmd('GFV')
        # TODO: create human-readable string for return
        return ans.split(',')[1:]

    def get_feature_permissions(self, byte_idx):
        """
        Retrieve the current feature permissions of a channel.
        Channel Type: Positioner, End Effector.

        :param byte_idx: feature byte targeted.
        :return: feature permissions size or feature bit code.
        """
        _ans = self._send_cmd('GFP', 255)
        n_feat_perm_bytes = _ans.split(',')[-1]
        if byte_idx <= n_feat_perm_bytes:
            ans = self._send_cmd('FP', byte_idx)
            return bin(ans.split(',')[-1])[-1]
        else:
            return -1


class SmaractMCSAngularAxis(SmaractMCSBaseAxis):

    # 3.2 - Configuration commands
    # -------------------------------------------------------------------------
    def get_angle_limit(self):
        """
        Gets the travel range limit currently configured for a rotatory channel.
        Channel Type: Positioner.

        :return: (minAngle, minRev, maxAngle, maxRev)
        """
        ans = self._send_cmd('GAL')
        return [float(x) for x in ans.split(',')[-4:]]

    def set_angle_limit(self, min_angle, min_rev, max_angle, max_rev):
        """
        Sets the travel range limit currently configured for a rotatory channel.
        Channel Type: Positioner.

        :param min_angle: minimum angle value.
        :param min_rev: minimum revolutions value.
        :param max_angle: maximum angle value.
        :param max_rev: maximum revolutions value.
        :return: None
        """
        is_angle_in_range([min_angle, max_angle])
        is_revolution_in_range([min_rev, max_rev])
        self._send_cmd('SAL', min_angle, min_rev, max_angle, max_rev)

    def move_angle_absolute(self, angle, rev, hold_time=0):
        """
        Instructs the positioner to turn to a specific angle value.
        Channel Type: Positioner.

        :param angle: target angle.
        :param rev: number of turns.
        :param hold_time: hold the movement for this amount of time in ms.
        :return: None
        """
        is_angle_in_range(angle)
        is_revolution_in_range(rev)
        is_hold_time_in_range(hold_time)
        self._send_cmd('MAA', angle, rev, hold_time)

    def move_angle_relative(self, angle, rev, hold_time=0):
        """
        Instructs the positioner to turn to an angle relative to its current
        position.
        Channel Type: Positioner.

        :param angle: angle increment.
        :param rev: turns increment.
        :param hold_time: hold the movement for this amount of time in ms.
        :return: None
        """
        is_angle_relative_in_range(angle)
        is_revolution_in_range(rev)
        is_hold_time_in_range(hold_time)
        self._send_cmd('MAR', angle, rev, hold_time)

    # 3.4 - Positioner feedback commands
    # -------------------------------------------------------------------------
    def get_angle(self):
        """
        Request the current angle of a positioner.
        Channel Type: Positioner.

        :return: (angle, revolution) in udeg.
        """
        ans = self._send_cmd('GA')
        # TODO: convert tuple (angle, rev) to angle.
        return [float(x) for x in ans.split(',')[-2:]]


class SmaractMCSLinearAxis(SmaractMCSBaseAxis):

    def set_position_limit(self, min_pos, max_pos):
        """
        Sets the travel range limit currently configured for a linear channel.
        Channel Type: Positioner.

        :param min_pos: minimum position.
        :param max_pos: maximum position.
        :return: None
        """
        self._send_cmd('SPL', min_pos, max_pos)

    def get_position_limit(self):
        """
        Gets the travel range limit currently configured for a linear channel.
        Channel Type: Positioner.

        :return: (min position, max_position)
        """
        ans = self._send_cmd('GPL')
        return [float(x) for x in ans.split(',')[-2:]]

    def move_position_absolute(self, position, hold_time=0):
        """
        Instructs the positioner to move to a specific position value.
        Channel Type: Positioner.

        :param position: target position
        :param hold_time: hold the movement for this amount of time in ms.
        :return: None
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
        """
        is_hold_time_in_range(hold_time)
        self._send_cmd('MPR', position, hold_time)
