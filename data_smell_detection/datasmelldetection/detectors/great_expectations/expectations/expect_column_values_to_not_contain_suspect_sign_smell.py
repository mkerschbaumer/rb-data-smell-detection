import json

from typing import Optional

from great_expectations.execution_engine import (
    PandasExecutionEngine,
    ExecutionEngine,
)
from great_expectations.expectations.expectation import (
    ColumnMapExpectation,
    ExpectationConfiguration,
)
from great_expectations.expectations.metrics import (
    ColumnMapMetricProvider,
    column_condition_partial,
)
from great_expectations.profile.base import ProfilerDataType
from great_expectations.validator.validation_graph import MetricConfiguration


from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmell, DataSmellMetadata


class ColumnValuesDontContainSuspectSignSmell(ColumnMapMetricProvider):
    condition_metric_name = "column_values.custom.not_contains_suspect_sign_smell"
    condition_value_keys = ("percentile_threshold",)

    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, _metrics, **kwargs):
        quantiles = _metrics.get("column.quantile_values")
        if quantiles[0] >= 0:
            # The majority of the values are positive => return True for positive values
            # to flag negative values
            return column >= 0
        elif quantiles[1] <= 0:
            # The majority of the values are negative => return True for negative values
            # to flag positive values
            return column <= 0
        else:
            # Suspect sign smell not present
            return column.map(lambda x: True)

    @classmethod
    def _get_evaluation_dependencies(
            cls,
            metric: MetricConfiguration,
            configuration: Optional[ExpectationConfiguration] = None,
            execution_engine: Optional[ExecutionEngine] = None,
            runtime_configuration: Optional[dict] = None,
    ):
        """Returns a dictionary of given metric names and their corresponding configuration, specifying the metric
        types and their respective domains"""
        dependencies: dict = super()._get_evaluation_dependencies(
            metric=metric,
            configuration=configuration,
            execution_engine=execution_engine,
            runtime_configuration=runtime_configuration,
        )

        percentile_threshold = metric.metric_value_kwargs["percentile_threshold"]

        dependencies["column.quantile_values"] = MetricConfiguration(
            metric_name="column.quantile_values",
            metric_domain_kwargs=metric.metric_domain_kwargs,
            metric_value_kwargs={
                "quantiles": [percentile_threshold, 1 - percentile_threshold],
                "allow_relative_error": "linear"
            }
        )

        return dependencies


