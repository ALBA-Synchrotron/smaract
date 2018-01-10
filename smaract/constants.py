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


# Smaract controller constants
MAX_FREQUENCY = 18500
MIN_FREQUENCY = 50
MAX_AMPLITUDE = 4095
MAX_STEPS = 30000
MAX_ACCELERATION = 10e7
MAX_VELOCITY = 10e8
MAX_ANGLE = 359999999
MIN_ANGLE = 0
MAX_REV = 32767
MIN_REV = -32768
MIN_FORCE = -10e6
MAX_FORCE = 10e6
MIN_SPEED = 1
MAX_SPEED = 225000
MIN_OPENING = 0
MAX_OPENING = 22500
MIN_TARGET = 0
MAX_TARGET = 4095
MIN_SCAN_SPEED = 0
MAX_SCAN_SPEED = 4095e6
MIN_BAUDRATE = 9600
MAX_BAUDRATE = 115200
MIN_DELAY = 100
MAX_DELAY = 60000
TRIGGER_INDEX_0 = 1792
MIN_TRIGGER = 0
MAX_TRIGGER = 255
MIN_HOLD_TIME = 0
MAX_HOLD_TIME = 60000

TURN = 360*1e6


class Status(object):
    """
    Smaract Status codes
    """
    STOPPED = 0
    STEPPING = 1
    SCANNING = 2
    HOLDING = 3
    TARGETING = 4
    WAITING = 5
    CALIBRATING = 6
    HOMING = 7
    LOCKED = 9

    states_txt = {0: 'Stopped',
                  1: 'Stepping',
                  2: 'Scanning',
                  3: 'Holding',
                  4: 'Targeting',
                  5: 'Move delay',
                  6: 'Calibrating',
                  7: 'Finding reference mark',
                  9: 'Locked'}
    
    status_txt = {0: 'The positioner is currently not performing any active ' 
                     'movement.',
                  1: 'The positioner is performing an open-loop movement.',
                  2: 'The positioner is performing a scanning movement.',
                  3: 'The positioner is holding its current target position '
                     'or is holding the reference mark',
                  4: 'The positioner is performing a close-loop movement.',
                  5: 'The positioner is currently waiting for the sensor to '
                     'power up before executing the movement command. This '
                     'status may be returned if the sensors are operated '
                     ' in power save mode.',
                  6: 'The positioner is buusy calibrating its sensor.',
                  7: 'The positioner is moving to find the reference mark.',
                  9: 'An emergency stop has occurred and further movements '
                     'are not allowed.'
                  }


class ChannelProperties(object):
    """
    Smaract channel properties
    """
    EmergencyStop = 16842753
    EmergencyStopDefault = 16842797
    LowVibration = 16908289
    BroadcastStop = 17039361
    PositionControl = 17104913
    SensorPowerSupply = 134938625
    SensorScaleOffset = 135659567
    SensorScaleInverted = 135659539
    DigitalIn = 33554433
    DigitalInEdge = 33554434
    CounterTriggerSource = 67108867
    Counter = 67108869
    CaptureBuffer = 83886083
    QueueSize = 100663300
    QueueCapacity = 100663302


class Direction(object):
    """
    Smaract motion constants (Find Reference Mark method).
    """
    FORWARD = 0
    BACKWARD = 1
    FORWARD_BACKWARD = 2
    BACKWARD_FORWARD = 3
    FORWARD_ABORT_ON_END = 4
    BACKWARD_ABORT_ON_END = 5
    FORWARD_BACKWARD_ABORT_ON_END = 6
    BACKWARD_FORWARD_ABORT_ON_END = 7


class TableIndex(object):
    """
    Table indexed to access controller configuration (only SDC) .
    SI: Step Increment.
    MF: Maximum closed loop frequency.
    ST: Sensor Type.
    """
    SI = 0
    MF = 1
    ST = 2


class CommunicationMode(object):
    """
    Defines the communication modes available
    """
    SYNC = 0
    ASYNC = 1


class ChannelType(object):
    """
    Defines the channel types available
    """
    POSITIONER = 0
    EFFECTOR = 1


class HandControlModuleMode(object):
    """
    Defines the hand-control module operation modes available.
    """
    DISABLED = 0
    ENABLED = 1
    READONLY = 2


class SensorMode(object):
    """
    Defines the sensor operation modes available.
    """
    DISABLED = 0
    ENABLED = 1
    POWER_SAVE = 2


class EffectorType(object):
    """
    Define the end effector types available.
    """
    GRIPPER = 1
    FORCE_SENSOR = 2
    FORCE_GRIPPER = 3


def is_angle_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) angle value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_ANGLE <= value <= MAX_ANGLE):
            msg = 'Valid angle range: [%d, %d] s' %\
                  (MIN_ANGLE, MAX_ANGLE)
            raise ValueError(msg)


