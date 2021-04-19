from typing import Tuple, List
import pytest

# A data smell registry with no smells registered.
from datasmelldetection.core import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmellRegistry, \
    DataSmellMetadata
from great_expectations.profile.base import ProfilerDataType

from .helper_dataclasses import DataSmellInformation


# A data smell registry with no smells registered.
@pytest.fixture
def data_smell_registry_empty() -> DataSmellRegistry:
    return DataSmellRegistry()


# Return data smell information for a simulated data smell for int and float
# columns.
@pytest.fixture
def data_smell_information1() -> DataSmellInformation:
    metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
        profiler_data_types={ProfilerDataType.INT, ProfilerDataType.FLOAT}
    )
    expectation_type = "expect_column_values_to_not_contain_extreme_value_smell"
    return DataSmellInformation(
        metadata=metadata,
        expectation_type=expectation_type,
        kwargs={}
    )


# Return the data smell informatoin for a second simulated data smell for float
# columns.
@pytest.fixture
def data_smell_information2() -> DataSmellInformation:
    metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL,
        profiler_data_types={ProfilerDataType.FLOAT}
    )
    expectation_type = \
        "expect_column_values_to_not_contain_integer_as_floating_point_number_smell"
    return DataSmellInformation(
        metadata=metadata,
        expectation_type=expectation_type,
        kwargs={}
    )


# Create a data smell registry with exactly one registered data smell
# (data_smell_information1 is registered).
@pytest.fixture
def data_smell_registry_with_data_smell1(data_smell_registry_empty, data_smell_information1) \
        -> DataSmellRegistry:
    registry = data_smell_registry_empty

    registry.register(
        metadata=data_smell_information1.metadata,
        expectation_type=data_smell_information1.expectation_type
    )
    return registry


# Create a data smell registry with exactly two registered data smells
# (data_smell_information1 and data_smell_information2 are registered).
@pytest.fixture
def data_smell_registry_with_data_smell2(
        data_smell_registry_with_data_smell1,
        data_smell_information2) -> DataSmellRegistry:
    registry = data_smell_registry_with_data_smell1

    registry.register(
        metadata=data_smell_information2.metadata,
        expectation_type=data_smell_information2.expectation_type
    )
    return registry


# The data smells present in the data smell registry
# `data_smell_registry_with_data_smell2`.
@pytest.fixture
def data_smell_registry_with_data_smell2_information(
        data_smell_information1,
        data_smell_information2) -> List[DataSmellInformation]:
    return [
        data_smell_information1,
        data_smell_information2
    ]
