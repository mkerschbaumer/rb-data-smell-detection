from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmell, DataSmellMetadata
from great_expectations.execution_engine import (
    PandasExecutionEngine,
)
from great_expectations.expectations.expectation import (
    ColumnMapExpectation,
)
from great_expectations.expectations.metrics import (
    ColumnMapMetricProvider,
    column_condition_partial,
)
from great_expectations.profile.base import ProfilerDataType


class ColumnValuesDontContainIntegerAsFloatingPointNumberSmell(ColumnMapMetricProvider):
    condition_metric_name = "column_values.custom.not_contains_integer_as_floating_point_number_smell"
    condition_value_keys = ("epsilon",)

    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, epsilon, **kwargs):
        # Round to nearest integer to estimate the presence of an integer as
        # floating point number smell.
        return (column - column.round(decimals=0)).abs() > epsilon


class ExpectColumnValuesToNotContainIntegerAsFloatingPointNumberSmell(ColumnMapExpectation, DataSmell):
    """
    Detect if an integer as floating point number smell is present.

    The presence of a suspect sign smell is checked by computing the absolute
    difference between a floating point number and the nearest integer. The
    nearest integer is estimated by rounding. It is assumed that an element
    (row) contains an integer as floating point number smell if the described
    absolute difference is below a specific threshold (epsilon).

    Parameters:
        epsilon: \
            The threshold for the absolute difference of a floating point
            number. to the nearest integer. This parameter must be a
            floating point value greater than zero.

    Keyword Args:
        mostly:
            See the documentation regarding the `mostly` concept regarding
            expectations in Great Expectations.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL,
        profiler_data_types={ProfilerDataType.FLOAT}
    )

    # Testcases
    examples = [
        {
            "data": {
                # A column of length 10. Only floating point numbers with
                # exactly the difference of 0.1 and 0.2 to the next
                # integer are contained.
                "distance0.1and0.2": [-5.8, -5.9, -0.2, -0.1, 0.1, 0.2, 7.8, 7.9, 8.1, 8.2],
            },
            "tests": [
                {
                    # All values in the column should contain the data smell
                    # since all values have a difference < eps to the nearest
                    # integer value.
                    "title": "test_distance0.1and0.2_eps_0.5_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "distance0.1and0.2", "mostly": 1, "epsilon": 0.5},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": [
                            -5.8, -5.9, -0.2, -0.1, 0.1, 0.2, 7.8, 7.9, 8.1, 8.2
                        ],
                    },
                },
                {
                    # All values in the column should contain the data smell
                    # since all values have a difference < eps to the nearest
                    # integer value.
                    "title": "test_distance0.1and0.2_eps_0.25_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "distance0.1and0.2", "mostly": 1, "epsilon": 0.25},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": [
                            -5.8, -5.9, -0.2, -0.1, 0.1, 0.2, 7.8, 7.9, 8.1, 8.2
                        ],
                    },
                },
                {
                    # Values in the column which have a difference < eps to the
                    # nearest integer value should contain the data smell.
                    # 5 out of 10 elements are faulty.
                    "title": "test_distance0.1and0.2_eps_0.15_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "distance0.1and0.2", "mostly": 1, "epsilon": 0.15},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": [-5.9, -0.1, 0.1, 7.9, 8.1],
                    },
                },
                {
                    # Values in the column which have a difference < eps to the
                    # nearest integer value should contain the data smell.
                    # 5 out of 10 elements are faulty. Since mostly is set to
                    # 0.4 no data smell should be flagged (success is set to
                    # True).
                    "title": "test_distance0.1and0.2_eps_0.15_mostly_0.4",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "distance0.1and0.2", "mostly": 0.4, "epsilon": 0.15},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [-5.9, -0.1, 0.1, 7.9, 8.1],
                    },
                },
                {
                    # Values in the column which have a difference < eps to the
                    # nearest integer value should contain the data smell.
                    # 5 out of 10 elements are faulty. Since mostly is set to
                    # 0.5 no data smell should be flagged (success is set to
                    # True).
                    "title": "test_distance0.1and0.2_eps_0.15_mostly_0.5",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "distance0.1and0.2", "mostly": 0.5, "epsilon": 0.15},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [-5.9, -0.1, 0.1, 7.9, 8.1],
                    },
                },
                {
                    # Values in the column which have a difference < eps to the
                    # nearest integer value should contain the data smell.
                    # No elements should be flagged.
                    "title": "test_distance0.1and0.2_eps_0.05_mostly_1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "distance0.1and0.2", "mostly": 1, "epsilon": 0.05},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
            ],
        }
    ]

    # This dictionary contains metadata for display in the public gallery
    library_metadata = {
        "maturity": "experimental",
        "tags": [],
        "contributors": [  # Github handles for all contributors to this Expectation.
            "@mkerschbaumer", # Don't forget to add your github handle here!
        ],
        "package": "experimental_expectations",
    }

    map_metric = "column_values.custom.not_contains_integer_as_floating_point_number_smell"

    success_keys = ("mostly", "epsilon")

    default_kwarg_values = {
        "epsilon": 1e-6,
        "mostly": 0.1
    }


expectation = ExpectColumnValuesToNotContainIntegerAsFloatingPointNumberSmell()
expectation.register_data_smell()
