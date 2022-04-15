from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from ipxact2009.common_structures import VendorExtensions
from ipxact2009.constraints import AbstractionDefPortConstraintsType
from ipxact2009.identifier import LibraryRefType
from ipxact2009.mod_8 import RequiresDriver

__NAMESPACE__ = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


class PresenceValue(Enum):
    REQUIRED = "required"
    ILLEGAL = "illegal"
    OPTIONAL = "optional"


class ServiceTypeInitiative(Enum):
    REQUIRES = "requires"
    PROVIDES = "provides"
    BOTH = "both"


class WirePortDirection(Enum):
    IN = "in"
    OUT = "out"
    INOUT = "inout"


@dataclass
class Presence:
    """If this element is present, the existance of the port is controlled by
    the specified value.

    valid values are 'illegal', 'required' and 'optional'.
    """
    class Meta:
        name = "presence"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    value: PresenceValue = field(
        default=PresenceValue.OPTIONAL
    )


@dataclass
class ServiceType:
    """
    The service that this transactional port can provide or requires.

    :ivar initiative: If this element is present, the type of access is
        restricted to the specified value.
    :ivar type_name: Defines the name of the transactional interface
        type.
    :ivar vendor_extensions:
    """
    class Meta:
        name = "serviceType"

    initiative: ServiceTypeInitiative = field(
        default=ServiceTypeInitiative.REQUIRES,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
        }
    )
    type_name: List["ServiceType.TypeName"] = field(
        default_factory=list,
        metadata={
            "name": "typeName",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "min_occurs": 1,
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
    class TypeName:
        """
        :ivar value:
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
        implicit: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )


@dataclass
class AbstractionDefinition:
    """
    Define the ports and other information of a particular abstraction of the
    bus.

    :ivar vendor: Name of the vendor who supplies this file.
    :ivar library: Name of the logical library this element belongs to.
    :ivar name: The name of the object.
    :ivar version: Indicates the version of the named element.
    :ivar bus_type: Reference to the busDefinition that this
        abstractionDefinition implements.
    :ivar extends: Optional name of abstraction type that this
        abstraction definition is compatible with. This abstraction
        definition may change the definitions of ports in the existing
        abstraction definition and add new ports, the ports in the
        original abstraction are not deleted but may be marked illegal
        to disallow their use. This abstraction definition may only
        extend another abstraction definition if the bus type of this
        abstraction definition extends the bus type of the extended
        abstraction definition
    :ivar ports: This is a list of logical ports defined by the bus.
    :ivar description:
    :ivar vendor_extensions:
    """
    class Meta:
        name = "abstractionDefinition"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    vendor: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    library: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    version: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    bus_type: Optional[LibraryRefType] = field(
        default=None,
        metadata={
            "name": "busType",
            "type": "Element",
            "required": True,
        }
    )
    extends: Optional[LibraryRefType] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    ports: Optional["AbstractionDefinition.Ports"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    vendor_extensions: Optional[VendorExtensions] = field(
        default=None,
        metadata={
            "name": "vendorExtensions",
            "type": "Element",
        }
    )

    @dataclass
    class Ports:
        port: List["AbstractionDefinition.Ports.Port"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            }
        )

        @dataclass
        class Port:
            """
            :ivar logical_name: The assigned name of this port in bus
                specifications.
            :ivar display_name:
            :ivar description:
            :ivar wire: A port that carries logic or an array of logic
                values
            :ivar transactional: A port that carries complex information
                modeled at a high level of abstraction.
            :ivar vendor_extensions:
            """
            logical_name: Optional[str] = field(
                default=None,
                metadata={
                    "name": "logicalName",
                    "type": "Element",
                    "required": True,
                }
            )
            display_name: Optional[str] = field(
                default=None,
                metadata={
                    "name": "displayName",
                    "type": "Element",
                }
            )
            description: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                }
            )
            wire: Optional["AbstractionDefinition.Ports.Port.Wire"] = field(
                default=None,
                metadata={
                    "type": "Element",
                }
            )
            transactional: Optional["AbstractionDefinition.Ports.Port.Transactional"] = field(
                default=None,
                metadata={
                    "type": "Element",
                }
            )
            vendor_extensions: Optional[VendorExtensions] = field(
                default=None,
                metadata={
                    "name": "vendorExtensions",
                    "type": "Element",
                }
            )

            @dataclass
            class Wire:
                """
                :ivar qualifier: The type of information this port
                    carries A wire port can carry both address and data,
                    but may not mix this with a clock or reset
                :ivar on_system: Defines constraints for this port when
                    present in a system bus interface with a matching
                    group name.
                :ivar on_master: Defines constraints for this port when
                    present in a master bus interface.
                :ivar on_slave: Defines constraints for this port when
                    present in a slave bus interface.
                :ivar default_value: Indicates the default value for
                    this wire port.
                :ivar requires_driver:
                """
                qualifier: Optional["AbstractionDefinition.Ports.Port.Wire.Qualifier"] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                    }
                )
                on_system: List["AbstractionDefinition.Ports.Port.Wire.OnSystem"] = field(
                    default_factory=list,
                    metadata={
                        "name": "onSystem",
                        "type": "Element",
                    }
                )
                on_master: Optional["AbstractionDefinition.Ports.Port.Wire.OnMaster"] = field(
                    default=None,
                    metadata={
                        "name": "onMaster",
                        "type": "Element",
                    }
                )
                on_slave: Optional["AbstractionDefinition.Ports.Port.Wire.OnSlave"] = field(
                    default=None,
                    metadata={
                        "name": "onSlave",
                        "type": "Element",
                    }
                )
                default_value: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "defaultValue",
                        "type": "Element",
                        "pattern": r"[+]?(0x|0X|#)?[0-9a-fA-F]+[kmgtKMGT]?",
                    }
                )
                requires_driver: Optional[RequiresDriver] = field(
                    default=None,
                    metadata={
                        "name": "requiresDriver",
                        "type": "Element",
                    }
                )

                @dataclass
                class Qualifier:
                    """
                    :ivar is_address: If this element is present, the
                        port contains address information.
                    :ivar is_data: If this element is present, the port
                        contains data information.
                    :ivar is_clock: If this element is present, the port
                        contains only clock information.
                    :ivar is_reset: Is this element is present, the port
                        contains only reset information.
                    """
                    is_address: Optional[bool] = field(
                        default=None,
                        metadata={
                            "name": "isAddress",
                            "type": "Element",
                        }
                    )
                    is_data: Optional[bool] = field(
                        default=None,
                        metadata={
                            "name": "isData",
                            "type": "Element",
                        }
                    )
                    is_clock: Optional[bool] = field(
                        default=None,
                        metadata={
                            "name": "isClock",
                            "type": "Element",
                        }
                    )
                    is_reset: Optional[bool] = field(
                        default=None,
                        metadata={
                            "name": "isReset",
                            "type": "Element",
                        }
                    )

                @dataclass
                class OnSystem:
                    """
                    :ivar group: Used to group system ports into
                        different groups within a common bus.
                    :ivar presence:
                    :ivar width: Number of bits required to represent
                        this port. Absence of this element indicates
                        unconstrained number of bits, i.e. the component
                        will define the number of bits in this port. The
                        logical numbering of the port starts at 0 to
                        width-1.
                    :ivar direction: If this element is present, the
                        direction of this port is restricted to the
                        specified value. The direction is relative to
                        the non-mirrored interface.
                    :ivar mode_constraints: Specifies default
                        constraints for the enclosing wire type port. If
                        the mirroredModeConstraints element is not
                        defined, then these constraints applied to this
                        port when it appears in a 'mode' bus interface
                        or a mirrored-'mode' bus interface. Otherwise
                        they only apply when the port appears in a
                        'mode' bus interface.
                    :ivar mirrored_mode_constraints: Specifies default
                        constraints for the enclosing wire type port
                        when it appears in a mirrored-'mode' bus
                        interface.
                    """
                    group: Optional[str] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        }
                    )
                    presence: Optional[PresenceValue] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    width: Optional[int] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    direction: Optional[WirePortDirection] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    mode_constraints: Optional[AbstractionDefPortConstraintsType] = field(
                        default=None,
                        metadata={
                            "name": "modeConstraints",
                            "type": "Element",
                        }
                    )
                    mirrored_mode_constraints: Optional[AbstractionDefPortConstraintsType] = field(
                        default=None,
                        metadata={
                            "name": "mirroredModeConstraints",
                            "type": "Element",
                        }
                    )

                @dataclass
                class OnMaster:
                    """
                    :ivar presence:
                    :ivar width: Number of bits required to represent
                        this port. Absence of this element indicates
                        unconstrained number of bits, i.e. the component
                        will define the number of bits in this port. The
                        logical numbering of the port starts at 0 to
                        width-1.
                    :ivar direction: If this element is present, the
                        direction of this port is restricted to the
                        specified value. The direction is relative to
                        the non-mirrored interface.
                    :ivar mode_constraints: Specifies default
                        constraints for the enclosing wire type port. If
                        the mirroredModeConstraints element is not
                        defined, then these constraints applied to this
                        port when it appears in a 'mode' bus interface
                        or a mirrored-'mode' bus interface. Otherwise
                        they only apply when the port appears in a
                        'mode' bus interface.
                    :ivar mirrored_mode_constraints: Specifies default
                        constraints for the enclosing wire type port
                        when it appears in a mirrored-'mode' bus
                        interface.
                    """
                    presence: Optional[PresenceValue] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    width: Optional[int] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    direction: Optional[WirePortDirection] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    mode_constraints: Optional[AbstractionDefPortConstraintsType] = field(
                        default=None,
                        metadata={
                            "name": "modeConstraints",
                            "type": "Element",
                        }
                    )
                    mirrored_mode_constraints: Optional[AbstractionDefPortConstraintsType] = field(
                        default=None,
                        metadata={
                            "name": "mirroredModeConstraints",
                            "type": "Element",
                        }
                    )

                @dataclass
                class OnSlave:
                    """
                    :ivar presence:
                    :ivar width: Number of bits required to represent
                        this port. Absence of this element indicates
                        unconstrained number of bits, i.e. the component
                        will define the number of bits in this port. The
                        logical numbering of the port starts at 0 to
                        width-1.
                    :ivar direction: If this element is present, the
                        direction of this port is restricted to the
                        specified value. The direction is relative to
                        the non-mirrored interface.
                    :ivar mode_constraints: Specifies default
                        constraints for the enclosing wire type port. If
                        the mirroredModeConstraints element is not
                        defined, then these constraints applied to this
                        port when it appears in a 'mode' bus interface
                        or a mirrored-'mode' bus interface. Otherwise
                        they only apply when the port appears in a
                        'mode' bus interface.
                    :ivar mirrored_mode_constraints: Specifies default
                        constraints for the enclosing wire type port
                        when it appears in a mirrored-'mode' bus
                        interface.
                    """
                    presence: Optional[PresenceValue] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    width: Optional[int] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    direction: Optional[WirePortDirection] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    mode_constraints: Optional[AbstractionDefPortConstraintsType] = field(
                        default=None,
                        metadata={
                            "name": "modeConstraints",
                            "type": "Element",
                        }
                    )
                    mirrored_mode_constraints: Optional[AbstractionDefPortConstraintsType] = field(
                        default=None,
                        metadata={
                            "name": "mirroredModeConstraints",
                            "type": "Element",
                        }
                    )

            @dataclass
            class Transactional:
                """
                :ivar qualifier: The type of information this port
                    carries A transactional port can carry both address
                    and data information.
                :ivar on_system: Defines constraints for this port when
                    present in a system bus interface with a matching
                    group name.
                :ivar on_master: Defines constraints for this port when
                    present in a master bus interface.
                :ivar on_slave: Defines constraints for this port when
                    present in a slave bus interface.
                """
                qualifier: Optional["AbstractionDefinition.Ports.Port.Transactional.Qualifier"] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                    }
                )
                on_system: List["AbstractionDefinition.Ports.Port.Transactional.OnSystem"] = field(
                    default_factory=list,
                    metadata={
                        "name": "onSystem",
                        "type": "Element",
                    }
                )
                on_master: Optional["AbstractionDefinition.Ports.Port.Transactional.OnMaster"] = field(
                    default=None,
                    metadata={
                        "name": "onMaster",
                        "type": "Element",
                    }
                )
                on_slave: Optional["AbstractionDefinition.Ports.Port.Transactional.OnSlave"] = field(
                    default=None,
                    metadata={
                        "name": "onSlave",
                        "type": "Element",
                    }
                )

                @dataclass
                class Qualifier:
                    """
                    :ivar is_address: If this element is present, the
                        port contains address information.
                    :ivar is_data: If this element is present, the port
                        contains data information.
                    """
                    is_address: Optional[bool] = field(
                        default=None,
                        metadata={
                            "name": "isAddress",
                            "type": "Element",
                        }
                    )
                    is_data: Optional[bool] = field(
                        default=None,
                        metadata={
                            "name": "isData",
                            "type": "Element",
                        }
                    )

                @dataclass
                class OnSystem:
                    """
                    :ivar group: Used to group system ports into
                        different groups within a common bus.
                    :ivar presence:
                    :ivar service: The service that this transactional
                        port can provide or requires.
                    """
                    group: Optional[str] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        }
                    )
                    presence: Optional[PresenceValue] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    service: Optional[ServiceType] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        }
                    )

                @dataclass
                class OnMaster:
                    """
                    :ivar presence:
                    :ivar service: The service that this transactional
                        port can provide or requires.
                    """
                    presence: Optional[PresenceValue] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    service: Optional[ServiceType] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        }
                    )

                @dataclass
                class OnSlave:
                    """
                    :ivar presence:
                    :ivar service: The service that this transactional
                        port can provide or requires.
                    """
                    presence: Optional[PresenceValue] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        }
                    )
                    service: Optional[ServiceType] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        }
                    )
