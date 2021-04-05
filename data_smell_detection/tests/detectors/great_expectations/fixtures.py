from typing import Tuple

import pytest


# A data smell registry with no smells registered.
from datasmelldetection.core import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmellRegistry, \
    DataSmellMetadata
from great_expectations.profile.base import ProfilerDataType


# A data smell registry with no smells registered.
@pytest.fixture
def data_smell_registry_empty() -> DataSmellRegistry:
    return DataSmellRegistry()


# Return data smell metadata and the corresponding expectation type for a
# simulated data smell.
@pytest.fixture
def data_smell_metadata1() -> Tuple[DataSmellMetadata, str]:
    metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
        profiler_data_types=(ProfilerDataType.INT, ProfilerDataType.FLOAT)
    )
    expectation_type = "expect_column_values_to_not_contain_extreme_value_smell"
    return metadata, expectation_type


# Return data smell metadata and the corresponding expectation type for a
# simulated data smell.
@pytest.fixture
def data_smell_metadata2() -> Tuple[DataSmellMetadata, str]:
    metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL,
        profiler_data_types={ProfilerDataType.FLOAT}
    )
    expectation_type = \
        "expect_column_values_to_not_contain_integer_as_floating_point_number_smell"
    return metadata, expectation_type


# Create a data smell registry with exactly one registered data smell
# (data_smell_metadata1 is registered).
@pytest.fixture
def data_smell_registry_with_data_smell1(data_smell_registry_empty, data_smell_metadata1) \
        -> DataSmellRegistry:
    metadata, expectation_type = data_smell_metadata1
    registry = data_smell_registry_empty

    registry.register(
        metadata=metadata,
        expectation_type=expectation_type
    )
    return registry


# Create a data smell registry with exactly two registered data smells
# (data_smell_metadata1 and data_smell_metadata2 are registered).
@pytest.fixture
def data_smell_registry_with_data_smell2(
        data_smell_registry_with_data_smell1,
        data_smell_metadata2) -> DataSmellRegistry:
    metadata, expectation_type = data_smell_metadata2
    registry = data_smell_registry_with_data_smell1

    registry.register(
        metadata=metadata,
        expectation_type=expectation_type
    )
    return registry
