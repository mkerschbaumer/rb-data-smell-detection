from datasmelldetection.detectors.great_expectations.datasmell import \
    DataSmellMetadata
from datasmelldetection.detectors.great_expectations.datasmell import \
    default_registry
from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.core.datasmells import DataSmellType
# Import great_expectations module to load expectations for
# data smell detection.
import datasmelldetection.detectors.great_expectations
from .helpers import check_data_smell_stored_in_registry


class TestExpectationRegistration:
    # Ensure that importing the
    # datasmelldetection.detectors.great_expectations module
    # registers the corresponding expectations for data smell detection
    # (regarding the default registry).

    def test_expect_column_values_to_not_contain_missing_value_smell(self):
        check_data_smell_stored_in_registry(
            registry=default_registry,
            metadata=DataSmellMetadata(
                data_smell_type=DataSmellType.MISSING_VALUE_SMELL,
                profiler_data_types=[x for x in ProfilerDataType]
            ),
            expectation_type="expect_column_values_to_not_contain_missing_value_smell"
        )
