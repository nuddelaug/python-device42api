#!/usr/bin/python

import httplib2 
import base64
import simplejson as json
from urllib import urlencode

class Required(object): pass
class Optional(object): pass

class Device42APIObjectException(Exception):    pass

class Device42APIObject(object):
    """.. _Device42APIObject:
    
    basic Object representing a device42 API object,
    inherit from this one and implement at least:
    
    * save()
    * load()
    * get_json()
    
    """
    def __init__(self, json=None, parent=None, api=None):
        self.api            = api
        self._json          = json
        self.json           = dict()
        self.parent         = parent
        self.custom_fields  = []
        if self._json != None:
            for k in self._json.keys():
                if k == 'custom_fields':
                    for c in self._json[k]:
                        self.custom_fields.append(CustomField(json=c, parent=self))
                setattr(self, k, self._json[k])
        else:
            self._json = dict()
    def save(self):
        raise Device42APIObjectException(u'need to implement save')
    def get_json(self):
        raise Device42APIObjectException(u'need to implement get_json')
    def load(self):
        raise Device42APIObjectException(u'need to implement load')
    def __get_json_validator__(self, keys=[]):
        for k in keys:
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                if not isinstance(v, int):
                    self.json[k] = str(v)
                else:
                    self.json[k] = v
            elif not self._json.has_key(k):
                if not isinstance(v, int):
                    self.json[k] = str(v)
                else:
                    self.json[k] = v
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if isinstance(v, Optional):  continue
                if self._json[k] != v:
                    if not isinstance(v, int):
                        self.json[k] = str(v)
                    else:
                        self.json[k] = v
            except AttributeError:  continue

class CustomField(Device42APIObject):
    """.. _CustomField:
    
    create CustomField
    postponed due to licensing issues
    """
    def __init__(self, json=None, parent=None, api=None):
        super(CustomField, self).__init__(json, parent, api)
    
class Building(Device42APIObject):
    """.. _Building:
    
    create Building object
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> b = device42api.Building(api=api)
    >>> b.name    = 'Test Building'
    >>> b.address = 'somewhere in the city'
    >>> b.notes   = 'destruction ongoing, leave the building immediatley'
    >>> b.save()
    {'msg': ['Building added/updated successfully', 3, 'TestBuilding', True, True], 'code': 0}

    """
    def __init__(self, json=None, parent=None, api=None):
        self.name           = Required()
        self.address        = Optional()
        self.contact_name   = Optional()
        self.contact_phone  = Optional()
        self.notes          = Optional()
        super(Building, self).__init__(json, parent, api)
    def __str__(self):
        return u'%s %s' % (self.name, self.address)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('buildings/', body=self.get_json())
    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException(u'required Attribute "name" not set')
        self.__get_json_validator__(('name', 'address', 'contact_name', 'contact_phone', 'notes'))
        return self.json

class Room(Device42APIObject):
    """.. _Room:
    
    create Room object
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> r = device42api.Room(api=api)
    >>> r.name      = 'Test Room'
    >>> r.building  = 'Test Building'
    >>> r.building_id = 3
    >>> r.notes     = 'coffee corner for sysadmins'
    >>> r.save()
    {'msg': ['Room added/updated successfully', 2, 'Test Room', True, True], 'code': 0}

    """
    def __init__(self, json=None, parent=None, api=None):
        self.name           = Required()
        self.building_id    = Required()
        self.building       = Required()
        self.notes          = Optional()
        self.assets         = []
        self.devices        = []
        self.racks          = []
        super(Room, self).__init__(json, parent, api)
    def __str__(self):
        return u'%s %s' % (self.name)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('rooms/', body=self.get_json())
    def load(self):
        """get entries for room from API
        
        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> r = device42api.Room(api=api)
        >>> r.room_id = 2
        >>> r.load()
        >>> r.notes
        'coffee corner for sysadmins'
        >>> r.building
        'TestBuilding'

        """
        if self.api != None:
            json = self.api.__get_api__('rooms/%s' % self.room_id)
            for k in json.keys():
                if k == 'devices':
                    for d in json[k]:
                        d = Device(json=d, parent=self, api=self.api)
                        d.load()
                        self.devices.append(d)
                elif k == 'racks':
                    for r in json[k]:
                        r = Rack(json=r, parent=self, api=self.api)
                        r.load()
                        self.racks.append(r)
                elif k == 'assets':
                    for a in json[k]:
                        a = Asset(json=a, parent=self, api=self.api)
                        a.load()
                        self.assets.append(a)
                else:
                    if json[k] != None:
                        setattr(self, k, json[k])
            self._json = json
    def get_json(self):
        for attr in ('name', 'building_id', 'building'):
            if isinstance(getattr(self, attr), Required):
                if attr == 'building_id' and isinstance(self.building, Required):
                    raise Device42APIObjectException(u'required Attribute "building_id" or Attribute "building" not set')
                elif attr == 'building' and isinstance(self.building_id, Required):
                    raise Device42APIObjectException(u'required Attribute "building_id" or Attribute "building" not set')
                elif attr == 'name':
                    raise Device42APIObjectException(u'required Attribute "name" not set')
        self.__get_json_validator__(('name', 'building', 'building_id', 'notes'))