def is_angle_relative_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) angle value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (-MAX_ANGLE <= value <= MAX_ANGLE):
            msg = 'Valid relative angle range: [%d, %d] s' %\
                  (-MAX_ANGLE, MAX_ANGLE)
            raise ValueError(msg)


def is_acceleration_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) acceleration value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (0 <= value <= MAX_ACCELERATION):
            msg = 'Valid acceleration range: [0,%d] um/s^2' %\
                  MAX_ACCELERATION
            raise ValueError(msg)


def is_revolution_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) revolution value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_REV <= value <= MAX_REV):
            msg = 'Valid revolution range: [%d, %d] s' %\
                  (MIN_REV, MAX_REV)
            raise ValueError(msg)


def is_steps_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) step value(s).
    :return: None
    """
    if type(values) is not list:
        values = (values)
    for value in values:
        if abs(value) > MAX_STEPS or value == 0:
            msg = 'Valid step range is [-%d, %d]' % (MAX_STEPS, MAX_STEPS)
            raise ValueError(msg)


def is_amplitude_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) amplitude value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if value < 0 or value > MAX_AMPLITUDE:
            msg = 'Valid amplitude range is (0, %d)' % MAX_AMPLITUDE
            raise ValueError(msg)


def is_frequency_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) frequency value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if value < 0 or value > MAX_FREQUENCY:
            msg = 'Valid frequency range is (0, %d]' % MAX_FREQUENCY
            raise ValueError(msg)


def is_velocity_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) velocity value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (0 <= value <= MAX_VELOCITY):
            msg = 'Valid velocity range: [0,%d] nm/s' % MAX_VELOCITY
            raise ValueError(msg)


def is_speed_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) speed value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_SPEED <= value <= MAX_SPEED):
            msg = 'Valid speed range: [%d,%d] Volts/s' % (MIN_SPEED, MAX_SPEED)
            raise ValueError(msg)


def is_force_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) force value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_FORCE <= value <= MAX_FORCE):
            msg = 'Valid force range: [%d,%d] 10 x uN' % (MIN_FORCE, MAX_FORCE)
            raise ValueError(msg)


def is_opening_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) opening value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_OPENING <= value <= MAX_OPENING):
            msg = 'Valid opening range: [%d,%d] 1/100 Volts' %\
                  (MIN_OPENING, MAX_OPENING)
            raise ValueError(msg)


def is_opening_relative_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) opening value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (-MAX_OPENING <= value <= MAX_OPENING):
            msg = 'Valid relative opening range: [%d,%d] 1/100 Volts' %\
                  (-MAX_OPENING, MAX_OPENING)
            raise ValueError(msg)


def is_target_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) target value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_TARGET <= value <= MAX_TARGET):
            msg = 'Valid target range: [%d,%d] (12-bit)' %\
                  (MIN_TARGET, MAX_TARGET)
            raise ValueError(msg)


def is_target_relative_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) target value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (-MAX_TARGET <= value <= MAX_TARGET):
            msg = 'Valid relative target range: [%d,%d] (12-bit)' % \
                  (-MAX_TARGET, MAX_TARGET)
            raise ValueError(msg)


def is_scan_speed_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) scan speed value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_SCAN_SPEED <= value <= MAX_SCAN_SPEED):
            msg = 'Valid scan speed range: [%d,%d] (12-bit/s)' %\
                  (MIN_TARGET, MAX_TARGET)
            raise ValueError(msg)


def is_trigger_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) trigger value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_TRIGGER <= value <= MAX_TRIGGER):
            msg = 'Valid trigger range: [%d,%d]' %\
                  (MIN_TRIGGER, MAX_TRIGGER)
            raise ValueError(msg)


def is_baudrate_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) baudrate value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_BAUDRATE <= value <= MAX_BAUDRATE):
            msg = 'Valid baudrate range: [%d,%d]' %\
                  (MIN_TRIGGER, MAX_TRIGGER)
            raise ValueError(msg)


def is_delay_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) delay value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_DELAY <= value <= MAX_DELAY):
            msg = 'Valid delay range: [%d,%d] ms' %\
                  (MIN_DELAY, MAX_DELAY)
            raise ValueError(msg)


def is_row_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) row value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if value < 0 or value > 7:
            raise ValueError('Valid row range is [0,7]')


def is_hold_time_in_range(values):
    """
    Checks that values are within the valid range defined.
    :param values: (list of) hold time value(s).
    :return: None
    """
    if type(values) is not list:
        values = [values]
    for value in values:
        if not (MIN_HOLD_TIME <= value <= MAX_HOLD_TIME):
            msg = 'Valid hold time range: [%d,%d] ms' %\
                  (MIN_HOLD_TIME, MAX_HOLD_TIME)
            raise ValueError(msg)
