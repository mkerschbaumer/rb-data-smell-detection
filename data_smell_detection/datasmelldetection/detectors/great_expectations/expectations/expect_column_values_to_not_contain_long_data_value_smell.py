from typing import Optional, Iterable, Dict, Any, List
import re

from datasmelldetection.core import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import DataSmell, DataSmellMetadata

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.execution_engine import ExecutionEngine, PandasExecutionEngine
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.profile.base import ProfilerDataType
from great_expectations.validator.validation_graph import MetricConfiguration


_test_data = {
    # A column of length 5 which contains 3 strings of length >= 20
    # which should be flagged. 3 strings are contained with a length
    # < 20. No spaces before and after are added.
    "no_spaces": [
        "word",
        "Incomprehensibilities",  # 21 letters
        "Pneumonoultramicroscopicsilicovolcanoconiosis",  # 45 letters
        "",
        "Pseudopseudohypoparathyroidism",  # 30 letters
    ],
    # A column of length 5 which contains 3 strings of length >= 20
    # which should be flagged. 2 strings are contained with a length
    # < 20. One or multiple spaces are added before the long word to
    # flag.
    "spaces_before": [
        " word",
        "   Pneumonoultramicroscopicsilicovolcanoconiosis",  # 45 letters
        "  ",
        "   Incomprehensibilities",  # 21 letters
        " Pseudopseudohypoparathyroidism",  # 30 letters
    ],
    # A column of length 5 which contains 3 strings of length >= 20
    # which should be flagged. 2 strings are contained with a length
    # < 20. One or multiple spaces are added after the long word to
    # flag.
    "spaces_after": [
        "Pseudopseudohypoparathyroidism  ",  # 30 letters
        "word ",
        " ",
        "Incomprehensibilities  ",  # 21 letters
        "Pneumonoultramicroscopicsilicovolcanoconiosis   ",  # 45 letters
    ],
    # A column of length 5 which contains 3 strings of length >= 20
    # which should be flagged. 2 strings are contained with a length
    # < 20. One or multiple words are added before the long word to
    # flag.
    "words_before": [
        "A test word",
        "Unrelated words Pneumonoultramicroscopicsilicovolcanoconiosis",  # 45 letters
        "Testcase  ",
        "Another unrelated word Incomprehensibilities",  # 21 letters
        "Test Pseudopseudohypoparathyroidism",  # 30 letters
    ],
    # A column of length 5 which contains 3 strings of length >= 20
    # which should be flagged. 2 strings are contained with a length
    # < 20. One or multiple words are added after the long word to
    # flag.
    "words_after": [
        "Pseudopseudohypoparathyroidism unrelated words",  # 30 letters
        "word test",
        " short word",
        "Incomprehensibilities unrelated part",  # 21 letters
        "Pneumonoultramicroscopicsilicovolcanoconiosis testcase",  # 45 letters
    ],
    # A column of length 5 which contains 3 strings of length >= 20
    # which should be flagged. 2 strings are contained with a length
    # < 20. One or multiple words are added before and after the long word to
    # flag.
    "words_before_and_after": [
        "A test word Pseudopseudohypoparathyroidism unrelated words",  # 30 letters
        "Unrelated words word test",
        "Another unrelated word Incomprehensibilities unrelated part",  # 21 letters
        "Test Pneumonoultramicroscopicsilicovolcanoconiosis testcase",  # 45 letters
        "Testcase short word",
    ],
}


