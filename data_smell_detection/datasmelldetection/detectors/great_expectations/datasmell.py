from abc import ABC
from dataclasses import dataclass
from inspect import isabstract
from typing import Set, Optional, Dict
from great_expectations.exceptions import InvalidExpectationConfigurationError
from great_expectations.expectations.expectation import Expectation
from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.core.datasmells import DataSmellType


@dataclass
class DataSmellMetadata:
    """
    General metadata about an Expectation which can be used for the detection
    of a specific data smell.
    """

    data_smell_type: DataSmellType
    """The data smell which is detected."""  # pylint: disable=W0105

    profiler_data_types: Set[ProfilerDataType]
    """Column types for which smell detection should be performed."""  # pylint: disable=W0105

    def validate_configuration(self):
        """
        Raise exceptions if the configuration is invalid.

        :return: True if the configuration is valid.
        """

        if not isinstance(self.data_smell_type, DataSmellType):
            raise InvalidExpectationConfigurationError("The data_smell_type field must be set!")
        if not isinstance(self.profiler_data_types, (list, tuple)):
            raise InvalidExpectationConfigurationError(
                "The profiler_data_types field must be set to a list or a tuple!")
        # Ensure the profiler data type field only contains the corresponding type
        # (only profiler data types of the corresponding Great Expectations type
        # are allowed)
        for profiler_data_type in self.profiler_data_types:
            if not isinstance(profiler_data_type, ProfilerDataType):
                raise InvalidExpectationConfigurationError(
                    "All elements of profiler_data_types must be valid ProfilerDataType instances!")

        return True


class DataSmellRegistry:
    """Store expectations for specific column types."""

    def __init__(self):
        # Store the expectations for each profiler type
        # Initialize expectations for each ProfilerDataType
        # e.g. integer-specific expectations
        self._registered_data_smells = dict()
        for data_type in ProfilerDataType:
            self._registered_data_smells[data_type] = dict()

    def register(self, metadata: DataSmellMetadata, expectation_type: str):
        """
        Store a new mapping between a data smell and the corresponding Great Expectations
        expectation.

        :param metadata: Information about the smell detection.
        :param expectation_type: The type of the Great Expectations expectation.
        """
        for data_type in metadata.profiler_data_types:
            self._registered_data_smells[data_type][metadata.data_smell_type] = expectation_type

    def get_smell_dict_for_profiler_data_type(self, profiler_data_type: ProfilerDataType) -> \
            Dict[DataSmellType, str]:
        """
        Get the registered data smells for a specific ProfilerDataType (column type)

        :param profiler_data_type: The column type for which data smells have been registered.
        :return: A dictionary which stores the association between the
            :class:`~datasmelldetection.core.datasmells.DataSmellType` and the corresponding type
            of the Great Expectations expectation.
        """
        return self._registered_data_smells[profiler_data_type]


default_registry: DataSmellRegistry = DataSmellRegistry()
"""
The default :class:`.DataSmellRegistry` which is used to register Expectation
classes which perform data smell detection.
"""  # pylint: disable=W0105


class DataSmell(ABC):
    """
    A base class for :class:`~great_expectations.expectations.expectation.Expectation` classes
    which implement data smell detection.

    The main purpose of this class is the association of
    :class:`~great_expectations.expectations.expectation.Expectation` to
    :class:`~datasmelldetection.core.DataSmellType` s. Furthermore, the column types where the data
    smell should be detected is stored too.
    """

    data_smell_metadata: Optional[DataSmellMetadata]
    """
    Information about the detected data smell detection. This attribute is
    required to perform data smell registration at a
    :class:`.DataSmellRegistry`.
    """  # pylint: disable=W0105

    @classmethod
    def is_abstract(cls) -> bool:
        """
        Return wether the class is abstract.

        A class is abstract if :func:`inspect.isabstract` is True or the
        attribute data_smell_metadata is None.
        """
        return cls.data_smell_metadata is None or isabstract(cls)

    # NOTE: register_data_smell has been chosen as the method name to avoid name
    # clashes since this class is meant to be used with multiple inheritance.
    @classmethod
    def register_data_smell(cls, registry: DataSmellRegistry = default_registry):
        """
        Register the corresponding data smell at a :class:`.DataSmellRegistry`.

        The corresponding subclass must inherit from
        :class:`great_expectations.expectations.expectation.Expectation`  and
        must not be abstract. Furthermore, the data_smell_metadata must not be
        None.

        :param registry: The registry where the data smell should be
            registered.
        """
        if cls.is_abstract():
            # TODO: Raise exception
            pass
        if not isinstance(cls, Expectation):
            # TODO: Raise exception
            pass

        # Checks above passed => subclass inherits from Expectation
        expectation: Expectation = cls
        expectation_type = expectation.expectation_type

        # TODO: Ensure metadata is not None (raise exception otherwise)
        # TODO: Remove ignore
        registry.register(cls.data_smell_metadata, expectation_type=expectation_type) # type: ignore
