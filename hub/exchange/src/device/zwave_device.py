from .device import Device
from .parameter import Parameter
from .data_types import DataType
from .attribute import Attribute
from .device_type import DeviceType

import uuid

class ZWaveDevice(Device):
    PROTOCOL='zwave'
    dataMappings={'Bool':DataType.Binary,'Byte':DataType.Byte, 'Decimal':DataType.Float,\
    'Int':DataType.Int, 'Short':DataType.Int, 'String':DataType.String, 'Button':DataType.Binary, \
    'List':DataType.List}

    def __init__ (self, node):
        self._valueMap = {}
        super().__init__(self._getDeviceType(node), name = node.name,address=uuid.uuid4().bytes,\
        version=str(node.version))
        self._node = node

    def _getDeviceType(self, node):
        attributes = []
        for key,val in node.get_values(genre='User').items():
            parameter= Parameter(val.label, ZWaveDevice.dataMappings[val.type],max_=val.max, \
            min_=val.min, isControllable=not val.is_read_only,value=val.data)
            attribute=Attribute(val.label,parameters=[parameter])
            attributes.append(attribute)
            self._valueMap[val.label] = val

        return DeviceType(node.product_name, ZWaveDevice.PROTOCOL, node.manufacturer_name,\
        attributes=attributes)


    def getValue(self, attribute):
        """
        Returns the value of an attribute
        attribute is the name of the attribute (String)
        """
        return self._valueMap[attribute].data

    def processEvent(self, val):
        parameters = []
        parameterChange = {
            'name' : val.label,
            'value' : val.data
        }
        parameters.append(parameterChange)
        data = {
            'attribute' : val.label,
            'changes' : parameters
	}
        return data

