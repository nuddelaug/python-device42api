#!/usr/bin/python

import httplib2 
import base64
import simplejson as json
from urllib import urlencode

class Required(object): pass
class Optional(object): pass

class Device42APIObjectException(Exception):    pass

class Device42APIObject(object):
    """basic Object representing a device42 API object """
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

class CustomField(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        super(CustomField, self).__init__(json, parent, api)
    
class Building(Device42APIObject):
    """create Building object
    
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
        self.json['name'] = str(self.name)
        for k in ('address', 'contact_name', 'contact_phone', 'notes'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
            elif not self._json.has_key(k):
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if isinstance(v, Optional):  continue
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class Room(Device42APIObject):
    """create Room object
    
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
        self.json['name'] = str(self.name)
        if not isinstance(self.building, Required):     self.json['building']       = str(self.building)
        if not isinstance(self.building_id, Required):  self.json['building_id']    = self.building_id
        for k in ('notes', ):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
            elif not self._json.has_key(k):
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if isinstance(v, Optional):  continue
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class Rack(Device42APIObject):
    """create Rack object
    
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
        body = dict(device=device.name, rack_id=self.rack_id, start_at=start_at)
        return self.api.__post_api__('device/rack', body=body)
    def save(self):
        if self.api != None:
            return self.api.__post_api__('racks/', body=self.get_json())
    def get_json(self):
        for attr in ('name', 'size', 'room'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException(u'required Attribute "%s" not set' % attr)
            self.json[attr] = str(getattr(self, attr))
        for k in ('building', 'room_id', 'numbering_start_from_bottom', 'first_number',
                  'row', 'manufacturer', 'notes'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
            elif not self._json.has_key(k):
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if isinstance(v, Optional):  continue
                if self._json[k] != v:
                    self.json[k] = str(v)
                else:
                    self.json[k] = str(v)
            except AttributeError:  continue
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
        self.patch_paneld_model_id  = Optional()
        self.numbering_start_from   = Optional()
        self.asset_contracts= []
        self.asset_purchases= []
        super(Asset, self).__init__(json['asset'], parent, api)
        self._json          = json
    def save(self):
        if self.api != None:
            return self.api.__post_api__('assets/', self.get_json())

class Device(Device42APIObject):
    """create Device object
    
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
                        self.ip_addresses.append(IPAM_ipaddress(json=i, parent=self, api=self.api))
                elif k == 'mac_addresses':
                    for m in json['mac_addresses']:
                        # cannot fetch single MAC Address without id, so only put object with macaddress attribute
                        mac = IPAM_macaddress(parent=self, api=self.api)
                        mac.macaddress = m['mac']
                        self.mac_addresses.append(mac)
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
        self.json['name'] = str(self.name)
        for k in ('serial_no', 'asset_no', 'manufacturer', 'hardware', 'type', 'service_level', 'virtual_host', 'blade_host', 'slot_no',
                  'storage_room_id', 'storage_room', 'os', 'osver', 'memory', 'cpucount', 'cpupower', 'cpucore',
                  'hddcount', 'hddsize', 'hddraid', 'hddraid_type', 'devices_in_cluster', 'appcomps',
                  'customer', 'contract', 'aliases', 'notes'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
            elif not self._json.has_key(k):
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if isinstance(v, Optional):  continue
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json
    def __str__(self):
        return u'%s' % self.name

class Hardware(Device42APIObject):
    """create Hardware object
    
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
        self.json['name'] = str(self.name)
        for k in ('type', 'size', 'depth', 'blade_size', 'part_no', 'watts', 'spec_url', 'manufacturer', 'front_image_id',
                  'back_image_id', 'notes'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
            elif not self._json.has_key(k):
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if isinstance(v, Optional):  continue
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class PDU(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        self.name           = Required()
        self.pdu_id         = Optional()
        self.rack_id        = Optional()
        self.device         = Optional()
        self.notes          = Optional()
        self.where          = Optional() # values: left, right, above, below or mounted.
        self.start_at       = Optional()
        self.orientation    = Optional()
        super(PDU, self).__init__(json, parent, api)
    def save(self):
        if self.api != None:
            if self.rack_id != Optional():
                return self.api.__post_api__('pdus/rack/', self.get_json())
            return self.api.__post_api__('pdus/', self.get_json())

class PatchPanel(Device42APIObject):
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

class IPAM_macaddress(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        super(IPAM_macaddress, self).__init__(json, parent, api)
        self.macaddress         = Required()
        self.port_name 	        = Optional() # Interface name.
        self.override 	        = False # Value can be smart, no, or yes. See notice below.
        self.vlan_id 	        = Optional() # GET VLAN IDs or UI Tools > Export > VLAN
        self.device 	        = Optional()
    def save(self):
        if self.api != None:
            return self.api.__post_api__('macs/', body=self.get_json())
    def get_json(self):
        if isinstance(self.macaddress, Required):
            raise Device42APIObjectException(u'required Attribute "macaddress" not set')
        self.json['macaddress'] = str(self.macaddress)
        for k in ('port_name', 'vlan_id', 'device'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class IPAM_ipaddress(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        super(IPAM_ipaddress, self).__init__(json, parent, api)
        if json != None and self.__dict__.get('ip', False):
            self.ipaddress  = self.ip
        else:
            self.ipaddress 	    = Required() 
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
    def save(self):
        if self.api != None:
            return self.api.__post_api__('ip/', v=None, body=self.get_json())
    def get_json(self):
        if isinstance(self.ipaddress, Required):
            raise Device42APIObjectException(u'required Attribute "ipaddress" not set')
        self.json['ipaddress'] = str(self.ipaddress)
        for k in ('tag', 'subnet', 'macaddress', 'device', 'type'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class IPAM_subnet(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        super(IPAM_subnet, self).__init__(json, parent, api)
        self.network 	    = Required() 
        self.mask_bits 	    = Optional() 
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
    def save(self):
        if self.api != None:
            return self.api.__post_api__('ip/', body=self.get_json())
    def get_json(self):
        if isinstance(self.network, Required):
            raise Device42APIObjectException(u'required Attribute "network" not set')
        self.json['network'] = str(self.network)
        for k in ('mask_bits', 'vrf_group_id', 'name', 'description', 'number', 'gateway',
                  'range_begin', 'range_end', 'parent_vlan_id', 'customer_id', 'customer'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class IPAM_vlan(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        super(IPAM_vlan, self).__init__(json, parent, api)
        self.number         = Required()
        self.name           = Optional()
        self.description    = Optional()
        self.switch_id      = Optional()
        self.switches       = Optional()
        self.notes          = Optional()
    def save(self):
        if self.api != None:
            return self.api.__post_api__('vlans/', body=self.get_json())
    def get_json(self):
        if isinstance(self.number, Required):
            raise Device42APIObjectException(u'required Attribute "number" not set')
        self.json['number'] = str(self.number)
        for k in ('name', 'description', 'switch_id', 'switches', 'notes'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class IPAM_switchport(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        super(IPAM_switchport, self).__init__(json, parent, api)
        self.port           = Required()
        self.switch         = Optional()
        self.description    = Optional()
        self.type           = Optional()
        self.vlan_ids       = Optional() # Comma separated vlan ids on that port
        self.up             = Optional()
        self.up_admin       = Optional()
        self.count          = Optional()
        self.remote_port_id = Optional()
        self.remote_device  = Optional()
        self.remote_port    = Optional()
        self.notes          = Optional()
    def save(self):
        if self.api != None:
            return self.api.__post_api__('vlans/', body=self.get_json())
    def get_json(self):
        if isinstance(self.port, Required):
            raise Device42APIObjectException(u'required Attribute "port" not set')
        self.json['port'] = str(self.port)
        for k in ('name', 'description', 'switch_id', 'switches', 'notes'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class IPAM_switch(Device42APIObject):
    def __init__(self, json=None, parent=None, api=None):
        super(IPAM_switch, self).__init__(json, parent, api)
        self.device         = Required()
        self.device_id      = Optional()
        self.switch_template_id = Required()
        self.notes          = Optional()
    def save(self):
        if self.api != None:
            return self.api.__post_api__('vlans/', body=self.get_json())
    def get_json(self):
        for attr in ('device', 'switch_template_id'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException(u'required Attribute "%s" not set' % getattr(self, attr))
        self.json['device'] = str(self.device)
        self.json['switch_template_id'] = self.switch_template_id
        for k in ('device_id', 'notes'):
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if self._json.has_key(k) and self._json[k] != v:
                self.json[k] = str(v)
        for k in self._json.keys():
            try:
                v = getattr(self, k)
                if self._json[k] != v:
                    self.json[k] = str(v)
            except AttributeError:  continue
        return self.json

class Device42API(object):
    def __init__(self, host=None, port=443, username=None, password=None):
        self.host       = host
        self.port       = int(port)
        self.username   = username
        self.password   = password
        self._http      = httplib2.Http(disable_ssl_certificate_validation=True)
        self._auth      = base64.encodestring('%s:%s' % (self.username, self.password))
        self._headers   = {'Accept':'application/json',
                           'Authorization': 'Basic %s' % self._auth}
    def __get_api__(self, path=None):
        if path == None:    return False
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
    def get_racks(self):
        racks = []
        for r in self.__get_api__('racks/')['racks']:
            rc = self.__get_api__('racks/%s/' % r['rack_id'])
            racks.append(Rack(json=rc, api=self))
        return racks

