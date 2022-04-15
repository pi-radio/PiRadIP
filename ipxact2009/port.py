from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from ipxact2009.auto_configure import (
    FormatType,
    RangeTypeType,
)
from ipxact2009.common_structures import (
    Parameter,
    VendorExtensions,
)
from ipxact2009.configurable import ResolveType
from ipxact2009.constraints import ConstraintSets
from ipxact2009.mod_8 import Driver

__NAMESPACE__ = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


class ComponentPortDirectionType(Enum):
    """
    The direction of a component port.
    """
    IN = "in"
    OUT = "out"
    INOUT = "inout"
    PHANTOM = "phantom"


class InitiativeValue(Enum):
    REQUIRES = "requires"
    PROVIDES = "provides"
    BOTH = "both"
    PHANTOM = "phantom"


@dataclass
class PortAccessHandle:
    """If present, is a method to be used to get hold of the object
    representing the port.

    This is typically a function call or array element reference in
    systemC.
    """
    class Meta:
        name = "portAccessHandle"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )


class PortAccessTypeValue(Enum):
    REF = "ref"
    PTR = "ptr"


@dataclass
class TransTypeDef:
    """
    Definition of a single transactional type defintion.

    :ivar type_name: The name of the port type. Can be any predefined
        type such sc_port or sc_export in SystemC or any user-defined
        type such as tlm_port.
    :ivar type_definition: Where the definition of the type is
        contained. For SystemC and SystemVerilog it is the include file
        containing the type definition.
    """
    class Meta:
        name = "transTypeDef"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    type_name: Optional["TransTypeDef.TypeName"] = field(
        default=None,
        metadata={
            "name": "typeName",
            "type": "Element",
            "required": True,
        }
    )
    type_definition: List[str] = field(
        default_factory=list,
        metadata={
            "name": "typeDefinition",
            "type": "Element",
        }
    )

    @dataclass
    class TypeName:
        """
        :ivar value:
        :ivar constrained: Defines that the type for the port has
            constrainted the number of bits in the vector
        """
        value: str = field(
            default="",
            metadata={
                "required": True,
            }
        )
        constrained: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )


@dataclass
class WireTypeDef:
    """
    Definition of a single wire type defintion that can relate to multiple
    views.

    :ivar type_name: The name of the logic type. Examples could be
        std_logic, std_ulogic, std_logic_vector, sc_logic, ...
    :ivar type_definition: Where the definition of the type is
        contained. For std_logic, this is contained in
        IEEE.std_logic_1164.all. For sc_logic, this is contained in
        systemc.h. For VHDL this is the library and package as defined
        by the "used" statement. For SystemC and SystemVerilog it is the
        include file required. For verilog this is not needed.
    :ivar view_name_ref: A reference to a view name in the file for
        which this type applies.
    """
    class Meta:
        name = "wireTypeDef"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    type_name: Optional["WireTypeDef.TypeName"] = field(
        default=None,
        metadata={
            "name": "typeName",
            "type": "Element",
            "required": True,
        }
    )
    type_definition: List[str] = field(
        default_factory=list,
        metadata={
            "name": "typeDefinition",
            "type": "Element",
        }
    )
    view_name_ref: List[str] = field(
        default_factory=list,
        metadata={
            "name": "viewNameRef",
            "type": "Element",
            "min_occurs": 1,
        }
    )

    @dataclass
    class TypeName:
        """
        :ivar value:
        :ivar constrained: Defines that the type for the port has
            constrainted the number of bits in the vector
        """
        value: str = field(
            default="",
            metadata={
                "required": True,
            }
        )
        constrained: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )


@dataclass
class Initiative:
    """
    If this element is present, the type of access is restricted to the
    specified value.
    """
    class Meta:
        name = "initiative"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    value: Optional[InitiativeValue] = field(
        default=None
    )


@dataclass
class PortAccessType:
    """Indicates how a netlister accesses a port.

    'ref' means accessed by reference (default) and 'ptr' means accessed
    by pointer.
    """
    class Meta:
        name = "portAccessType"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    value: Optional[PortAccessTypeValue] = field(
        default=None
    )


