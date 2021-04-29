from dataclasses import dataclass
from typing import Dict, Set, Any, List, Optional

import pytest
from datasmelldetection.core import DataSmellType
from great_expectations.core import ExpectationSuite
from great_expectations.data_asset import DataAsset
from great_expectations.dataset.pandas_dataset import PandasDataset
from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.detectors.great_expectations.profiler import DataSmellAwareProfiler
# Register expectations for data smell detection
import datasmelldetection.detectors.great_expectations.expectations
from datasmelldetection.detectors.great_expectations.datasmell import default_registry, \
    DataSmellRegistry

from .fixtures import (
    data_smell_registry_empty,
    data_smell_registry_with_data_smell1,
    data_smell_registry_with_data_smell2,
    data_smell_information1,
    data_smell_information2,
    data_smell_registry_with_data_smell1_information,
    data_smell_registry_with_data_smell2_information,
    data_smell_registry_with_data_smell1_custom_kwargs_information,
    data_smell_registry_with_data_smell2_custom_kwargs_information,
    data_smell_registry_with_data_smell2_custom_kwargs
)
from .helper_dataclasses import DataSmellInformation
from .helper_functions import (
    check_all_expectation_combinations_in_expectations_suite,
    check_column_types_in_expectation_suite_meta_information
)


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


@dataclass
class ProfilerTestCase:
    # The name of the test which is contained in the expectation that is raised
    # if the test fails.
    title: str

    # The dataset which should be profiled.
    dataset: DataAsset

    # The data smell registry which is used for profiling.
    registry: Optional[DataSmellRegistry]

    # The data smell configuration which contains data smell specific kwargs
    # which should be used by the profiler.
    data_smell_configuration: Optional[Dict[DataSmellType, Dict[str, Any]]]

    # The expected number of expectations which should be generated by
    # profiling.
    expected_nr_of_expectations: Optional[int]

    # Information about data smells which are present in the corresponding
    # data smell registry (needed for ensuring the presence of the
    # corresponding generated expectations).
    registered_data_smell_information: Optional[List[DataSmellInformation]] = None

    # Information which columns are of which column type. This field is
    # required to ensure the presence of the corresponding generated
    # expectations. The column names are stored as the dict values.
    columns_by_column_type: Optional[Dict[ProfilerDataType, Set[str]]] = None


# Generate data smell configuration testcases which should have 0
# generated expectations. Any registry used with an empty data smell
# configuration should have 0 generated expectations. Tests generated
# by this fixture have the prefix "test_empty_dsc_".
@pytest.fixture
def profiler_testcases_empty_data_smell_configuration(
        pandas_dataset1,
        expected_column_types_dataset1,
        data_smell_registry_with_data_smell2,
        data_smell_registry_empty) -> List[ProfilerTestCase]:
    testcases: List[ProfilerTestCase] = list()

    registries: Dict[str, Optional[DataSmellRegistry]] = {
        "none": None,
        "nonempty": data_smell_registry_with_data_smell2,
        "empty": data_smell_registry_empty
    }
    data_smell_configuration_name: str = "empty"
    for registry_name, registry in registries.items():
        testcase: ProfilerTestCase = ProfilerTestCase(
            dataset=pandas_dataset1,
            registry=registry,
            data_smell_configuration={},
            expected_nr_of_expectations=0,
            title=f"test_empty_dsc_{registry_name}_registry",
            columns_by_column_type=expected_column_types_dataset1
        )
        testcases.append(testcase)

    return testcases


# Generate registry related testcases which should have 0 generated
# expectations. Any data smell configuration used with an empty data smell
# registry should have 0 generated expectations. Tests generated by this
# fixture have the prefix "test_empty_registry_".
@pytest.fixture
def profiler_testcases_empty_data_smell_registry(
        pandas_dataset1,
        expected_column_types_dataset1,
        data_smell_registry_empty) -> List[ProfilerTestCase]:
    testcases: List[ProfilerTestCase] = list()

    data_smell_configurations: Dict[str, Optional[Dict[DataSmellType, Dict[str, Any]]]] = {
        "none": None,
        "empty": {},
        "nonempty": {
            DataSmellType.MISSING_VALUE_SMELL: {
                "mostly": 0.9
            },
            DataSmellType.EXTREME_VALUE_SMELL: {
                "threshold": 3
            }
        }
    }
    for data_smell_configuration_name, data_smell_configuration in data_smell_configurations.items():
        testcase: ProfilerTestCase = ProfilerTestCase(
            dataset=pandas_dataset1,
            registry=data_smell_registry_empty,
            data_smell_configuration=data_smell_configuration,
            expected_nr_of_expectations=0,
            title=f"test_empty_registry_{data_smell_configuration_name}_dsc",
            columns_by_column_type=expected_column_types_dataset1
        )
        testcases.append(testcase)

    return testcases


