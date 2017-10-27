*******************
Smaract Users Guide
*******************


Smaract Units
-------------

The smaract python library does not change the units used by the controller.
So, this is the list of unit used to interface the controller commands:

* *Distance:* nanometers [`nm`]
* *Time:* milliseconds [`ms`]
* *Linear velocity:* nanometers/second [`nm/s`]
* *Linear acceleration:* micrometers/second^2 [`um/s^2`]
* *Angular velocity:* micro-degrees/second [`udeg/s`]
* *Angular acceleration:* milli-degrees/second^2 [`mdeg/s^2`]

Angular references
------------------

In order to provide a user-friendly API to specify angular positions (for
instance, to provide target positions or limits), we provide the following
formula which translate a user angular value :math:`\theta` to the expected SmarAct values
(`angle` and `revolution`) in default units (udeg):

.. math::

    \theta = revolution * 360*1e6 + angle

For example, the position `-45 deg` corresponds to `angle=315*1e6` and `revoution=-1`.

Connecting to the MCS controller
--------------------------------

This example is based on the MCS API.

.. code-block:: python

    from smaract import SmaractMCSController, CommType
    mcs = SmaractMCSController(CommType.Socket, <ip_address>, <port=5000>, <timeout=3>)

The `SmaractMCSController` class exposes each axis as as an element of the `mcs`
object.



