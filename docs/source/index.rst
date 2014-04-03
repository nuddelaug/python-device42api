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

* create Hardware representing our device(s)
* create a Building
* create a Room in our Building
* create a Rack in our Room
* create a Device
* add macAddress and ipAddress for the Device
* create a switch
* create a patch panel
* connect switch and panel and device

::

    >>> import device42api
    >>> api             = device42api.Device42API(host='localhost', username='admin', password='changeme')
    >>> size            = 2
    >>> # create Hardware for device
    >>> hw              = device42api.Hardware(api=api)
    >>> hw.name         = 'Generic Hardware %sU' % size
    >>> hw.type         = 1
    >>> hw.size         = size
    >>> hw.depth        = 1
    >>> hw.manufacturer = 'Test'
    >>> hw.save()
    {'msg': ['hardware model added or updated', 1, 'Generic Hardware 2U', True, True], 'code': 0}
    >>> # create Building
    >>> b               = device42api.Building(api=api)
    >>> b.name          = 'Test Building'
    >>> b.address       = 'somewhere in the city'
    >>> b.notes         = 'destruction ongoing, leave the building immediatley'
    >>> b.save()
    {'msg': ['Building added/updated successfully', 1, 'Test Building', True, True], 'code': 0}  
    >>> # create a Room in our Building
    >>> room                = device42api.Room(api=api)
    >>> room.name           = 'Test Room'
    >>> room.building       = b.name
    >>> room.building_id    = b.building_id
    >>> room.notes          = 'coffee corner for sysadmins'
    >>> room.save()
    {'msg': ['Room added/updated successfully', 1, 'Test Room', True, True], 'code': 0}
    >>> # create a Rack in our Room
    >>> rack            = device42api.Rack(api=api)
    >>> rack.name       = 'Test Rack'
    >>> rack.size       = 42
    >>> rack.room       = room.name
    >>> rack.building   = room.building
    >>> rack.room_id    = room.room_id
    >>> rack.numbering_start_from_botton = 'no'
    >>> rack.notes         = 'First Rack'
    >>> rack.save()
    {'msg': ['rack added/updated.', 1, 'Test Rack', True, True], 'code': 0}    
    >>> # create a Device
    >>> device                  = device42api.Device(api=api)
    >>> device.name             = 'Test Device'    
    >>> device.serial_no        = '0123456789'
    >>> device.hardware         = 'Generic Hardware 2U'
    >>> device.in_service       = 'yes'
    >>> device.type             = 'physical'
    >>> device.service_level    = 'production'
    >>> device.os               = 'RHEL Server'
    >>> device.osver            = 6.5
    >>> device.memory           = 16.000
    >>> device.cpucount         = 80
    >>> device.cpucore          = 8
    >>> device.notes            = 'Test Device'
    >>> device.save()
    {'msg': ['device added or updated', 1, 'Test Device', True, True], 'code': 0}
    >>> # add macAddress and ipAddress for the Device
    >>> for mA, iA, dN in (('00:11:22:33:44:55', '1.1.1.1', 'eth0'),
    ...                    ('00:11:22:33:44:66', '1.1.1.2', 'eth1')):
    ...     device.add_mac(macAddress=mA, port_name=dN)
    ...     device.add_ip(ipAddress=iA, macAddress=mA)
    True
    True
    True
    True  
    >>> # validate mac and ip addresses
    >>> for m in device.mac_addresses:      print m, m.macaddress, m.mac_id
    ...
    <device42api.IPAM_macaddress object at 0x2272ad0> 00:11:22:33:44:55 1
    <device42api.IPAM_macaddress object at 0x22728d0> 00:11:22:33:44:66 2
    >>> for i in device.ip_addresses:       print i, i.ipaddress, i.ip_id
    ...
    <device42api.IPAM_ipaddress object at 0x2272950> 1.1.1.1 1
    <device42api.IPAM_ipaddress object at 0x22772d0> 1.1.1.2 2 
    >>> rack.add_device(device, start_at=1)
    {'msg': ['device added or updated in the rack', 1, '[1.0] - Test Rack -Test Room'], 'code': 0}
    >>> # create a switch
    >>> switch                  = device42api.Device(api=api)
    >>> switch.name             = 'switch1'    
    >>> switch.serial_no        = '9876543210'
    >>> switch.hardware         = 'Generic Hardware 2U'
    >>> switch.in_service       = 'yes'
    >>> switch.type             = 'physical'
    >>> switch.service_level    = 'production'
    >>> switch.is_it_switch     = 'yes'
    >>> switch.save()
    {'msg': ['device added or updated', 2, 'switch1', True, True], 'code': 0}  
    >>> # since Hardware isn't fetch able in the API you need to remember the Hardware size if you want to start from top down
    >>> rack.add_device(switch, start_at=rack.size - size)
    {'msg': ['device added or updated in the rack', 1, '[40.0] - Test Rack -Test Room'], 'code': 0}

