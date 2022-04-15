from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from ipxact2009.mod_8 import OtherClockDriver

__NAMESPACE__ = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


class CellTypeValueType(Enum):
    """
    Indicates legal cell class values.
    """
    COMBINATIONAL = "combinational"
    SEQUENTIAL = "sequential"


class CellFunctionValueType(Enum):
    """
    Indicates legal cell function values.
    """
    NAND2 = "nand2"
    BUF = "buf"
    INV = "inv"
    MUX21 = "mux21"
    DFF = "dff"
    LATCH = "latch"
    XOR2 = "xor2"


class CellStrengthValueType(Enum):
    """
    Indicates legal cell strength values.
    """
    LOW = "low"
    MEDIAN = "median"
    HIGH = "high"


@dataclass
class ConstraintSetRef:
    """
    A reference to a set of port constraints.
    """
    class Meta:
        name = "constraintSetRef"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )


class DelayValueType(Enum):
    """Indicates the type of delay value - minimum or maximum delay."""
    MIN = "min"
    MAX = "max"


class EdgeValueType(Enum):
    """
    Indicates legal values for edge specification attributes.
    """
    RISE = "rise"
    FALL = "fall"


@dataclass
class CellSpecification:
    """
    Used to provide a generic description of a technology library cell.

    :ivar cell_function: Defines a technology library cell in library
        independent fashion, based on specification of a cell function
        and strength.
    :ivar cell_class: Defines a technology library cell in library
        independent fashion, based on specification of a cell class and
        strength.
    """
    class Meta:
        name = "cellSpecification"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    cell_function: Optional["CellSpecification.CellFunction"] = field(
        default=None,
        metadata={
            "name": "cellFunction",
            "type": "Element",
        }
    )
    cell_class: Optional["CellSpecification.CellType"] = field(
        default=None,
        metadata={
            "name": "cellClass",
            "type": "Element",
        }
    )

    @dataclass
    class CellFunction:
        value: Optional[CellFunctionValueType] = field(
            default=None,
            metadata={
                "required": True,
            }
        )
        cell_strength: Optional[CellStrengthValueType] = field(
            default=None,
            metadata={
                "name": "cellStrength",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )

    @dataclass
    class CellType:
        value: Optional[CellTypeValueType] = field(
            default=None,
            metadata={
                "required": True,
            }
        )
        cell_strength: Optional[CellStrengthValueType] = field(
            default=None,
            metadata={
                "name": "cellStrength",
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )


@dataclass
class OtherClocks:
    """List of clocks associated with the component that are not associated
    with ports.

    Set the clockSource attribute on the clockDriver to indicate the
    source of a clock not associated with a particular component port.
    """
    class Meta:
        name = "otherClocks"

    other_clock_driver: List[OtherClockDriver] = field(
        default_factory=list,
        metadata={
            "name": "otherClockDriver",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "min_occurs": 1,
        }
    )


@dataclass
class TimingConstraint:
    """Defines a timing constraint for the associated port.

    The constraint is relative to the clock specified by the clockName
    attribute. The clockEdge indicates which clock edge the constraint
    is associated with (default is rising edge). The delayType attribute
    can be specified to further refine the constraint.

    :ivar value:
    :ivar clock_edge:
    :ivar delay_type:
    :ivar clock_name: Indicates the name of the clock to which this
        constraint applies.
    """
    class Meta:
        name = "timingConstraint"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    value: Optional[float] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": 0.0,
            "max_inclusive": 100.0,
        }
    )
    clock_edge: EdgeValueType = field(
        default=EdgeValueType.RISE,
        metadata={
            "name": "clockEdge",
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    delay_type: Optional[DelayValueType] = field(
        default=None,
        metadata={
            "name": "delayType",
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    clock_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "clockName",
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
            "white_space": "collapse",
            "pattern": r"\i[\p{L}\p{N}\.\-:_]*",
        }
    )


@dataclass
class DriveConstraint:
    """Defines a constraint indicating how an input is to be driven.

    The preferred methodology is to specify a library cell in technology
    independent fashion. The implemention tool should assume that the
    associated port is driven by the specified cell, or that the drive
    strength of the input port is indicated by the specified resistance
    value.
    """
    class Meta:
        name = "driveConstraint"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    cell_specification: Optional[CellSpecification] = field(
        default=None,
        metadata={
            "name": "cellSpecification",
            "type": "Element",
            "required": True,
        }
    )


@dataclass
class LoadConstraint:
    """
    Defines a constraint indicating the type of load on an output port.

    :ivar cell_specification:
    :ivar count: Indicates how many loads of the specified cell are
        connected. If not present, 3 is assumed.
    """
    class Meta:
        name = "loadConstraint"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    cell_specification: Optional[CellSpecification] = field(
        default=None,
        metadata={
            "name": "cellSpecification",
            "type": "Element",
            "required": True,
        }
    )
    count: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class AbstractionDefPortConstraintsType:
    """
    Defines constraints that apply to a wire type port in an abstraction
    definition.
    """
    class Meta:
        name = "abstractionDefPortConstraintsType"

    timing_constraint: List[TimingConstraint] = field(
        default_factory=list,
        metadata={
            "name": "timingConstraint",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    drive_constraint: List[DriveConstraint] = field(
        default_factory=list,
        metadata={
            "name": "driveConstraint",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "max_occurs": 2,
            "sequential": True,
        }
    )
    load_constraint: List[LoadConstraint] = field(
        default_factory=list,
        metadata={
            "name": "loadConstraint",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "max_occurs": 3,
            "sequential": True,
        }
    )


@dataclass
class ConstraintSet:
    """Defines constraints that apply to a component port.

    If multiple constraintSet elements are used, each must have a unique
    value for the constraintSetId attribute.

    :ivar name: Unique name
    :ivar display_name:
    :ivar description:
    :ivar vector: The optional element vector specify the bits of a
        vector for which the constraints apply. The vaules of left and
        right must be within the range of the port. If the vector is not
        specified then the constraints apply to all the bits of the
        port.
    :ivar drive_constraint:
    :ivar load_constraint:
    :ivar timing_constraint:
    :ivar constraint_set_id:
    """
    class Meta:
        name = "constraintSet"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
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
    vector: Optional["ConstraintSet.Vector"] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    drive_constraint: Optional[DriveConstraint] = field(
        default=None,
        metadata={
            "name": "driveConstraint",
            "type": "Element",
        }
    )
    load_constraint: Optional[LoadConstraint] = field(
        default=None,
        metadata={
            "name": "loadConstraint",
            "type": "Element",
        }
    )
    timing_constraint: List[TimingConstraint] = field(
        default_factory=list,
        metadata={
            "name": "timingConstraint",
            "type": "Element",
        }
    )
    constraint_set_id: str = field(
        default="default",
        metadata={
            "name": "constraintSetId",
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )

    @dataclass
    class Vector:
        """
        :ivar left: The optional elements left and right can be used to
            select a bit-slice of a vector.
        :ivar right: The optional elements left and right can be used to
            select a bit-slice of a vector.
        """
        left: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        right: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            }
        )


@dataclass
class ConstraintSets:
    """
    List of constraintSet elements for a component port.
    """
    class Meta:
        name = "constraintSets"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    constraint_set: List[ConstraintSet] = field(
        default_factory=list,
        metadata={
            "name": "constraintSet",
            "type": "Element",
            "min_occurs": 1,
        }
    )