class Rack(Device42APIObject):
    """.. _Rack:
    
    create Rack object
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> r = device42api.Rack(api=api)
    >>> r.name = 'TestRack1'
    >>> r.size = 42
    >>> r.room = 'Test Room'
    >>> r.building = 'TestBuilding'
    >>> r.room_id = 2
    >>> r.numbering_start_from_botton = 'no'
    >>> r.notes = 'my personal rack'
    >>> r.save()
    {'msg': ['rack added/updated.', 80, 'TestRack1', True, True], 'code': 0}

    """
    def __init__(self, json=None, parent=None, api=None):
        self.name           = Required()
        self.size           = Required()
        self.room           = Required()
        self.building       = Optional()
        self.room_id        = Optional()
        self.numbering_start_from_bottom = Optional()
        self.first_number   = Optional()
        self.row            = Optional()
        self.manufacturer   = Optional()
        self.notes          = Optional()
        self.assets         = {}
        self.devices        = {}
        if json != None and json.has_key('rack'):
            super(Rack, self).__init__(json['rack'], parent, api)
        else:
            super(Rack, self).__init__(json, parent, api)
        if self.assets != {}:
            assets  = {}
            for a in self.assets:
                aa  = assets.get(a['start_at'], False)
                if not aa:
                    aa  = Asset(json=a, parent=self, api=self.api)
                assets[a['start_at']]   = aa
            self.assets = assets
        if self.devices != {}:
            devices = {}
            for d in self.devices:
                dd = devices.get(d['start_at'], False)
                if not dd:
                    dd = Device(json=d, parent=self, api=self.api)
                devices[d['start_at']]  = dd
            self.devices = devices
    def __str__(self):
        return u'%s' % self.name
    def get_assets(self):
        order   = self.assets.keys()
        if self.numbering_start_from_bottom == 'no':
            order.sort()
        else:
            order.reverse()
        for k in order:
            yield self.assets[k]
    def get_devices(self):
        order   = self.devices.keys()
        if self.numbering_start_from_bottom == 'no':
            order.sort()
        else:
            order.reverse()
        for k in order:
            yield self.devices[k]
    def add_device(self, device=None, start_at='auto'):
        """.. _Rack.add_device:
        
        add's a device to the rack starting at given position "start_at=xxx" or auto for next possible free slot
        
        >>> # if created you need to set the rack_id first
        >>> hw  = device42api.Hardware(api=api)
        >>> hw.name, hw.type, hw.size, hw.depth = 'Generic Hardware 1U', 1, 1, 1
        >>> h.save()
        >>> dev = device42api.Device(api=api)
        >>> dev.name = 'Test Device'
        >>> dev.hardware = 'Generic Hardware 1U'
        >>> dev.save()
        >>> r.rack_id = 80
        >>> r.add_device(dev, start_at=1)
        {'msg': ['device added or updated in the rack', 1, '[1.0] - TestRack1 -Test Room'], 'code': 0}
        
        """
        body = dict(device=device.name, rack_id=self.rack_id, start_at=start_at)
        return self.api.__post_api__('device/rack', body=body)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('racks/', body=self.get_json())
    def get_json(self):
        for attr in ('name', 'size', 'room'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException(u'required Attribute "%s" not set' % attr)
        self.__get_json_validator__(('name', 'size', 'room', 'building', 'room_id', 'numbering_start_from_bottom', 'first_number',
                  'row', 'manufacturer', 'notes'))
        return self.json
    def load(self):
        """get entries for rack from API
        
        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> r = device42api.Rack(api=api)
        >>> r.rack_id = 80
        >>> r.load()
        >>> r.name, r.notes
        ('TestRack1', 'my personal rack')
        >>> r.devices
        {32.0: <device42api.Device object at 0x991cd0>, 36.0: <device42api.Device object at 0x991b50>, 6.0: <device42api.Device object at 0x9097d0>, 40.0: <device42api.Device object at 0x994d50>, 45.0: <device42api.Device object at 0x994f10>, 28.0: <device42api.Device object at 0x991b10>}
        
        """
        if self.api != None:
            json = self.api.__get_api__('racks/%s' % self.rack_id)
            for k in json.keys():
                if k == 'devices':
                    for d in json[k]:
                        start_at = d['start_at']
                        d = Device(json=d, parent=self, api=self.api)
                        d.load()
                        self.devices[start_at] = d
                elif k == 'assets':
                    for a in json[k]:
                        start_at = a['start_at']
                        a = Asset(json=a, parent=self, api=self.api)
                        a.load()
                        self.assets[start_at] = a
                else:
                    if json[k] != None:
                        setattr(self, k, json[k])
            self._json = json

class Asset(Device42APIObject):
    """.. _Asset:
    
    create Rack object
    postponed due to licensing issues
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> a = device42api.Asset(api=api)
    >>> a.type = 'AC' # AC,Breaker Panel,Cable Modem,DMARC,Fabric Extender,Fax Machine,Filler Panel,Monitor,Patch Panel
                      # Patch Panel Module,Projector,Scanner,Shredder,Software,Speaker Phone,TAP Module
    >>> a.serial_no = '1234567890'
    >>> a.vendor = 'Test'
    >>> a.building = 'TestBuilding'
    >>> a.room = 'Test Room'
    >>> a.rack_id = 80
    >>> a.start_at = 1
    >>> a.save()
    {'msg': ['asset added/edited.', 1, ''], 'code': 0}

    """
    def __init__(self, json=None, parent=None, api=None):
        self.type           = Required()
        self.name           = Optional()
        self.service_level  = Optional()
        self.serial_no      = Optional()
        self.asset_no       = Optional()
        self.customer_id    = Optional()
        self.location       = Optional()
        self.notes          = Optional()
        self.building       = Optional()
        self.vendor         = Optional()
        self.imagefile_id   = Optional()
        self.contract_id    = Optional()
        self.rack_id        = Optional()
        self.building       = Optional()
        self.room           = Optional()
        self.rack           = Optional()
        self.row            = Optional()
        self.start_at       = Optional()
        self.size           = Optional()
        self.orientation    = Optional()
        self.depth          = Optional()
        self.patch_panel_model_id   = Optional()
        self.numbering_start_from   = Optional()
        self.asset_contracts= []
        self.asset_purchases= []
        if json != None and json.has_key('asset'):
            super(Asset, self).__init__(json['asset'], parent, api)
        else:
            super(Asset, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('assets/', body=self.get_json())
    def get_json(self):
        if isinstance(self.type, Required):
            raise Device42APIObjectException(u'required Attribute "type" not set')
        self.__get_json_validator__(('type', 'name', 'service_level', 'serial_no', 'asset_no', 'customer_id', 'location',
                  'notes', 'building', 'vendor', 'imagefile_id', 'contract_id', 'rack_id',
                  'building', 'room', 'rack', 'row', 'start_at', 'size', 'orientation',
                  'depth', 'patch_panel_model_id', 'numbering_start_from'))
        return self.json
    def load(self):
        """get entries for asset from API
        
        """
        if self.api != None:
            json = self.api.__get_api__('assets/%s' % self.asset_id)
            for k in json.keys():
                if json[k] != None:
                    setattr(self, k, json[k])
            self._json = json


class Device(Device42APIObject):
    """.. _Device:
    
    create Device object
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> d = device42api.Device(api=api)
    >>> d.name = 'TestDevice'
    >>> d.serial_no = 'Ab123asd' # serial number must follow certain structure ???
    >>> d.hardware = 'Generic Hardware 1U'
    >>> d.in_service = 'yes'
    >>> d.type = 'physical'
    >>> d.service_level = 'production'
    >>> d.os = 'RHEL Server'
    >>> d.osver = 6.5
    >>> d.memory = 16.000
    >>> d.cpucount = 80
    >>> d.cpucore = 8
    >>> d.notes = 'my special device'
    >>> d.save()
    {'msg': ['device added or updated', 156, 'TestDevice', True, True], 'code': 0}

    """
    def __init__(self, json=None, parent=None, api=None):
        self.name                   = Required()
        self.serial_no              = Optional()
        self.asset_no               = Optional()
        self.manufacturer           = Optional()
        self.hardware               = Optional()
        self.is_it_switch           = False
        self.is_it_virtual_host     = False
        self.is_it_blade_host       = False
        self.in_service             = False
        self.type                   = Optional() # values are physical, virtual, blade, cluster, or other
        self.service_level          = Optional()
        self.virtual_host           = Optional()
        self.blade_host             = Optional()
        self.slot_no                = Optional()
        self.storage_room_id        = Optional()
        self.storage_room           = Optional()
        self.os                     = Optional()
        self.osver                  = Optional()
        self.memory                 = Optional()
        self.cpucount               = Optional()
        self.cpupower               = Optional()
        self.cpucore                = Optional()
        self.hddcount               = Optional()
        self.hddsize                = Optional()
        self.hddraid                = Optional()
        self.hddraid_type           = Optional()
        self.mac_addresses          = []
        self.ip_addresses           = []
        self.devices_in_cluster     = Optional()
        self.appcomps               = Optional()
        self.customer               = Optional()
        self.contract               = Optional()
        self.aliases                = Optional()
        self.notes                  = Optional()
        if json != None:
            super(Device, self).__init__(json['device'], parent, api)
            self._json              = json
        else:
            super(Device, self).__init__(json, parent, api)
            self._json              = dict()
    def save(self):
        if self.api != None:
            return self.api.__post_api__('device/', v=None, body=self.get_json())
    def load(self):
        """
        
        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> d = device42api.Device(api=api)
        >>> d.device_id = 156
        >>> d.load()
        >>> d.name, d.serial_no
        ('TestDevice', 'Ab123asd')
        
        """
        if self.api != None:
            json = self.api.__get_api__('devices/id/%s/' % self.device_id)
            for k in json.keys():
                if k == 'ip_addresses':
                    for i in json['ip_addresses']:
                        ip = IPAM_ipaddress(json=i, parent=self, api=self.api)
                        ip.load()
                        self.ip_addresses.append(ip)
                elif k == 'mac_addresses':
                    for m in json['mac_addresses']:
                        self.mac_addresses.append(self.api.get_macid_byAddress(m['mac']))
                elif k == 'hw_model':
                    setattr(self, 'hardware', json[k])
                    # hack as hardware is returned as hw_model
                    json['hardware'] = json[k]
                else:
                    if json[k] != None:
                        setattr(self, k, json[k])
            self._json = json
    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException(u'required Attribute "name" not set')
        self.__get_json_validator__(('name', 'serial_no', 'asset_no', 'manufacturer', 'hardware', 'type', 'service_level', 'virtual_host', 'blade_host', 'slot_no',
                  'storage_room_id', 'storage_room', 'os', 'osver', 'memory', 'cpucount', 'cpupower', 'cpucore',
                  'hddcount', 'hddsize', 'hddraid', 'hddraid_type', 'devices_in_cluster', 'appcomps',
                  'customer', 'contract', 'aliases', 'notes'))
        return self.json
    def add_mac(self, macAddress=None, port_name=None):
        """.. _Device.add_mac:
        
        adds a macAddress to the device (if new macAddress will be created)
        
        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> d = device42api.Device(api=api)
        >>> d.device_id = 1
        >>> d.load()
        >>> d.add_mac('00:00:00:00:00:02', 'eth1')
        {'msg': ['mac address successfully added/updated', 2, '00:00:00:00:00:02', True, True], 'code': 0}
        
        """
        mc = IPAM_macaddress(api=self.api)
        mc.macaddress = macAddress
        if port_name != None:
            mc.port_name = port_name
        mc.device = self
        rsp = mc.save()
        if rsp['msg'][-2] == True:
            self.mac_addresses.append(mc)
            return True
        return rsp
    def add_ip(self, ipAddress=None, macAddress=None):
        """.. _Device.add_ip:
        
        adds an ipAddress to the device
        
        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> racks = api.get_racks()
        >>> racks[0].devices.keys()
        [1.0]
        >>> d = racks[0].devices[1.0]
        >>> len(d.mac_addresses)
        1
        >>> d.add_ip('2.2.2.2') # if macAddress is ommited and only one macAddress is in device this one will be used
        {'msg': ['mac address successfully added/updated', 2, '00:00:00:00:00:02', True, True], 'code': 0}
        >>> for ip in d.ip_addresses:
        ...     print ip.ipaddress
        1.1.1.1
        2.2.2.2
        
        """
        ip  = IPAM_ipaddress(api=self.api)
        ip.ipaddress    = ipAddress
        if macAddress != None:
            ip.macaddress = macAddress
        elif len(self.mac_addresses) == 1:
            ip.macaddress = self.mac_addresses[0].macaddress
        ip.device = self.name
        ip.type = 'static'
        rsp = ip.save()
        if rsp['msg'][-2] == True:
            self.ip_addresses.append(ip)
            return True
        return rsp
    def __str__(self):
        return u'%s' % self.name

class Hardware(Device42APIObject):
    """.. _Hardware:
    
    create Hardware object
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> h = device42api.Hardware(api=api)
    >>> h.name = 'TestHardware'
    >>> h.type = 1  # 1=Regular,2=Blade,3=Other
    >>> h.size = 1  
    >>> h.depth = 1 # 1=Full,2=Half
    >>> h.notes = 'my test hardware'
    >>> h.save()
    {'msg': ['hardware model added or updated', 25, 'TestHardware', True, True], 'code': 0}
    
    """
    def __init__(self, json=None, parent=None, api=None):
        self.name           = Required()
        self.type           = Optional() # 1=Regular,2=Blade,3=Other
        self.size           = Optional()
        self.depth          = Optional() # 2 = Half depth or empty, 1 = Full depth
        self.blade_size     = Optional() # 1=Full Height,2=Half Height,3=Double Half Height,4=Double Full Height
        self.part_no        = Optional()
        self.watts          = Optional()
        self.spec_url       = Optional()
        self.manufacturer   = Optional()
        self.front_image_id = Optional()
        self.back_image_id  = Optional()
        self.notes          = Optional()
        super(Hardware, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('hardwares/', body=self.get_json())
    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException(u'required Attribute "name" not set')
        self.__get_json_validator__(('name', 'type', 'size', 'depth', 'blade_size', 'part_no', 'watts', 'spec_url', 'manufacturer', 'front_image_id',
                  'back_image_id', 'notes'))
        return self.json

class PDU_Model(Device42APIObject):
    """.. _PDU:
    
    only representing the PDU Models as object
    !!! since there's no API call to create/update these can only be retrieved !!!
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> models = api.get_pdu_models()
    >>> for m in models:
    ...     print m
    pdu_model 1 ports 8 type NEMA 5-15R

    """
    def __init__(self, json=None, parent=None, api=None):
        super(PDU_Model, self).__init__(json, parent, api)
        self.ports  = getattr(self, 'ports in pdu model')
    def __str__(self):
        pdu_port_count, pdu_port_type = 0, []
        for p in self.ports:
            pdu_port_count += p['pdu_port_count']
            pdu_port_type.append(p['pdu_port_type'])
        return u'pdu_model %s ports %s type %s' % (self.pdu_model_id, pdu_port_count, ','.join(pdu_port_type))

class PDU(Device42APIObject):
    """.. _PDU:
    
    create Rack object
    postponed due to licensing issues
    
    !!! the PDU Model needs to exist an unfortunatley there's no API call to create it !!!
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> pdu_models = api.get_pdu_models()
    >>> p = device42api.PDU(api=api)
    >>> p.name = 'Test PDU'
    >>> p.pdu_id = 1
    >>> p.rack_id = 80
    >>> p.device = 156
    >>> p.notes = 'Test PDU Test Device'
    >>> p.where = 'left'
    >>> p.start_at = 1
    >>> p.save()
    {'msg': '{\'pdu\': [u"Model PDU with pk u\'1\' does not exist."]}', 'code': 1}

    !!! that might be an API bug ? updating after adding it in the GUI works 
    >>> p.save()
    {'msg': ['PDU Rack Info successfully added/edited.', 1, 'PDU Test'], 'code': 0}
    >>> r = api.get_racks()
    >>> r[0].pdus
    [{'start_at': 1.0, 'name': 'PDU Test', 'orientation': 'Front', 'pdu_id': 1, 'depth': 'Full Depth', 'where': 'Left', 'size': 1.0}]
    
    """
    def __init__(self, json=None, parent=None, api=None):
        self.name           = Required()
        self.pdu_id         = Optional()
        self.rack_id        = Optional()
        self.device         = Optional()
        self.notes          = Optional()
        self.where          = Optional() # values: left, right, above, below or mounted.
        self.start_at       = Optional()
        self.orientation    = Optional()
        if json != None and json.has_key('pdu'):
            super(PDU, self).__init__(json['pdu'], parent, api)
        else:
            super(PDU, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            if self.rack_id != Optional():
                return self.api.__post_api__('pdus/rack/', body=self.get_json())
            return self.api.__post_api__('pdus/', body=self.get_json())
    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException(u'required Attribute "name" not set')
        self.__get_json_validator__(('name', 'pdu_id', 'rack_id', 'device', 'notes', 'where', 'start_at', 'orientation'))
        return self.json

class PatchPanel(Device42APIObject):
    """.. _PatchPanel:
    
    create PatchPanel
    postponed due to licensing issues
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> cp = device42api.PatchPanel(api=api)
    >>> p = api.get_patch_panels()[0]
    >>> mac = api.get_macid_byAddress('00:00:00:00:00:01')
    >>> cp.patch_panel_id = p.asset_id
    >>> cp.number = 1
    >>> cp.mac_id = mac.address_id
    >>> cp.get_json()
    {'patch_panel_id': 2, 'mac_id': 1, 'number': 1}
    >>> cp.save()
    {'msg': ['patch port details edited successfully.', 1, 'Test Panel : 1'], 'code': 0}
    
    """
    def __init__(self, json=None, parent=None, api=None):
        self.patch_panel_id         = Required()
        self.number                 = Required()
        self.mac_id                 = Required()
        self.device_id              = Required()
        self.device                 = Required()
        self.switchport_id          = Optional()
        self.switch                 = Optional()
        self.switchport             = Optional()
        self.patch_panel_port_id    = Optional()
        self.label                  = Optional()
        self.obj_label1             = Optional()
        self.obj_label2             = Optional()
        self.back_connection_id     = Optional()
        self.back_switchport_id     = Optional()
        self.back_switch            = Optional()
        self.back_switchport        = Optional()
        self.cable_type             = Optional()
        super(PatchPanel, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('patch_panel_ports/', body=self.get_json())
    def get_json(self):
        for attr in ('patch_panel_id', 'number'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException(u'required Attribute "%s" not set' % attr)
        if isinstance(self.mac_id, Required) and \
            (isinstance(self.device_id, Required) or isinstance(self.device), Required):
            raise Device42APIObjectException(u'required Attribute mac_id or device_id or device')
        elif not isinstance(self.mac_id, Required):
            if isinstance(self.device_id, Required):    self.device_id = Optional()
            if isinstance(self.device, Required):       self.device    = Optional()
        if not isinstance(self.device, Required) or not isinstance(self.device_id, Required):
            if isinstance(self.mac_id, Required):       self.mac_id     = Optional()
            for attr in ('device', 'device_id'):
                if isinstance(getattr(self, attr), Optional):   continue
        self.__get_json_validator__(('patch_panel_id', 'number', 'mac_id', 'device', 'device_id', 'switchport_id', 'switch', 'switchport', 'patch_panel_port_id', 'label',
                  'obj_label1', 'obj_label2', 'back_connection_id', 'back_switchport_id',
                  'back_switch', 'back_switchport', 'cable_type'))
        return self.json

class IPAM_macaddress(Device42APIObject):
    """.. _IPAM_macaddress:
    
    create IPAM macaddress
    these objects are returned if you fetch devices with configured macAddresses, manual adding a mac Address to a device
    as follows ...
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> i = device42api.IPAM_macaddress(api=api)
    >>> i.macaddress = '00:11:22:33:44:55'
    >>> i.port_name = 'eth0'
    >>> i.device = 'Test Device'
    >>> i.get_json()
    {'device': 'Test Device', 'macaddress': '00:11:22:33:44:55', 'port_name': 'eth0'}
    >>> i.save()
    {'msg': ['mac address successfully added/updated', 1, '00:11:22:33:44:55', True, True], 'code': 0}

    """
    def __init__(self, json=None, parent=None, api=None):
        self.macaddress         = Required()
        self.port_name 	        = Optional() # Interface name.
        self.override 	        = False # Value can be smart, no, or yes. See notice below.
        self.vlan_id 	        = Optional() # GET VLAN IDs or UI Tools > Export > VLAN
        self.device 	        = Optional()
        super(IPAM_macaddress, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('macs/', body=self.get_json())
    def get_json(self):
        if isinstance(self.macaddress, Required):
            raise Device42APIObjectException(u'required Attribute "macaddress" not set')
        self.__get_json_validator__(('macaddress', 'port_name', 'vlan_id', 'device'))
        return self.json

class IPAM_ipaddress(Device42APIObject):
    """.. _IPAM_ipaddress:
    
    create IPAM macaddress
    these objects are returned if you fetch devices with configured macAddresses, manual adding a mac Address to a device
    as follows ...
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> i = device42api.IPAM_ipaddress(api=api)
    >>> i.ipaddress = '1.1.1.1' # 127.0.0.1 is not supported and will lead to {'msg': 'list index out of range', 'code': 1}
    >>> i.macaddress = '00:11:22:33:44:55'
    >>> i.device = 'Test Device'
    >>> i.type = 'static' # static or dhcp    
    >>> i.get_json() 
    {'device': 'Test Device', 'macaddress': '00:11:22:33:44:55', 'ipaddress': '1.1.1.1', 'type': 'static'}
    >>> i.save()
    {'msg': ['ip added or updated', 1, '1.1.1.1', True, True], 'code': 0}
    
    """
    def __init__(self, json=None, parent=None, api=None): 
        self.ipaddress      = Required()
        self.tag 	    = Optional() # label for the interface
        self.subnet 	    = Optional()
        self.macaddress     = Optional() 
        self.device 	    = Optional()
        self.type 	    = Optional() # Could be static, dhcp or reserved
        self.notes 	    = Optional()
        self.vrf_group_id   = Optional() # Added in v5.1.2. ID of the VRF group you want this IP to be associated with.
        self.vrf_group 	    = Optional() # Name of the VRF group you want this IP to be associated with. Processed only if vrf_group_id is not present in the arguments.
        self.available 	    = False # If yes - then IP is marked as available and device and mac address associations are cleared. Added in v5.7.2
        self.clear_all 	    = False # If yes - then IP is marked as available and device and mac address associations are cleared. Also notes and lable fields are cleared. Added in v5.7.2
        super(IPAM_ipaddress, self).__init__(json, parent, api)
        if json != None and self.__dict__.get('ip', False):
            self.ipaddress  = self.ip
    def save(self):
        if self.api != None:
            return self.api.__post_api__('ip/', v=None, body=self.get_json())
    def get_json(self):
        if isinstance(self.ipaddress, Required):
            raise Device42APIObjectException(u'required Attribute "ipaddress" not set')
        self.__get_json_validator__(('ipaddress', 'tag', 'subnet', 'macaddress', 'device', 'type'))
        return self.json
    def load(self):
        """ there's nothing to be loaded for now"""
        return True

class IPAM_subnet(Device42APIObject):
    """.. _IPAM_subnet:
    
    create IPAM subnet
    
    >>> api = device42api.Device42API(host='192.168.122.102', username='admin', password='admin')
    >>> sub = device42api.IPAM_subnet(api=api)
    >>> sub.network = '1.1.1.0'
    >>> sub.mask_bits = 24
    >>> sub.name    = 'Home Servers'
    >>> sub.gateway = '1.1.1.254'
    >>> sub.save()
    {'msg': ['subnet successfully added/updated', 1, 'Home Servers-1.1.1.0/24'], 'code': 0}
    
    """
    def __init__(self, json=None, parent=None, api=None):
        self.network 	    = Required() 
        self.mask_bits 	    = Required() 
        self.vrf_group_id   = Optional()
        self.name           = Optional() 
        self.description    = Optional()
        self.number 	    = Optional() 
        self.gateway        = Optional()
        self.range_begin    = Optional()
        self.range_end      = Optional()
        self.parent_vlan_id = Optional()
        self.customer_id    = Optional()
        self.customer       = Optional()
        self.notes 	    = Optional()
        super(IPAM_subnet, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('subnets/', body=self.get_json())
    def get_json(self):
        for attr in ('network', 'mask_bits'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException(u'required Attribute "%s" not set' % getattr(self, attr))
        self.__get_json_validator__(('network', 'mask_bits', 'vrf_group_id', 'name', 'description', 'number', 'gateway',
                  'range_begin', 'range_end', 'parent_vlan_id', 'customer_id', 'customer'))
        return self.json

class IPAM_vlan(Device42APIObject):
    """.. _IPAM_vlan:
    
    create IPAM subnet
    >>> v = device42api.IPAM_vlan(api=api)
    >>> v.number = 1
    >>> v.name = 'Default VLAN'
    >>> v.save()
    {'msg': ['vlan successfully added', 1, 'Default VLAN', True], 'code': 0}
    
    """
    def __init__(self, json=None, parent=None, api=None):
        self.number         = Required()
        self.name           = Optional()
        self.description    = Optional()
        self.switch_id      = Optional()
        self.switches       = Optional()
        self.notes          = Optional()
        super(IPAM_vlan, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('vlans/', body=self.get_json())
    def get_json(self):
        if isinstance(self.number, Required):
            raise Device42APIObjectException(u'required Attribute "number" not set')
        self.__get_json_validator__(('number', 'name', 'description', 'switch_id', 'switches', 'notes'))
        return self.json

class IPAM_switchport(Device42APIObject):
    """.. _IPAM_switchport:
    
    create IPAM switchport
    
    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> sp = device42api.IPAM_switchport(api=api)
    >>> sp.port = 1
    >>> sp.vlan_ids = '1'
    >>> sp.description = 'Test Port'
    >>> sp.up = 'yes'
    >>> sp.up_admin = 'no'
    >>> sp.count = 'yes'
    >>> sp.save()
    {'msg': ['switchport successfully added/updated', 7, '1'], 'code': 0}
    
    !!! API Bug !!! even with the switchport_id given the API adds a new port
    
    >>> sp.get_json()
    {'switchport_id': 7, 'port': 7}
    >>> sp.save()
    {'msg': ['switchport successfully added/updated', 9, '7'], 'code': 0}
    
    """
    def __init__(self, json=None, parent=None, api=None):
        self.port           = Required()
        self.switch         = Optional()
        self.description    = Optional()
        self.type           = Optional()
        self.vlan_ids       = Optional() # only one integer item in reality API bug ?
        self.up             = Optional()
        self.up_admin       = Optional()
        self.count          = Optional()
        self.remote_port_id = Optional()
        self.remote_device  = Optional()
        self.remote_port    = Optional()
        self.notes          = Optional()
        self.switchport_id  = Optional()
        super(IPAM_switchport, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('switchports/', body=self.get_json())
    def get_json(self):
        if isinstance(self.port, Required):
            raise Device42APIObjectException(u'required Attribute "port" not set')
        self.__get_json_validator__(('port', 'switch', 'description', 'type', 'vlan_ids', 'up', 'up_admin', 'count',
                                     'remote_port_id', 'remote_device', 'remote_port', 'notes', 'switchport_id'))
        return self.json

class IPAM_switch(Device42APIObject):
    """.. _IPAM_switch:
    
    create IPAM subnet
    postponed 
    """
    def __init__(self, json=None, parent=None, api=None):
        self.device         = Required()
        self.device_id      = Optional()
        self.switch_template_id = Required()
        self.notes          = Optional()
        super(IPAM_switch, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('vlans/', body=self.get_json())
    def get_json(self):
        for attr in ('device', 'switch_template_id'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException(u'required Attribute "%s" not set' % getattr(self, attr))
        self.__get_json_validator__(('device', 'switch_template_id', 'device_id', 'notes'))
        return self.json

class Device42API(object):
    """.. _Device42API:
    
    API abstraction class
    this object deals with the https request to the device42 service
    
    >>> api = device42api.Device42API(host='192.168.122.200', username='admin', password='changeme')
    >>> for r in api.get_racks():
    ...     print r
    ...
    TestRack1
    TestRack2
    
    
    low level methods:
    * __get_api__(path='.../')  # everythin after /api/1.0/
    * __post_api__(path='.../', v='1.0', body=dict())   # v='1.0' or None
    * __put_api__(path='.../', body=dict()) # currently not used
    
    """
    def __init__(self, host=None, port=443, username=None, password=None):
        self.host       = host
        self.port       = int(port)
        self.username   = username
        self.password   = password
        self._macAddress = {}
        self._http      = httplib2.Http(disable_ssl_certificate_validation=True)
        self._auth      = base64.encodestring('%s:%s' % (self.username, self.password))
        self._headers   = {'Accept':'application/json',
                           'Authorization': 'Basic %s' % self._auth}
    def __get_api__(self, path=None):
        if path == None:    return False
        if not path.startswith('patch_panel_ports'):
            # unfortunately for this url path they API doesn't accept tailing '/'
            if not path.endswith('/'):  path += '/'
        c, r = self._http.request(u'https://%s:%s/api/1.0/%s' % (self.host, self.port, path), 'GET', headers=self._headers)
        self.__set_cookie__(c)
        return json.loads(r)
    def __post_api__(self, path=None, v='1.0', body=None):
        if path == None or body == None:    return False
        if not path.endswith('/'):  path += '/'
        self._headers['content-type'] = 'application/x-www-form-urlencoded'
        if v == '1.0':
            c, r = self._http.request(u'https://%s:%s/api/1.0/%s' % (self.host, self.port, path), 'POST', headers=self._headers, body=urlencode(body))
        else:
            c, r = self._http.request(u'https://%s:%s/api/%s' % (self.host, self.port, path), 'POST', headers=self._headers, body=urlencode(body))
        self.__set_cookie__(c)
        del self._headers['content-type']
        try:    return json.loads(r)
        except ValueError:  return r
    def __put_api__(self, path=None, body=None):
        if path == None or body == None:    return False
        if not path.endswith('/'):  path += '/'
        self._headers['content-type'] = 'application/x-www-form-urlencoded'
        c, r = self._http.request(u'https://%s:%s/api/%s' % (self.host, self.port, path), 'PUT', headers=self._headers, body=urlencode(body))
        self.__set_cookie__(c)
        del self._headers['content-type']
        try:    return json.loads(r)
        except ValueError:  return r
    def __set_cookie__(self, headers):
        if headers.has_key('set-cookie'):
            self._headers['Cookie'] = headers['set-cookie']
    def get_macid_byAddress(self, macAddress=None, reload=False):
        if self._macAddress == {} or reload == True:
            for m in self.__get_api__('macs/')['macaddresses']:
                mac = IPAM_macaddress(json=m, parent=self, api=self)
                self._macAddress[mac.macaddress] = mac
        return self._macAddress.get(macAddress, False)
    def get_pdu_models(self):
        """return all PDU models from device42"""
        pdum    = []
        for r in self.__get_api__('pdu_models/')['pdu_models']:
            pdum.append(PDU_Model(json=r, parent=self, api=self))
        return pdum
    def get_racks(self):
        """return all racks from device42"""
        racks = []
        for r in self.__get_api__('racks/')['racks']:
            rc = self.__get_api__('racks/%s/' % r['rack_id'])
            ra = Rack(json=rc, parent=self, api=self)
            ra.load()
            racks.append(ra)
        return racks
    def get_assets(self):
        """return all assets from device42"""
        assets = []
        for a in self.__get_api__('assets/')['assets']:
            assets.append(Asset(json=a, parent=self, api=self))
        return assets
    def get_patch_panels(self):
        """return all patch panels from device42, use get_assets and validate patch_panel_model_id field"""
        panels = []
        for a in self.get_assets():
            if a.type != 'Patch Panel': continue
            panels.append(a)
        return panels

