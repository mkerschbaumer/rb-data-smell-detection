from typing import Optional

from datasmelldetection.core import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmell, DataSmellMetadata

from great_expectations.core import ExpectationConfiguration
from great_expectations.profile.base import ProfilerDataType

from great_expectations.expectations.expectation import ColumnMapExpectation


class ExpectColumnValuesToNotContainExtremeValueSmell(ColumnMapExpectation, DataSmell):
    """
    Detect the presence of an extreme value smell (outliers).

    This expectation internally uses the "column_values.z_score.under_threshold"
    metric which is also be used by the
    "expect_column_value_z_scores_to_be_less_than" expectation. By default,
    double-sided checking is performed.
    
    
    Parameters:
        threshold: \
            The threshold to use regarding the z-score. This parameter can be
            configured by users but is set to 3 by default. It is assumed that
            this parameter is a positive number.

    Keyword Args:
        mostly:
            See the documentation regarding the `mostly` concept regarding
            expectations in Great Expectations.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
        profiler_data_types={ProfilerDataType.INT, ProfilerDataType.FLOAT, ProfilerDataType.NUMERIC}
    )

    map_metric = "column_values.z_score.under_threshold"
    success_keys = (
        "mostly",
        "threshold",
        "double_sided"
    )

    default_kwarg_values = {
        "threshold": 3,
        "double_sided": True,
        "catch_exceptions": True
    }

    def validate_configuration(self, configuration: Optional[ExpectationConfiguration]):
        super().validate_configuration(configuration)
        assert configuration is not None
        assert "double_sided" not in configuration.kwargs, "double_sided cannot be altered"
        if "threshold" in configuration.kwargs:
            threshold = configuration.kwargs["threshold"]
            assert threshold > 0, "Threshold must be a positive integer."


expectation = ExpectColumnValuesToNotContainExtremeValueSmell()
expectation.register_data_smell()
del expectation
