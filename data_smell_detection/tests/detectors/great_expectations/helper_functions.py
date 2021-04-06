from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmellRegistry,
    DataSmellMetadata,
)


# Ensure that a data smell has been registered. Check the following:
# + A dictionary is returned by the
#   get_smell_dict_for_profiler_data_type() call.
# + The data smell type in the metadata object is present in the dictionary
#   returned by get_smell_dict_for_profiler_data_type() as a key.
# + The expectation_type is the corresponding dictionary value.
def check_data_smell_stored_in_registry(
        registry: DataSmellRegistry,
        metadata: DataSmellMetadata,
        expectation_type: str):
    for data_type in metadata.profiler_data_types:
        smell_dict = registry.get_smell_dict_for_profiler_data_type(data_type)
        assert isinstance(smell_dict, dict)

        # Ensure that the data smell has been registered for the corresponding
        # ProfilerDataType.
        assert metadata.data_smell_type in smell_dict
        # Ensure that the expectation type is stored as the corresponding dict
        # value.
        assert smell_dict[metadata.data_smell_type] == expectation_type


# Ensure that profiler data types for which no data smells have been registered
# do not contain any smells. Pass the registry to check and the expected types
# (profiler data types for which data smells have been registered).
def check_remaining_data_types_have_no_registered_smells(
        registry,
        expected_types):
    # ProfilerDataTypes which must not contain registered data smells.
    remaining_types = [
        x for x in ProfilerDataType
        if x not in expected_types
    ]
    for data_type in remaining_types:
        # Ensure that no smells have been registered.
        result = registry.get_smell_dict_for_profiler_data_type(data_type)
        assert isinstance(result, dict)
        assert len(result) == 0