# Generate testcase for a column in `_test_data`. The testcases are padding
# related. For instance, the expected validation result should be similar even
# if padding is present (spaces, words before or after the word which causes
# the data smell). For example, the presence of the substring
# "Pseudopseudohypoparathyroidism" should trigger the data smell detection.
def _generate_per_column_testcases(column_name: str) -> List[Dict[str, Any]]:
    # Pass substrings of the testcases which should be detected. The actual
    # strings used in the testcases are extracted using this function.
    # The column name of the calling function is used.
    def _generate_unexpected_list(results_substrings: Iterable[str]) -> Iterable[str]:
        column = _test_data[column_name]
        result = []
        for substring in results_substrings:
            matching = [x for x in column if substring in x]
            assert len(matching) == 1
            result.append(matching[0])

        return result

    return [
        {
            # NOTE: Success is expected since the longest word in the
            # test column contains 45 characters. Since the threshold
            # is set to 50, no faulty elements are expected.
            "title": f"test_{column_name}_threshold_50",
            "exact_match_out": False,
            "include_in_gallery": True,
            "in": {
                "column": column_name,
                "length_threshold": 50
            },
            "out": {
                "success": True,
                "partial_unexpected_list": [],
            },
        },
        {
            # Only flag string values which contain words longer than 30
            # characters.
            "title": f"test_{column_name}_threshold_30_1_mostly",
            "exact_match_out": False,
            "include_in_gallery": True,
            "in": {
                "column": column_name,
                "length_threshold": 30
            },
            "out": {
                "success": False,
                "partial_unexpected_list": _generate_unexpected_list([
                    "Pneumonoultramicroscopicsilicovolcanoconiosis",  # 45 letters
                    "Pseudopseudohypoparathyroidism",  # 30 letters
                ]),
            },
        },
        {
            # Only flag string values which contain words longer than 30
            # characters. Success is expected since mostly is set to 40%
            # and only 2 out of 5 elements are faulty.
            "title": f"test_{column_name}_threshold_30_0.4_mostly",
            "exact_match_out": False,
            "include_in_gallery": True,
            "in": {
                "column": column_name,
                "length_threshold": 30,
                "mostly": 0.4
            },
            "out": {
                "success": True,
                "partial_unexpected_list": _generate_unexpected_list([
                    "Pneumonoultramicroscopicsilicovolcanoconiosis",  # 45 letters
                    "Pseudopseudohypoparathyroidism",  # 30 letters
                ]),
            },
        },
        {
            # Only flag string values which contain words longer than 20
            # characters.
            "title": f"test_{column_name}_threshold_20_1_mostly",
            "exact_match_out": False,
            "include_in_gallery": True,
            "in": {
                "column": column_name,
                "length_threshold": 20,
                "mostly": 1
            },
            "out": {
                "success": False,
                "partial_unexpected_list": _generate_unexpected_list([
                    "Incomprehensibilities",  # 21 letters
                    "Pneumonoultramicroscopicsilicovolcanoconiosis",  # 45 letters
                    "Pseudopseudohypoparathyroidism",  # 30 letters
                ]),
            },
        },
    ]


class ExpectColumnValuesToNotContainLongDataValueSmell(ColumnMapExpectation, DataSmell):
    """
    Detect if a long data value smell is present.

    The presence of a long data value smell is checked by searching for
    substrings consisting of word characters which are longer than a
    specific length threshold. If at least one word exceeding the
    length threshold is present then it is assumed that a long data
    value smell is present.

    Parameters:
        length_threshold: \
            The minimum number of characters a word must consist of to be
            considered "long". This parameter must be an integer greater than
            zero.

    Keyword Args:
        mostly:
            See the documentation regarding the `mostly` concept regarding
            expectations in Great Expectations.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.LONG_DATA_VALUE_SMELL,
        profiler_data_types={ProfilerDataType.STRING}
    )

    # NOTE: The examples are used to perform tests
    # NOTE: Some testcases were taken from
    # https://www.grammarly.com/blog/14-of-the-longest-words-in-english/.
    examples = [
        {
            "data": _test_data,
            "tests": _generate_per_column_testcases("no_spaces") + \
                _generate_per_column_testcases("spaces_before") + \
                _generate_per_column_testcases("spaces_after") + \
                _generate_per_column_testcases("words_before") + \
                _generate_per_column_testcases("words_after") + \
                _generate_per_column_testcases("words_before_and_after") + \
                [
                    # Remaining testcases which are not auto-generated
                     {
                         # Ensure that default parameters are used (mostly = 1
                         # and length_threshold = 30).
                         "title": f"test_no_spaces_default",
                         "exact_match_out": False,
                         "include_in_gallery": True,
                         "in": {
                             "column": "no_spaces",
                         },
                         "out": {
                             "success": False,
                             "partial_unexpected_list": [
                                 "Pneumonoultramicroscopicsilicovolcanoconiosis",  # 45 letters
                                 "Pseudopseudohypoparathyroidism",  # 30 letters
                             ],
                         },
                     },
                ]
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
    success_keys = ("length_threshold", "mostly")

    default_kwarg_values = {
        "length_threshold": 30,
        "mostly": 0.95
    }

    def get_validation_dependencies(
        self,
        configuration: Optional[ExpectationConfiguration] = None,
        execution_engine: Optional[ExecutionEngine] = None,
        runtime_configuration: Optional[dict] = None,
    ):
        dependencies = super(ExpectColumnValuesToNotContainLongDataValueSmell, self).get_validation_dependencies(
            configuration, execution_engine, runtime_configuration
        )

        # Get values for success kwargs (needed to ensure that default length
        # threshold value is used if it is not explicitly specified).
        success_kwargs = self.get_success_kwargs(configuration)

        pattern = re.compile(r"^column_values\.not_match_regex\.")
        length_threshold = success_kwargs["length_threshold"]
        regex: str = r"\w{" + str(length_threshold) + r",}"

        # Override regex for internally used metric
        # (column_values.not_match_regex). This is required since the regex is
        # constructed above using the length threshold parameter.
        for metric_name, metric_configuration_ in dependencies["metrics"].items():
            if pattern.search(metric_name):
                assert isinstance(metric_configuration_, MetricConfiguration)
                metric_configuration: MetricConfiguration = metric_configuration_
                metric_configuration.metric_value_kwargs["regex"] = regex

        return dependencies


expectation = ExpectColumnValuesToNotContainLongDataValueSmell()
expectation.register_data_smell()
del expectation