class ExpectColumnValuesToNotContainSuspectSignSmell(ColumnMapExpectation, DataSmell):
    """
    Detect if a suspect sign smell is present.

    The presence of a suspect sign smell is checked by comparing the column
    values to quantile values. The `percentile_threshold` parameter controls
    which quantiles are computed. If `percentile_threshold` is set to 0.25
    then the 0.25 quantile and the 1 - 0.25 = 0.75 quantiles are computed.

    First, it is checked whether the lower computed quantile is positive.
    If that is the case, then the majority of the column values are positive.
    In this case, negative values are assumed to be faulty.

    If the first condition didn't match it is checked whether the second
    computed quantile is negative. In this case the majority of the column
    values are negative. Therefore, positive values are assumed to be faulty.

    Parameters:
        percentile_threshold: \
            This parameter must be in the interval [0,1]. It controls which
            quantiles are computed. The computed quantiles are used to
            determine whether the majority of the column values are positive
            or negative.

    Keyword Args:
        mostly:
            See the documentation regarding the `mostly` concept regarding
            expectations in Great Expectations.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.SUSPECT_SIGN_SMELL,
        profiler_data_types={ProfilerDataType.INT, ProfilerDataType.FLOAT, ProfilerDataType.NUMERIC}
    )

    # NOTE: The examples are used to perform tests
    examples = [
        {
            "data": {
                # Only one negative number. Most of the entries are positive
                "mostly_positive1": [-1, 0, 1, 2, 3, 4, 5, 6, 8, 9],
                # Two negative numbers. Most of the entries are positive
                "mostly_positive2": [-2, -1, 0, 1, 2, 3, 4, 5, 6, 8],
                # Only one positive number. Most of the entries are negative
                "mostly_negative1": [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1],
                # Two positive numbers. Most of the entries are negative
                "mostly_negative2": [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2],
                "all_negative": [-9, -8, -7, -6, -5, -4, -3, -2, -1, 0],
                "all_positive": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            },
            "tests": [
                {
                    "title": "test_mostly_positive_with_one_negative_number_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_positive1", "mostly": 1, "percentile_threshold": 0.25},
                    "out": {
                        "success": False,
                        # "unexpected_index_list": [0],
                        "partial_unexpected_list": [-1],
                    },
                },
                {
                    "title": "test_mostly_positive_with_one_negative_number_mostly_0.8",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_positive1", "mostly": 0.8, "percentile_threshold": 0.25},
                    "out": {
                        "success": True,
                        # "unexpected_index_list": [0],
                        "partial_unexpected_list": [-1],
                    },
                },
                {
                    "title": "test_mostly_positive_with_two_negative_numbers_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_positive2", "mostly": 1, "percentile_threshold": 0.25},
                    "out": {
                        "success": False,
                        # "unexpected_index_list": [0, 1],
                        "partial_unexpected_list": [-1, -2],
                    },
                },
                {
                    "title": "test_mostly_positive_with_two_negative_numbers_mostly_0.8",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_positive2", "mostly": 0.8, "percentile_threshold": 0.25},
                    "out": {
                        "success": True,
                        # "unexpected_index_list": [0, 1],
                        "partial_unexpected_list": [-1, -2],
                    },
                },
                {
                    "title": "test_mostly_positive_with_one_positive_number_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_negative1", "mostly": 1, "percentile_threshold": 0.25},
                    "out": {
                        "success": False,
                        # "unexpected_index_list": [9],
                        "partial_unexpected_list": [1],
                    },
                },
                {
                    "title": "test_mostly_positive_with_one_positive_number_mostly_0.8",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_negative1", "mostly": 0.8, "percentile_threshold": 0.25},
                    "out": {
                        "success": True,
                        # "unexpected_index_list": [9],
                        "partial_unexpected_list": [1],
                    },
                },
                {
                    "title": "test_mostly_positive_with_two_positive_numbers_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_negative2", "mostly": 1, "percentile_threshold": 0.25},
                    "out": {
                        "success": False,
                        # "unexpected_index_list": [8, 9],
                        "partial_unexpected_list": [1, 2],
                    },
                },
                {
                    "title": "test_mostly_positive_with_two_positive_numbers_mostly_0.8",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mostly_negative2", "mostly": 0.8, "percentile_threshold": 0.25},
                    "out": {
                        "success": True,
                        # "unexpected_index_list": [8, 9],
                        "partial_unexpected_list": [1, 2],
                    },
                },
                {
                    "title": "test_all_positive",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "all_positive", "mostly": 1, "percentile_threshold": 0.25},
                    "out": {
                        "success": True,
                        # "unexpected_index_list": [],
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_all_negative",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "all_negative", "mostly": 1, "percentile_threshold": 0.25},
                    "out": {
                        "success": True,
                        # "unexpected_index_list": [],
                        "partial_unexpected_list": [],
                    },
                }
            ],
        }
    ]

    # This dictionary contains metadata for display in the public gallery
    library_metadata = {
        "maturity": "experimental",
        "tags": [
            "experimental"
        ],
        "contributors": [
            "@mkerschbaumer",
        ],
        "package": "experimental_expectations",
    }

    map_metric = "column_values.custom.not_contains_suspect_sign_smell"

    # for more information about domain and success keys, and other arguments to Expectations
    success_keys = ("mostly", "percentile_threshold")

    default_kwarg_values = {
        "percentile_threshold": 0.25,
        "mostly": 0.95
    }


expectation = ExpectColumnValuesToNotContainSuspectSignSmell()
expectation.register_data_smell()
del expectation
