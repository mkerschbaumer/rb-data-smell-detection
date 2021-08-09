import json
from typing import Optional

from datasmelldetection.core import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmell, DataSmellMetadata

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.profile.base import ProfilerDataType


class ExpectColumnValuesToNotContainIntegerAsStringSmell(ColumnMapExpectation, DataSmell):
    """
    Detect if an integer is stored as a string.

    The presence of an integer as string smell is checked by using regex
    matching. Currently no parameters are defined.

    Keyword Args:
        mostly:
            See the documentation regarding the `mostly` concept regarding
            expectations in Great Expectations.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.INTEGER_AS_STRING_SMELL,
        profiler_data_types={ProfilerDataType.STRING}
    )

    # NOTE: The examples are used to perform tests
    examples = [
        {
            "data": {
                # A column which contains floating point values. This column is
                # needed to ensure that integer as string detection does not
                # detect strings containing float values.
                "floats": ["0.0", "+3.14", "-5.3", "3.", "-5."],
                # A column to test spaces before an integer.
                "spaces_before": [" +1", " -3", " 5", " -4", " 0"],
                # A column to test spaces after an integer.
                "spaces_after": ["+1 ", "-3 ", "5 ", "-4 ", "0 "],
                # A column to ensure that integers mixed with words are not flagged.
                "integer_in_word": ["a3b", "abc d-2ef", "a0", "3d", "test abc 3d ef"],
                # Integer column 1: 60% of the column values are integers.
                # Test for empty string too.
                "integers_col1": ["abc", "-2", "5", "", "0"],
            },
            "tests": [
                {
                    # Ensure that floating point values as strings are not
                    # flagged as an integer as string smell.
                    "title": "test_floats",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "floats"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_spaces_before",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "spaces_before"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_spaces_after",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "spaces_after"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_integer_in_word",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "integer_in_word"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_integers_case1_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "integers_col1", "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["-2", "5", "0"],
                    },
                },
                {
                    # 60% of the column values are integers. Therefore 40% of
                    # the column values are not integers. The test should
                    # succeed since mostly is set to 0.4.
                    "title": "test_integers_case1_mostly0.4",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "integers_col1", "mostly": 0.4},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": ["-2", "5", "0"],
                    },
                },
            ],
        }
    ]

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

    map_metric = "column_values.not_match_regex"
    success_keys = (
        "mostly",
        "regex"
    )

    default_kwarg_values = {
        "catch_exceptions": True,
        "regex": r'^(?:\+|-)?\d+$',
        "mostly": 0.1
    }

    def validate_configuration(self, configuration: Optional[ExpectationConfiguration]):
        super().validate_configuration(configuration)
        assert configuration is not None
        assert "regex" not in configuration.kwargs, "regex cannot be altered"


expectation = ExpectColumnValuesToNotContainIntegerAsStringSmell()
expectation.register_data_smell()
del expectation