@dataclass
class PortAccessType1:
    """
    :ivar port_access_type: Indicates how a netlister accesses a port.
        'ref' means accessed by reference (default) and 'ptr' means
        accessed through a pointer.
    :ivar port_access_handle:
    """
    class Meta:
        name = "portAccessType"

    port_access_type: Optional[PortAccessTypeValue] = field(
        default=None,
        metadata={
            "name": "portAccessType",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    port_access_handle: Optional[str] = field(
        default=None,
        metadata={
            "name": "portAccessHandle",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )


@dataclass
class ServiceTypeDef:
    """
    Definition of a single service type defintion.

    :ivar type_name: The name of the service type. Can be any predefined
        type such as booean or integer or any user-defined type such as
        addr_type or data_type.
    :ivar type_definition: Where the definition of the type is contained
        if the type if not part of the language. For SystemC and
        SystemVerilog it is the include file containing the type
        definition.
    :ivar parameters: list service parameters (e.g. parameters for a
        systemVerilog interface)
    """
    class Meta:
        name = "serviceTypeDef"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    type_name: Optional["ServiceTypeDef.TypeName"] = field(
        default=None,
        metadata={
            "name": "typeName",
            "type": "Element",
            "required": True,
        }
    )
    type_definition: List[str] = field(
        default_factory=list,
        metadata={
            "name": "typeDefinition",
            "type": "Element",
        }
    )
    parameters: Optional["ServiceTypeDef.Parameters"] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )

    @dataclass
    class TypeName:
        """
        :ivar value:
        :ivar constrained: Defines that the type for the port has
            constrainted the number of bits in the vector
        :ivar implicit: Defines that the typeName supplied for this
            service is implicit and a netlister should not declare this
            service in a language specific top-level netlist
        """
        value: str = field(
            default="",
            metadata={
                "required": True,
            }
        )
        constrained: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        implicit: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )

    @dataclass
    class Parameters:
        parameter: List[Parameter] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            }
        )


