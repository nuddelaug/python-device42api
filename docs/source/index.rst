.. python-device42api documentation master file, created by
   sphinx-quickstart on Tue Apr  1 15:30:29 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-device42api's documentation!
==============================================

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. automodule:: device42api
       :members:


Example usage
=============

following steps are necessary (in order) to get a device deployed in a Rack/Room/Building.

create Hardware representing our device(s)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    import device42api
    api             = device42api.Device42API(hostame='localhost', username='admin', password='changeme')
    size            = 2
    hw              = device42api.Hardware(api=api)
    hw.name         = 'Generic Hardware %sU' % size
    hw.type         = 1
    hw.size         = size
    hw.depth        = 1
    hw.manufacturer = 'Test'
    hw.save()
    {'msg': ['hardware model added or updated', 1, 'Generic Hardware 2U', True, True], 'code': 0}

create a Building
^^^^^^^^^^^^^^^^^

::

    import device42api
    api             = device42api.Device42API(hostame='localhost', username='admin', password='changeme')
    b               = device42api.Building(api=api)
    b.name          = 'Test Building'
    b.address       = 'somewhere in the city'
    b.notes         = 'destruction ongoing, leave the building immediatley'
    b.save()
    {'msg': ['Building added/updated successfully', 1, 'TestBuilding', True, True], 'code': 0}

create a Room in our Building
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # assume that you've also executed "create a Building"
    import device42api
    api                 = device42api.Device42API(hostame='localhost', username='admin', password='changeme')
    room                = device42api.Room(api=api)
    room.name           = 'Test Room'
    room.building       = b.name
    room.building_id    = b.building_id
    room.notes          = 'coffee corner for sysadmins'
    room.save()
    {'msg': ['Room added/updated successfully', 1, 'Test Room', True, True], 'code': 0}

create a Rack in our Room
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # assume that you've also executed "create a Room"
    import device42api
    api             = device42api.Device42API(hostame='localhost', username='admin', password='changeme')
    room            = device42api.Room(api=api)
    room.room_id    = 1
    room.load()
    rack            = device42api.Rack(api=api)
    rack.name       = 'Test Rack'
    rack.size       = 42
    rack.room       = room.name
    rack.building   = room.building
    rack.room_id    = room.room_id
    rack.numbering_start_from_botton = 'no'
    rack.notes         = 'First Rack'
    rack.save()
    {'msg': ['rack added/updated.', 1, 'Test Rack', True, True], 'code': 0}

create a Device
^^^^^^^^^^^^^^^

::

    import device42api
    api                     = device42api.Device42API(hostame='localhost', username='admin', password='changeme')
    device                  = device42api.Device(api=api)
    device.name             = 'Test Device'    
    device.serial_no        = '0123456789'
    device.hardware         = 'Generic Hardware 2U'
    device.in_service       = 'yes'
    device.type             = 'physical'
    device.service_level    = 'production'
    device.os               = 'RHEL Server'
    device.osver            = 6.5
    device.memory           = 16.000
    device.cpucount         = 80
    device.cpucore          = 8
    device.notes            = 'Test Device'
    device.save()
    {'msg': ['device added or updated', 1, 'Test Device', True, True], 'code': 0}

added macAddress and ipAddress for the Device
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    import device42api
    api                     = device42api.Device42API(hostame='localhost', username='admin', password='changeme')
    device                  = device42api.Device(api=api)
    device.device_id        = 1
    device.load()
    for mA, iA, dN in (('00:11:22:33:44:55', '127.0.0.1', 'eth0'),
                       ('00:11:22:33:44:66', '127.0.0.2', 'eth1')):
        mac             = device42api.IPAM_macaddress(api=api)
        mac.macaddress  = mA
        mac.port_name   = dN
        mac.device      = device.name
        mac.save()
        ip              = device42api.IPAM_ipaddress(api=api)
        ip.ipaddress    = iA
        ip.tag          = mac.port_name
        ip.macaddress   = mac.macaddress
        ip.device       = device.name
        ip.save()

add the Device to the Rack created
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    import device42api
    api                 = device42api.Device42API(hostame='localhost', username='admin', password='changeme')
    rack                = device42api.Rack(api=api)
    rack.rack_id        = 1
    rack.load()
    device              = device42api.Device(api=api)
    device.device_id    = 1
    device.load()
    rack.add_device(device, start_at=1)
    
it might be that in future releases you can simple do a *rack.save()* instead of rack_add_device but due to lack of time (and license) I wasn't able
to implement this already.
