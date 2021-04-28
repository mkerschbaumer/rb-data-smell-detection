from typing import List, Dict, Set, Any

from copy import deepcopy
from datasmelldetection.core import DataSmellType
from great_expectations.core import ExpectationConfiguration
from great_expectations.profile.basic_dataset_profiler import BasicDatasetProfilerBase
from great_expectations.core.expectation_suite import ExpectationSuite

from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmellRegistry,
    default_registry
)


# Create a configuration dictionary for data smells. The registry is used to
# get the data smell types of all registered data smells. An empty configuration
# dictionary is created for each registered data smell.
def _create_data_smell_configuration_dict(registry: DataSmellRegistry) \
        -> Dict[DataSmellType, Dict[str, Any]]:
    registered_data_smells: Set[DataSmellType] = registry.get_registered_data_smells()

    result: Dict[DataSmellType, Dict[str, Any]] = dict()
    for data_smell_type in registered_data_smells:
        result[data_smell_type] = dict()

    return result


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

    data_smell_configuration:
        A dictionary of type Dict[DataSmellType, Dict[str, Any]]. It stores
        kwargs for an expectation class which detects a specific
        :class:`~datasmelldetection.detectors.core.datasmells.DataSmellType`.
        If this configuration key is provided, only data smells are considered
        which are explicitly specified as keys. The corresponding dictionary
        values (for a specific
        :class:`~datasmelldetection.detectors.core.datasmells.DataSmellType`)
        are used as kwargs. If this configuration key is not provided it is
        assumed that no data-smell specific kwargs should be used. In this case
        all data smells are used which are registered in the corresponding
        data smell registry. The data smell configuration dictionary can also
        be used to restrict data smell detection to specific data smell types.
        This can be achieved by providing a data smell configuration dictionary
        which only contains the relevant data smells. Data smells which are
        not registered in the provided data smell registry may be provided but
        are ignored.
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

        # Kwargs to use for each data smell type.
        if configuration is None or \
                "data_smell_configuration" not in configuration or \
                not isinstance(configuration["data_smell_configuration"], dict):
            data_smell_configuration: Dict[DataSmellType, Dict[str, Any]] = _create_data_smell_configuration_dict(registry)
        else:
            data_smell_configuration = configuration["data_smell_configuration"]

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
            expectation_dict = registry.get_smell_dict_for_profiler_data_type(type_)
            for data_smell_type, expectation_type in expectation_dict.items():
                if data_smell_type not in data_smell_configuration:
                    # Data smell type should not be considered
                    continue

                # Use provided kwargs for the corresponding data smell type
                kwargs: Dict[str, Any] = deepcopy(data_smell_configuration[data_smell_type])
                kwargs["column"] = column

                config = ExpectationConfiguration(
                    expectation_type=expectation_type, kwargs=kwargs
                )
                expectation_suite.add_expectation(config)

        # Add column type information to the expectation suite.
        expectation_suite.meta["columns"] = meta_columns

        return expectation_suite