@dataclass
class Vector:
    """
    Definition of the indecies for a vectored port.

    :ivar left: The optional elements left and right can be used to
        select a bit-slice of a port vector to map to the bus interface.
    :ivar right: The optional elements left and right can be used to
        select a bit-slice of a port vector to map to the bus interface.
    """
    class Meta:
        name = "vector"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    left: Optional["Vector.Left"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    right: Optional["Vector.Right"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )

    @dataclass
    class Left:
        value: Optional[int] = field(
            default=None,
            metadata={
                "required": True,
            }
        )
        format: FormatType = field(
            default=FormatType.LONG,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        resolve: ResolveType = field(
            default=ResolveType.IMMEDIATE,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        id: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        dependency: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        any_attributes: Dict[str, str] = field(
            default_factory=dict,
            metadata={
                "type": "Attributes",
                "namespace": "##any",
            }
        )
        choice_ref: Optional[str] = field(
            default=None,
            metadata={
                "name": "choiceRef",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        order: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        config_groups: List[str] = field(
            default_factory=list,
            metadata={
                "name": "configGroups",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
                "tokens": True,
            }
        )
        bit_string_length: Optional[int] = field(
            default=None,
            metadata={
                "name": "bitStringLength",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        minimum: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        maximum: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        range_type: RangeTypeType = field(
            default=RangeTypeType.FLOAT,
            metadata={
                "name": "rangeType",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        prompt: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )

    @dataclass
    class Right:
        value: Optional[int] = field(
            default=None,
            metadata={
                "required": True,
            }
        )
        format: FormatType = field(
            default=FormatType.LONG,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        resolve: ResolveType = field(
            default=ResolveType.IMMEDIATE,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        id: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        dependency: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        any_attributes: Dict[str, str] = field(
            default_factory=dict,
            metadata={
                "type": "Attributes",
                "namespace": "##any",
            }
        )
        choice_ref: Optional[str] = field(
            default=None,
            metadata={
                "name": "choiceRef",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        order: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        config_groups: List[str] = field(
            default_factory=list,
            metadata={
                "name": "configGroups",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
                "tokens": True,
            }
        )
        bit_string_length: Optional[int] = field(
            default=None,
            metadata={
                "name": "bitStringLength",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        minimum: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        maximum: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        range_type: RangeTypeType = field(
            default=RangeTypeType.FLOAT,
            metadata={
                "name": "rangeType",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        prompt: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )


@dataclass
class WireTypeDefs:
    """The group of wire type definitions.

    If no match to a viewName is found then the default language types
    are to be used. See the User Guide for these default types.
    """
    class Meta:
        name = "wireTypeDefs"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    wire_type_def: List[WireTypeDef] = field(
        default_factory=list,
        metadata={
            "name": "wireTypeDef",
            "type": "Element",
            "min_occurs": 1,
        }
    )


@dataclass
class PortWireType:
    """
    Wire port type for a component.

    :ivar direction: The direction of a wire style port. The basic
        directions for a port are 'in' for input ports, 'out' for output
        port and 'inout' for bidirectional and tristate ports. A value
        of 'phantom' is also allowed and define a port that exist on the
        IP-XACT component but not on the HDL model.
    :ivar vector: Specific left and right vector bounds. Signal width is
        max(left,right)-min(left,right)+1 When the bounds are not
        present, a scalar port is assumed.
    :ivar wire_type_defs:
    :ivar driver:
    :ivar constraint_sets:
    :ivar all_logical_directions_allowed: True if logical ports with
        different directions from the physical port direction may be
        mapped onto this port. Forbidden for phantom ports, which always
        allow logical ports with all direction value to be mapped onto
        the physical port. Also ignored for inout ports, since any
        logical port maybe mapped to a physical inout port.
    """
    class Meta:
        name = "portWireType"

    direction: Optional[ComponentPortDirectionType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
        }
    )
    vector: Optional[Vector] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    wire_type_defs: Optional[WireTypeDefs] = field(
        default=None,
        metadata={
            "name": "wireTypeDefs",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    driver: Optional[Driver] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    constraint_sets: Optional[ConstraintSets] = field(
        default=None,
        metadata={
            "name": "constraintSets",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    all_logical_directions_allowed: bool = field(
        default=False,
        metadata={
            "name": "allLogicalDirectionsAllowed",
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )


@dataclass
class ServiceTypeDefs:
    """The group of type definitions.

    If no match to a viewName is found then the default language types
    are to be used. See the User Guide for these default types.
    """
    class Meta:
        name = "serviceTypeDefs"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    service_type_def: List[ServiceTypeDef] = field(
        default_factory=list,
        metadata={
            "name": "serviceTypeDef",
            "type": "Element",
            "min_occurs": 1,
        }
    )


@dataclass
class AbstractorPortWireType(PortWireType):
    """
    Wire port type for an abstractor.
    """
    class Meta:
        name = "abstractorPortWireType"


@dataclass
class PortTransactionalType:
    """
    Transactional port type.

    :ivar trans_type_def: Definition of the port type expressed in the
        default language for this port (i.e. SystemC or SystemV).
    :ivar service: Describes the interface protocol.
    :ivar connection: Bounds number of legal connections.
    :ivar all_logical_initiatives_allowed: True if logical ports with
        different initiatives from the physical port initiative may be
        mapped onto this port. Forbidden for phantom ports, which always
        allow logical ports with all initiatives value to be mapped onto
        the physical port. Also ignored for "both" ports, since any
        logical port may be mapped to a physical "both" port.
    """
    class Meta:
        name = "portTransactionalType"

    trans_type_def: Optional[TransTypeDef] = field(
        default=None,
        metadata={
            "name": "transTypeDef",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    service: Optional["PortTransactionalType.Service"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
        }
    )
    connection: Optional["PortTransactionalType.Connection"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    all_logical_initiatives_allowed: bool = field(
        default=False,
        metadata={
            "name": "allLogicalInitiativesAllowed",
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )

    @dataclass
    class Service:
        """
        :ivar initiative: Defines how the port accesses this service.
        :ivar service_type_defs: The group of service type definitions.
        :ivar vendor_extensions:
        """
        initiative: Optional[InitiativeValue] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
                "required": True,
            }
        )
        service_type_defs: Optional[ServiceTypeDefs] = field(
            default=None,
            metadata={
                "name": "serviceTypeDefs",
                "type": "Element",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        vendor_extensions: Optional[VendorExtensions] = field(
            default=None,
            metadata={
                "name": "vendorExtensions",
                "type": "Element",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )

    @dataclass
    class Connection:
        """
        :ivar max_connections: Indicates the maximum number of
            connections this port supports. If this element is not
            present or set to 0 it implies an unbounded number of
            allowed connections.
        :ivar min_connections: Indicates the minimum number of
            connections this port supports. If this element is not
            present, the minimum number of allowed connections is 1.
        """
        max_connections: Optional[int] = field(
            default=None,
            metadata={
                "name": "maxConnections",
                "type": "Element",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )
        min_connections: Optional[int] = field(
            default=None,
            metadata={
                "name": "minConnections",
                "type": "Element",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )


@dataclass
class PortDeclarationType:
    """
    Basic port declarations.

    :ivar name: Unique name
    :ivar display_name:
    :ivar description:
    :ivar wire: Defines a port whose type resolves to simple bits.
    :ivar transactional: Defines a port that implements or uses a
        service that can be implemented with functions or methods.
    :ivar access: Port access characteristics.
    """
    class Meta:
        name = "portDeclarationType"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
            "white_space": "collapse",
            "pattern": r"\i[\p{L}\p{N}\.\-:_]*",
        }
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    wire: Optional[PortWireType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    transactional: Optional[PortTransactionalType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    access: Optional[PortAccessTypeValue] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )


@dataclass
class PortType(PortDeclarationType):
    """
    A port description, giving a name and an access type for high level ports.
    """
    class Meta:
        name = "portType"

    vendor_extensions: Optional[VendorExtensions] = field(
        default=None,
        metadata={
            "name": "vendorExtensions",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )


@dataclass
class AbstractorPortType(PortType):
    """
    A port description, giving a name and an access type for high level ports.
    """
    class Meta:
        name = "abstractorPortType"


@dataclass
class Port(PortType):
    """
    Describes port characteristics.
    """
    class Meta:
        name = "port"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"