# Generate testcases for profiling where a nonempty expectation suite should
# be generated. The data smell configuration is only used for filtering of
# the present data smell types (e.g. only detect the specified data smell
# types). No custom kwargs are used. Hence, the generated expectation
# configurations only contain the "column" key. Tests generated by this
# fixture have the "test_default_kwargs_" prefix.
@pytest.fixture
def profiler_testcases_default_kwargs(
        pandas_dataset1,
        expected_column_types_dataset1,
        data_smell_registry_with_data_smell1_information,
        data_smell_registry_with_data_smell2_information,
        data_smell_registry_with_data_smell2) -> List[ProfilerTestCase]:
    return [
        ProfilerTestCase(
            # Provide no data smell configuration (None).
            title="test_default_kwargs_none_dsc",
            dataset=pandas_dataset1,
            columns_by_column_type=expected_column_types_dataset1,
            registry=data_smell_registry_with_data_smell2,
            registered_data_smell_information=data_smell_registry_with_data_smell2_information,
            data_smell_configuration=None,
            # Ensure that exactly 6 expectations are generated.
            # DataSmellType.EXTREME_VALUE_SMELL for int and float columns (2 int
            #   and 2 float columns are present) => 4 expectations.
            # DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL for float columns
            #   => 2 expectations
            # => 6 expectations in total if all expected combination and no
            #   additional expectation is generated.
            expected_nr_of_expectations=6
        ),
        ProfilerTestCase(
            # Provide a data smell configuration with default kwargs (no keys
            # contained in data smell specific kwargs dictionary). This
            # configuration is used for filtering (only use registered extreme
            # value smell and ignore the integer as floating point number smell).
            title="test_default_kwargs_filtering_dsc",
            dataset=pandas_dataset1,
            columns_by_column_type=expected_column_types_dataset1,
            registry=data_smell_registry_with_data_smell2,
            registered_data_smell_information=data_smell_registry_with_data_smell1_information,
            data_smell_configuration={
                DataSmellType.EXTREME_VALUE_SMELL: {}
            },
            # Ensure that exactly 4 expectations are generated.
            # DataSmellType.EXTREME_VALUE_SMELL for int and float columns (2 int
            #   and 2 float columns are present) => 4 expectations.
            # => 4 expectations in total if all expected combination and no
            #   additional expectation is generated.
            expected_nr_of_expectations=4
        )
    ]


