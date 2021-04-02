import pytest
from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmellRegistry,
    DataSmellMetadata
)
from .helpers import (
    check_data_smell_stored_in_registry,
    check_remaining_data_types_have_no_registered_smells
)


class TestDataSmellMetadata:
    def test_validate_configuration(self):
        # TODO: Implement
        pass


@pytest.fixture
def data_smell_registry():
    return DataSmellRegistry()


class TestDataSmellRegistry:
    def test_creation(self, data_smell_registry):
        # Iterate over possible values of ProfilerDataType and ensure that
        # after the creation no data smells are stored.
        for profiler_data_type in ProfilerDataType:
            result = data_smell_registry.get_smell_dict_for_profiler_data_type(profiler_data_type)
            assert len(result) == 0

    def test_general(self, data_smell_registry):
        # Perform registration of data smells and ensure that
        # get_smell_dict_for_profiler_data_type() calls return expected
        # results.

        # Simulated smell which should be registered
        metadata1 = DataSmellMetadata(
            data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
            profiler_data_types=(ProfilerDataType.INT, ProfilerDataType.FLOAT)
        )
        expectation_type1 = "expect_column_values_to_not_contain_extreme_value_smell"

        data_smell_registry.register(metadata=metadata1, expectation_type=expectation_type1)
        # Ensure the registration was successful
        check_data_smell_stored_in_registry(data_smell_registry, metadata1, expectation_type1)
        # Ensure that only one data smell has been registered for int and float.
        for data_type in [ProfilerDataType.INT, ProfilerDataType.FLOAT]:
            result = data_smell_registry.get_smell_dict_for_profiler_data_type(data_type)
            assert len(result) == 1

        # Ensure that the data smell has not been registered for other
        # ProfilerDataTypes (not int and not float).
        check_remaining_data_types_have_no_registered_smells(
            data_smell_registry,
            metadata1.profiler_data_types
        )

        # Second simulated smell which should be registered
        metadata2 = DataSmellMetadata(
            data_smell_type=DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL,
            profiler_data_types={ProfilerDataType.FLOAT}
        )
        expectation_type2 = \
            "expect_column_values_to_not_contain_integer_as_floating_point_number_smell"

        # Register and check if registration was successful
        data_smell_registry.register(metadata=metadata2, expectation_type=expectation_type2)
        check_data_smell_stored_in_registry(data_smell_registry, metadata2, expectation_type2)

        # Ensure that the extreme value smell registered before is still
        # present.
        check_data_smell_stored_in_registry(data_smell_registry, metadata1, expectation_type1)

        # Ensure that only int and float smells have been registered.
        check_remaining_data_types_have_no_registered_smells(
            data_smell_registry,
            {ProfilerDataType.INT, ProfilerDataType.FLOAT}
        )


class TestDataSmell:
    def test_is_abstract(self):
        # TODO
        pass

    def test_register_data_smell(self):
        # TODO
        pass
