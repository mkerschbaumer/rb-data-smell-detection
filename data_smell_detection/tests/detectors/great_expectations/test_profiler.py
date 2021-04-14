from typing import Dict, Set

import pytest
from great_expectations.core import ExpectationSuite
from great_expectations.dataset.pandas_dataset import PandasDataset

from datasmelldetection.detectors.great_expectations.profiler import DataSmellAwareProfiler
# Register expectations for data smell detection
import datasmelldetection.detectors.great_expectations.expectations
from datasmelldetection.detectors.great_expectations.datasmell import default_registry
from great_expectations.profile.base import ProfilerDataType

from .fixtures import (
    data_smell_registry_empty,
    data_smell_registry_with_data_smell1,
    data_smell_registry_with_data_smell2,
    data_smell_information1,
    data_smell_information2,
    data_smell_registry_with_data_smell2_information
)
from .helper_functions import check_all_expectation_combinations_in_expectations_suite


@pytest.fixture
def pandas_dataset1() -> PandasDataset:
    return PandasDataset(
        {
            "int_col1": [0, 1, 2, 3, 4],
            "int_col2": [1, 2, 3, 4, 5],
            "float_col1": [0.0, 1.0, 2.0, 3.0, 4.0],
            "float_col2": [0.1, 1.4, 2.5, 3.2, 4.8],
            "string_col1": ["a", "b", "c", "d", "e"]
        }
    )

# Information which columns are of which profiler data types.
@pytest.fixture
def expected_column_types_dataset1() -> Dict[ProfilerDataType, Set[str]]:
    return {
        ProfilerDataType.INT: {"int_col1", "int_col2"},
        ProfilerDataType.FLOAT: {"float_col1", "float_col2"},
        ProfilerDataType.STRING: {"string_col1"}
    }


class TestDataSmellAwareProfiler:
    def test_no_data_smell_registry(self, pandas_dataset1):
        # Ensure that the default_registry is used as a fallback if no
        # registry is provided.

        # Set configuration to None and perform profiling
        profiler_configuration_none = DataSmellAwareProfiler()
        expectation_suite_none, _ = profiler_configuration_none.profile(
            data_asset=pandas_dataset1,
            profiler_configuration=None
        )

        # Set configuration to empty dictionary and perform profiling.
        # Purpose: Provide a configuration but don't provide a registry.
        profiler_configuration_empty = DataSmellAwareProfiler()
        expectation_suite_empty, _ = profiler_configuration_empty.profile(
            data_asset=pandas_dataset1,
            profiler_configuration={}
        )

        # Explicitly provide the default registry.
        profiler_configuration_default_registry = DataSmellAwareProfiler()
        expectation_suite_default, _ = profiler_configuration_default_registry.profile(
            data_asset=pandas_dataset1,
            profiler_configuration={"registry": default_registry}
        )

        # Ensure both cases with no explicit data smell registry set
        # produce the same expectations and column type results.
        assert expectation_suite_none.expectations == expectation_suite_default.expectations
        assert expectation_suite_none.meta['columns'] == expectation_suite_default.meta['columns']
        assert expectation_suite_empty.expectations == expectation_suite_default.expectations
        assert expectation_suite_empty.meta['columns'] == expectation_suite_default.meta['columns']
        # Ensure at least one expectation has been generated.
        assert len(expectation_suite_default.expectations) > 0

    def test_empty_data_smell_registry(self, data_smell_registry_empty, pandas_dataset1):
        # Ensure that no expectations are generated if a data smell registry
        # with no registered expectations is passed.
        profiler = DataSmellAwareProfiler()
        configuration = {"registry": data_smell_registry_empty}
        expectation_suite, _ = profiler.profile(
            data_asset=pandas_dataset1,
            profiler_configuration=configuration
        )

        assert isinstance(expectation_suite, ExpectationSuite)
        # Ensure no expectations were generated.
        assert len(expectation_suite.expectations) == 0

    def test_data_smell_registry_passed(
            self,
            pandas_dataset1,
            expected_column_types_dataset1,
            data_smell_registry_with_data_smell2,
            data_smell_registry_with_data_smell2_information):
        # Test profiling when a data smell registry with 2 registered data
        # smells is passed.

        profiler = DataSmellAwareProfiler()
        expectation_suite, _, = profiler.profile(
            data_asset=pandas_dataset1,
            profiler_configuration={"registry": data_smell_registry_with_data_smell2}
        )

        # The data smells present in the passed data smell registry (needed
        # for ensuring the presence of the corresponding generated
        # expectations).
        data_smell_information = \
            data_smell_registry_with_data_smell2_information

        # Ensure that all combinations of data smells and the corresponding
        # column names are generated. For instance, an expectation for an
        # integer-specific smell should be generated for each integer
        # column in the profiled dataset.
        check_all_expectation_combinations_in_expectations_suite(
            expectation_suite=expectation_suite,
            data_smell_information=data_smell_information,
            expected_column_types=expected_column_types_dataset1
        )

        # TODO: Check the columns key of the meta dictionary which is present
        # in a generated expectation suite.

