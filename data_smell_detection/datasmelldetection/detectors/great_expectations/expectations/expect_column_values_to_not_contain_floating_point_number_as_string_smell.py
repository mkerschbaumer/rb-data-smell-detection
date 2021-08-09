from typing import Optional

from datasmelldetection.core import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmell, DataSmellMetadata

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.profile.base import ProfilerDataType


class ExpectColumnValuesToNotContainFloatingPointNumberAsStringSmell(ColumnMapExpectation,
                                                                    DataSmell):
    """
    Detect if a floating point value is stored as a string.

    Internally the presence of the floating point value as string smell is
    checked by using regex matching. Currently no parameters are defined.

    Keyword Args:
        mostly:
            See the documentation regarding the `mostly` concept regarding
            expectations in Great Expectations.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL,
        profiler_data_types={ProfilerDataType.STRING}
    )

    # NOTE: The examples are used to perform tests
    examples = [
        {
            "data": {
                # A column which contains integer values. This column is
                # needed to ensure that floating point number as string
                # detection does not detect strings containing integer
                # values.
                "integers": ["0", "+3", "-5", "4", "-8"],
                # Columns which contain floating point values. These columns are
                # needed to ensure that floating point number as string
                # detection does detect strings containing float values.
                # The "short" suffix in the following tests denotes floating
                # point numbers like "3.0" which are stored as "3.".
                # The "long" suffix denotes floating point numbers like "3.0".
                "floats_short": ["0.", "+3.", "-5.", "3.", "-8."],
                "floats_long": ["0.0", "+3.14", "-5.3", "3.14", "-5.7"],
                # Columns to ensure that the "point character" is '.'.
                # The regex which is currently used for floating point number
                # as string detection contains "\." for matching the dot.
                # Ensure escaping of the dot inside the regex is performed by
                # testing that "3,5" or "-3," do not match the regex.
                "wrong_point_character_short": ["0,", "+3,", "-5,", "3,", "-8,"],
                "wrong_point_character_long": ["0,0", "+3,14", "-5,3", "3,14", "-5,7"],
                # Columns to test spaces before a floating point number.
                "spaces_before_short": [" 0.", " +3.", " -5.", " 3.", " -8."],
                "spaces_before_long": [" 0.0", " +3.14", " -5.3", " 3.14", " -5.7"],
                # Columns to test spaces after a floating point number.
                "spaces_after_short": ["0. ", "+3. ", "-5. ", "3. ", "-8. "],
                "spaces_after_long": ["0.0 ", "+3.14 ", "-5.3 ", "3.14 ", "-5.7 "],
                # Columns to ensure that floating point numbers mixed with
                # words are not flagged.
                "in_word_short": ["a3.b", "abc d-2.ef", "a0.", "3.d", "test abc 3.d ef"],
                "in_word_long": ["a3.14b", "abc d-2.84ef", "a0.0", "3.3d", "test abc 3.14d ef"],
                # Floating point number column 1: 60% of the column values are
                # floating point values. Test for empty string too.
                "floats_col1": ["abc", "-2.", "5.8", "", "0.0"],
            },
            "tests": [
                {
                    # Ensure that integer values as strings are not flagged as
                    # a floating point number as string smell.
                    "title": "test_integers",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "integers"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_spaces_before_short",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "spaces_before_short"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_spaces_before_long",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "spaces_before_long"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_wrong_point_character_short",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "wrong_point_character_short"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_wrong_point_character_long",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "wrong_point_character_long"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_spaces_after_short",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "spaces_after_short"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_spaces_after_long",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "spaces_after_long"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_in_word_short",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "in_word_short"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_in_word_long",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "in_word_long"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    "title": "test_floats_short",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "floats_short", "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["0.", "+3.", "-5.", "3.", "-8."],
                    },
                },
                {
                    "title": "test_floats_long",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "floats_long", "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["0.0", "+3.14", "-5.3", "3.14", "-5.7"],
                    },
                },
                {
                    # Floating point numbers as strings in a column with
                    # non-floating point numbers.
                    "title": "test_floats_case1_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "floats_col1", "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["-2.", "5.8", "0.0"],
                    },
                },
                {
                    # 60% of the column values are floating point numbers.
                    # Therefore 40% of the column values are not floating point
                    # numbers. The test should succeed since mostly is set to
                    # 0.4.
                    "title": "test_floats_case1_mostly0.4",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "floats_col1", "mostly": 0.4},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": ["-2.", "5.8", "0.0"],
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
        "regex": r'^(?:\+|-)?\d+\.\d*$',
        "mostly": 0.1
    }

    def validate_configuration(self, configuration: Optional[ExpectationConfiguration]):
        super().validate_configuration(configuration)
        assert configuration is not None
        assert "regex" not in configuration.kwargs, "regex cannot be altered"


expectation = ExpectColumnValuesToNotContainFloatingPointNumberAsStringSmell()
expectation.register_data_smell()
del expectation
