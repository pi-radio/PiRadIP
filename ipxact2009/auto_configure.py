from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

__NAMESPACE__ = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


@dataclass
class Choices:
    """
    Choices used by elements with an attribute spirit:choiceRef.

    :ivar choice: Non-empty set of legal values for a elements with an
        attribute spirit:choiceRef.
    """
    class Meta:
        name = "choices"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    choice: List["Choices.Choice"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        }
    )

    @dataclass
    class Choice:
        """
        :ivar name: Choice key, available for reference by the
            spirit:choiceRef attribute.
        :ivar enumeration: One possible value of spirit:choice
        """
        name: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        enumeration: List["Choices.Choice.Enumeration"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            }
        )

        @dataclass
        class Enumeration:
            """
            :ivar value:
            :ivar text: When specified, displayed in place of the
                spirit:enumeration value
            :ivar help: Text that may be displayed if the user requests
                help about the meaning of an element
            """
            value: str = field(
                default="",
                metadata={
                    "required": True,
                }
            )
            text: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
                }
            )
            help: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
                }
            )


class DelayValueUnitType(Enum):
    """
    Indicates legal units for delay values.
    """
    PS = "ps"
    NS = "ns"


class FormatType(Enum):
    """This is an indication on the formatof the value for user defined
    properties.

    bitString means either a double quoted string of 1's an 0's or a
    scaledInteger number. bool means a boolean (true, false) is
    expected.  float means a decimal floating point number is expected.
    long means an value of scaledInteger is expected.  String means any
    text is acceptable.
    """
    BIT_STRING = "bitString"
    BOOL = "bool"
    FLOAT = "float"
    LONG = "long"
    STRING = "string"


class RangeTypeType(Enum):
    """This type is used to indicate how the minimum and maximum attributes
    values should be interpreted.

    For purposes of this attribute, an int is 4 bytes and a long is 8
    bytes.
    """
    FLOAT = "float"
    INT = "int"
    UNSIGNED_INT = "unsigned int"
    LONG = "long"
    UNSIGNED_LONG = "unsigned long"
