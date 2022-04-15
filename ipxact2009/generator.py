from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from ipxact2009.auto_configure import Choices
from ipxact2009.common_structures import (
    Parameters,
    VendorExtensions,
)
from ipxact2009.identifier import LibraryRefType

__NAMESPACE__ = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


class GeneratorTypeApiType(Enum):
    TGI = "TGI"
    NONE = "none"


class GroupSelectorMultipleGroupSelectionOperator(Enum):
    AND = "and"
    OR = "or"


class InstanceGeneratorTypeScope(Enum):
    INSTANCE = "instance"
    ENTITY = "entity"


@dataclass
class Phase:
    """This is an non-negative floating point number that is used to sequence
    when a generator is run.

    The generators are run in order starting with zero. There may be
    multiple generators with the same phase number. In this case, the
    order should not matter with respect to other generators at the same
    phase. If no phase number is given the generator will be considered
    in the "last" phase and these generators will be run in the order in
    which they are encountered while processing generator elements.
    """
    class Meta:
        name = "phase"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    value: Optional[float] = field(
        default=None,
        metadata={
            "required": True,
        }
    )


class TransportMethodsTransportMethod(Enum):
    FILE = "file"


@dataclass
class GeneratorType:
    """
    Types of generators.

    :ivar name: Unique name
    :ivar display_name:
    :ivar description:
    :ivar phase:
    :ivar parameters:
    :ivar api_type: Indicates the type of API used by the generator.
        Valid value are TGI, and none. If this element is not present,
        TGI is assumed.
    :ivar transport_methods:
    :ivar generator_exe: The pathname to the executable file that
        implements the generator
    :ivar vendor_extensions:
    :ivar hidden: If this attribute is true then the generator should
        not be presented to the user, it may be part of a chain and has
        no useful meaning when invoked standalone.
    """
    class Meta:
        name = "generatorType"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
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
    phase: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    parameters: Optional[Parameters] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    api_type: Optional[GeneratorTypeApiType] = field(
        default=None,
        metadata={
            "name": "apiType",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    transport_methods: Optional["GeneratorType.TransportMethods"] = field(
        default=None,
        metadata={
            "name": "transportMethods",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    generator_exe: Optional[str] = field(
        default=None,
        metadata={
            "name": "generatorExe",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
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
    hidden: bool = field(
        default=False,
        metadata={
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )

    @dataclass
    class TransportMethods:
        """
        :ivar transport_method: Defines a SOAP transport protocol other
            than HTTP which is supported by this generator. The only
            other currently supported protocol is 'file'.
        """
        transport_method: Optional[TransportMethodsTransportMethod] = field(
            default=None,
            metadata={
                "name": "transportMethod",
                "type": "Element",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
                "required": True,
            }
        )


@dataclass
class GroupSelector:
    """Specifies a set of group names used to select subsequent generators.

    The attribute "multipleGroupOperator" specifies the OR or AND
    selection operator if there is more than one group name
    (default=OR).

    :ivar name: Specifies a generator group name or a generator chain
        group name to be selected for inclusion in the generator chain.
    :ivar multiple_group_selection_operator: Specifies the OR or AND
        selection operator if there is more than one group name.
    """
    class Meta:
        name = "groupSelector"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    name: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        }
    )
    multiple_group_selection_operator: GroupSelectorMultipleGroupSelectionOperator = field(
        default=GroupSelectorMultipleGroupSelectionOperator.OR,
        metadata={
            "name": "multipleGroupSelectionOperator",
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )


@dataclass
class Generator(GeneratorType):
    """
    Specifies a set of generators.
    """
    class Meta:
        name = "generator"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


@dataclass
class GeneratorSelectorType:
    class Meta:
        name = "generatorSelectorType"

    group_selector: Optional[GroupSelector] = field(
        default=None,
        metadata={
            "name": "groupSelector",
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            "required": True,
        }
    )


@dataclass
class InstanceGeneratorType(GeneratorType):
    """
    :ivar group: An identifier to specify the generator group. This is
        used by generator chains for selecting which generators to run.
    :ivar scope: The scope attribute applies to component generators and
        specifies whether the generator should be run for each instance
        of the entity (or module) or just once for all instances of the
        entity.
    """
    class Meta:
        name = "instanceGeneratorType"

    group: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )
    scope: InstanceGeneratorTypeScope = field(
        default=InstanceGeneratorTypeScope.INSTANCE,
        metadata={
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )


@dataclass
class AbstractorGenerator(InstanceGeneratorType):
    """Specifies a set of abstractor generators.

    The scope attribute applies to abstractor generators and specifies
    whether the generator should be run for each instance of the entity
    (or module) or just once for all instances of the entity.
    """
    class Meta:
        name = "abstractorGenerator"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


@dataclass
class ComponentGenerator(InstanceGeneratorType):
    """Specifies a set of component generators.

    The scope attribute applies to component generators and specifies
    whether the generator should be run for each instance of the entity
    (or module) or just once for all instances of the entity.
    """
    class Meta:
        name = "componentGenerator"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"


@dataclass
class GeneratorChain:
    """
    :ivar vendor: Name of the vendor who supplies this file.
    :ivar library: Name of the logical library this element belongs to.
    :ivar name: The name of the object.
    :ivar version: Indicates the version of the named element.
    :ivar generator_chain_selector: Select other generator chain files
        for inclusion into this chain. The boolean attribute "unique"
        (default false) specifies that only a single generator is valid
        in this context. If more that one generator is selected based on
        the selection criteria, DE will prompt the user to resolve to a
        single generator.
    :ivar component_generator_selector: Selects generators declared in
        components of the current design for inclusion into this
        generator chain.
    :ivar generator:
    :ivar chain_group: Identifies this generator chain as belonging to
        the named group. This is used by other generator chains to
        select this chain for programmatic inclusion.
    :ivar display_name:
    :ivar description:
    :ivar choices:
    :ivar vendor_extensions:
    :ivar hidden: If this attribute is true then the generator should
        not be presented to the user, it may be part of a chain and has
        no useful meaning when invoked standalone.
    """
    class Meta:
        name = "generatorChain"
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
    generator_chain_selector: List["GeneratorChain.GeneratorChainSelector"] = field(
        default_factory=list,
        metadata={
            "name": "generatorChainSelector",
            "type": "Element",
            "sequential": True,
        }
    )
    component_generator_selector: List[GeneratorSelectorType] = field(
        default_factory=list,
        metadata={
            "name": "componentGeneratorSelector",
            "type": "Element",
            "sequential": True,
        }
    )
    generator: List[Generator] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequential": True,
        }
    )
    chain_group: List[str] = field(
        default_factory=list,
        metadata={
            "name": "chainGroup",
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
    choices: Optional[Choices] = field(
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
    hidden: bool = field(
        default=False,
        metadata={
            "type": "Attribute",
            "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
        }
    )

    @dataclass
    class GeneratorChainSelector:
        """
        :ivar group_selector:
        :ivar generator_chain_ref: Select another generator chain using
            the unique identifier of this generator chain.
        :ivar unique: Specifies that only a single generator is valid in
            this context. If more that one generator is selcted based on
            the selection criteria, DE will prompt the user to resolve
            to a single generator.
        """
        group_selector: Optional[GroupSelector] = field(
            default=None,
            metadata={
                "name": "groupSelector",
                "type": "Element",
            }
        )
        generator_chain_ref: Optional[LibraryRefType] = field(
            default=None,
            metadata={
                "name": "generatorChainRef",
                "type": "Element",
            }
        )
        unique: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            }
        )


@dataclass
class AbstractorGenerators:
    """
    List of abstractor generators.
    """
    class Meta:
        name = "abstractorGenerators"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    abstractor_generator: List[AbstractorGenerator] = field(
        default_factory=list,
        metadata={
            "name": "abstractorGenerator",
            "type": "Element",
            "min_occurs": 1,
        }
    )


@dataclass
class ComponentGenerators:
    """
    List of component generators.
    """
    class Meta:
        name = "componentGenerators"
        namespace = "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"

    component_generator: List[ComponentGenerator] = field(
        default_factory=list,
        metadata={
            "name": "componentGenerator",
            "type": "Element",
            "min_occurs": 1,
        }
    )
