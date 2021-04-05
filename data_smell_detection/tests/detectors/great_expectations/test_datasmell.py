from great_expectations.profile.base import ProfilerDataType

from .helpers import (
    check_data_smell_stored_in_registry,
    check_remaining_data_types_have_no_registered_smells
)
from .fixtures import (
    data_smell_registry_empty,
    data_smell_registry_with_data_smell1,
    data_smell_registry_with_data_smell2,
    data_smell_metadata1,
    data_smell_metadata2
)


class TestDataSmellMetadata:
    def test_validate_configuration(self):
        # TODO: Implement
        pass


class TestDataSmellRegistry:
    def test_creation(self, data_smell_registry_empty):
        # Iterate over possible values of ProfilerDataType and ensure that
        # after the creation no data smells are stored.
        for profiler_data_type in ProfilerDataType:
            result = data_smell_registry_empty.get_smell_dict_for_profiler_data_type(profiler_data_type)
            assert len(result) == 0

    def test_one_data_smell(self, data_smell_registry_with_data_smell1, data_smell_metadata1):
        # Perform registration of one data smell and ensure that
        # get_smell_dict_for_profiler_data_type() calls return expected
        # results. The registration of the corresponding smell is performed
        # by the fixture.

        metadata1, expectation_type1 = data_smell_metadata1
        registry = data_smell_registry_with_data_smell1

        # Ensure the registration of the first data smell (extreme value smell)
        # was successful
        check_data_smell_stored_in_registry(registry, metadata1, expectation_type1)
        # Ensure that only one data smell has been registered for int and float.
        for data_type in [ProfilerDataType.INT, ProfilerDataType.FLOAT]:
            result = registry.get_smell_dict_for_profiler_data_type(data_type)
            assert len(result) == 1

        # Ensure that the data smell has not been registered for other
        # ProfilerDataTypes (not int and not float).
        check_remaining_data_types_have_no_registered_smells(
            registry,
            metadata1.profiler_data_types
        )

    def test_two_data_smells(
            self,
            data_smell_registry_with_data_smell2,
            data_smell_metadata1,
            data_smell_metadata2):
        # Perform registration of two data smells and ensure that
        # get_smell_dict_for_profiler_data_type() calls return expected
        # results. The registration of the corresponding smells is performed
        # by the fixtures.

        # NOTE: data_smell_registry_with_data_smell2 already has two
        # smells registered.
        registry = data_smell_registry_with_data_smell2
        metadata2, expectation_type2 = data_smell_metadata2

        # Check if registration of second data smell was successful
        check_data_smell_stored_in_registry(
            registry,
            metadata2,
            expectation_type2
        )

        # Ensure that the extreme value smell registered before (data smell 1)
        # is still present.
        metadata1, expectation_type1 = data_smell_metadata1
        check_data_smell_stored_in_registry(
            registry,
            metadata1,
            expectation_type1
        )

        # Ensure that only int and float smells have been registered.
        check_remaining_data_types_have_no_registered_smells(
            registry,
            {ProfilerDataType.INT, ProfilerDataType.FLOAT}
        )


class TestDataSmell:
    def test_is_abstract(self):
        # TODO
        pass

    def test_register_data_smell(self):
        # TODO
        pass