# Generate testcases for profiling where a nonempty expectation suite should
# be generated. The data smell configuration is used for filtering of
# the present data smell types (e.g. only detect the specified data smell
# types). Custom kwargs are used. Tests generated by this fixture have the
# "test_custom_kwargs_" prefix.
@pytest.fixture
def profiler_testcases_custom_kwargs(
        pandas_dataset1,
        expected_column_types_dataset1,
        data_smell_registry_with_data_smell1_custom_kwargs_information,
        data_smell_registry_with_data_smell2_custom_kwargs_information,
        data_smell_registry_with_data_smell2_custom_kwargs) -> List[ProfilerTestCase]:
    return [
        ProfilerTestCase(
            # Generate
            title="test_custom_kwargs_no_filtering",
            dataset=pandas_dataset1,
            columns_by_column_type=expected_column_types_dataset1,
            registry=data_smell_registry_with_data_smell2_custom_kwargs,
            registered_data_smell_information=data_smell_registry_with_data_smell2_custom_kwargs_information,
            data_smell_configuration={
                DataSmellType.EXTREME_VALUE_SMELL: {
                    "threshold": 3
                },
                DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL: {
                    "mostly": 0.8
                }
            },
            # Ensure that exactly 6 expectations are generated.
            # DataSmellType.EXTREME_VALUE_SMELL for int and float columns (2 int
            #   and 2 float columns are present) => 4 expectations.
            # DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL for float columns
            #   => 2 expectations
            # => 6 expectations in total if all expected combination and no
            #   additional expectation is generated.
            expected_nr_of_expectations=6
        ),
        ProfilerTestCase(
            # Provide a data smell configuration with default kwargs (no keys
            # contained in data smell specific kwargs dictionary). This
            # configuration is used for filtering (only use registered extreme
            # value smell and ignore the integer as floating point number smell).
            title="test_custom_kwargs_filtering_dsc",
            dataset=pandas_dataset1,
            columns_by_column_type=expected_column_types_dataset1,
            registry=data_smell_registry_with_data_smell2_custom_kwargs,
            registered_data_smell_information=data_smell_registry_with_data_smell1_custom_kwargs_information,
            data_smell_configuration={
                DataSmellType.EXTREME_VALUE_SMELL: {
                    "threshold": 3
                }
            },
            # Ensure that exactly 4 expectations are generated.
            # DataSmellType.EXTREME_VALUE_SMELL for int and float columns (2 int
            #   and 2 float columns are present) => 4 expectations.
            # => 4 expectations in total if all expected combination and no
            #   additional expectation is generated.
            expected_nr_of_expectations=4
        )
    ]


@pytest.fixture
def profiler_testcases(
        profiler_testcases_empty_data_smell_configuration,
        profiler_testcases_empty_data_smell_registry,
        profiler_testcases_default_kwargs,
        profiler_testcases_custom_kwargs) -> List[ProfilerTestCase]:
    return profiler_testcases_empty_data_smell_configuration + \
        profiler_testcases_empty_data_smell_registry + \
        profiler_testcases_default_kwargs + \
        profiler_testcases_custom_kwargs


class TestDataSmellAwareProfiler:
    def test_profiler_testcases(self, profiler_testcases: List[ProfilerTestCase]):
        def process_testcase(testcase: ProfilerTestCase):
            profiler = DataSmellAwareProfiler()
            configuration = {
                "registry": testcase.registry,
                "data_smell_configuration": testcase.data_smell_configuration
            }

            expectation_suite, _ = profiler.profile(
                data_asset=testcase.dataset,
                profiler_configuration=configuration
            )
            assert isinstance(expectation_suite, ExpectationSuite)

            if testcase.expected_nr_of_expectations is not None:
                assert len(expectation_suite.expectations) == testcase.expected_nr_of_expectations

            if testcase.columns_by_column_type is not None:
                # Ensure that column type information is present in the
                # generated expectations suite.
                check_column_types_in_expectation_suite_meta_information(
                    suite=expectation_suite,
                    expected_column_types=testcase.columns_by_column_type
                )

            if testcase.registered_data_smell_information is not None and \
                    testcase.columns_by_column_type is not None:
                # Ensure that all combinations of data smells and the corresponding
                # column names are generated. For instance, an expectation for an
                # integer-specific smell should be generated for each integer
                # column in the profiled dataset.
                check_all_expectation_combinations_in_expectations_suite(
                    expectation_suite=expectation_suite,
                    data_smell_information=testcase.registered_data_smell_information,
                    expected_column_types=testcase.columns_by_column_type
                )

        for testcase in profiler_testcases:
            try:
                print(f"Executing testcase {testcase.title}")
                process_testcase(testcase)
            except AssertionError as e:
                raise AssertionError(f"During execution of testcase {testcase.title}: {e}")

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

        # Ensure that exactly 6 expectations are generated.
        # DataSmellType.EXTREME_VALUE_SMELL for int and float columns (2 int
        #   and 2 float columns are present) => 4 expectations.
        # DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL for float columns
        #   => 2 expectations
        # => 6 expectations in total if all expected combination and no
        #   additional expectation is generated.
        assert len(expectation_suite.expectations) == 6

        # Ensure that column type information is present in the
        # generated expectations suite.
        check_column_types_in_expectation_suite_meta_information(
            suite=expectation_suite,
            expected_column_types=expected_column_types_dataset1
        )

