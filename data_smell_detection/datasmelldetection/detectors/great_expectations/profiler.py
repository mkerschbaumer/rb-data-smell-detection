from typing import List, Dict

from great_expectations.core import ExpectationConfiguration
from great_expectations.profile.basic_dataset_profiler import BasicDatasetProfilerBase
from great_expectations.core.expectation_suite import ExpectationSuite

from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmellRegistry,
    default_registry
)


class DataSmellAwareProfiler(BasicDatasetProfilerBase):
    """
    A Great Expectations based profiler for data smell detection.

    The purpose of this class is to apply data smells registered at a
    :class:`~datasmelldetection.detectors.great_expectations.datasmell.DataSmellRegistry`
    to columns of the corresponding
    :class:`~datasmelldetection.core.datasmells.DataSmellType`. For instance,
    epectations for integer-specific data smells are generated for all integer
    columns.

    Currently the following keys are supported by the configuration:

    registry
        The
        :class:`~datasmelldetection.detectors.great_expectations.datasmell.DataSmellRegistry`
        to use. If this key does not exist or is None, then the default registry (
        :class:`~datasmelldetection.detectors.great_expectations.datasmell.default_registry`
        ) is used.
    """

    @classmethod
    def _profile(cls, dataset, configuration=None) -> ExpectationSuite:
        df = dataset

        # Expectations to evaluate later on
        expectation_suite = ExpectationSuite(
            expectation_suite_name="profiled_expectation_suite"
        )

        if configuration is None or \
                "registry" not in configuration or \
                not isinstance(configuration["registry"], DataSmellRegistry):
            registry: DataSmellRegistry = default_registry
        else:
            # Custom valid data smell registry provided
            registry = configuration["registry"]

        df.set_default_expectation_argument("catch_exceptions", True)
        df.set_config_value("interactive_evaluation", False)

        columns: List[str] = df.get_table_columns()

        # Store information about the column types (needed for analysis)
        meta_columns: Dict[str, Dict[str, str]] = {}
        for column in columns:
            meta_columns[column] = {}

        for column in columns:
            type_ = cls._get_column_type(df, column)

            meta_columns[column]["type"] = str(type_)

            # Parameters used to evaluate expectation later on.
            kwargs = {"column": column}
            expectation_dict = registry.get_smell_dict_for_profiler_data_type(type_)
            for expectation_type in expectation_dict.values():
                config = ExpectationConfiguration(
                    expectation_type=expectation_type, kwargs=kwargs
                )
                expectation_suite.add_expectation(config)

        # Add column type information to the expectation suite.
        expectation_suite.meta["columns"] = meta_columns

        return expectation_suite
