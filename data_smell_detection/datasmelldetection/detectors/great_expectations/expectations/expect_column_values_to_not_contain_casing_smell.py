from typing import List, Dict, Any

from great_expectations.execution_engine import PandasExecutionEngine
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.expectations.metrics import (
    ColumnMapMetricProvider,
    column_condition_partial,
)
from great_expectations.profile.base import ProfilerDataType
import re

from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmell,
    DataSmellMetadata
)


class ColumnValuesDontContainCasingSmell(ColumnMapMetricProvider):
    condition_metric_name = "column_values.custom.not_contains_casing_smell"
    condition_value_keys = ("same_case_wordcount_threshold", )

    @classmethod
    def _contains_casing_smell(cls, element: str, same_case_wordcount_threshold: int) -> bool:
        # Extract substrings of the input string by splitting on spaces
        word_candidates: List[str] = re.split(r"\s+", element)

        words: List[str] = list()
        for word in word_candidates:
            # Find consecutive alphabetical characters. Require matching to
            # start at the begin of a string to consider cases like
            # "word." where only "word" should be extracted.
            substrings = list(re.findall(r"^[a-zA-Z]+", word))
            words = words + substrings

        word_count: int = len(words)

        # Case 1: Function for testing if all words are in lowercase
        # (e.g. "abc def ghi")
        def is_all_lower_case(word: str) -> bool:
            return word.lower() == word

        # Case 1: Function for testing if all words are in uppercase
        # (e.g. "ABC DEF GHI")
        def is_all_upper_case(word: str) -> bool:
            return word.upper() == word

        is_all_words_lowercase: bool = all(map(is_all_lower_case, words))
        is_all_words_uppercase: bool = all(map(is_all_upper_case, words))

        # At least `same_case_wordcount_threshold` lowercase or uppercase words
        # have to be present to flag a casing smell. This is required since
        # strings like "abc" should not be flagged.
        #
        # NOTE: Only consider a Casing Smell to be present if all words are
        # lower case or all are upper case. This is done to avoid that
        # inputs like "A test string" are not flagged.
        if word_count >= same_case_wordcount_threshold and \
                (is_all_words_lowercase or is_all_words_uppercase):
            return True

        # Case 2: Some words are in mixed case (e.g. "AbC dEf gHI")
        def is_mixed_case(x: str) -> bool:
            # e.g. "AbC" or "AbcDef"
            regex_case1 = r"[A-Z]+[a-z]+[A-Z]+.*"
            # e.g. "aBC" or "abCdefGHI"
            regex_case2 = r"[a-z]+[A-Z]+.*"
            regex = f"^({regex_case1}|{regex_case2})$"
            return bool(re.match(regex, x))
        return any(map(is_mixed_case, words))

    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, _metrics, same_case_wordcount_threshold: int, **kwargs):
        # Negate the result of _contains_casing_smell since Great Expectations
        # assumes that False is returned if a value is faulty
        # (a data smell is present).
        def not_contains_casing_smell(element: str) -> bool:
            return not cls._contains_casing_smell(element, same_case_wordcount_threshold)
        return column.map(not_contains_casing_smell)


class ExpectColumnValuesToNotContainCasingSmell(ColumnMapExpectation, DataSmell):
    """
    Detect the presence of a Casing Smell.

    The detection of a Casing Smell is performed for string columns. Words contained in a
    row are analyzed to estimate whether a data smell is present. Two cases are considered.
    In the first case the data smell is assumed to be present if all words are of the same
    case (either all lowercase or all uppercase). The data smell detection process for
    this case can be customized using the `same_case_wordcount_threshold` parameter described
    below. The second case concerns the situation where
    at least one word in the string contains unusual mixed casing patterns. The first mixed
    case pattern which is searched is the situation where the word begins with a lowercase
    character and contains an uppercase character (e.g. ”wOrd” or ”worD”). The second
    mixed case pattern describes the situation where a string begins with an uppercase
    character, contains at least one following lowercase character followed by an uppercase
    character (e.g. ”WoRd” or ”WorD”).


    Parameters:
        same_case_wordcount_threshold: \
            This parameter controls how many words must be contained in a string for a
            casing smell, where all words are of the same case, to exist. For instance, strings like
            ”all lowercase” or ”ALL UPPERCASE” with `same_case_wordcount_threshold = 2` would
            trigger this case while ”string” would not.

    Keyword Args:
        mostly:
            See the documentation regarding the `mostly` concept regarding
            expectations in Great Expectations.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.CASING_SMELL,
        profiler_data_types={ProfilerDataType.STRING}
    )

    # NOTE: The examples are used to perform tests
    examples = [
        {
            "data": {
                # NOTE: Empty string should not be flagged as faulty
                "lowercase_only": ["abc", "abc def", "abc def ghi", "abc def ghi jkl", ""],
                "uppercase_only": ["ABC", "ABC DEF", "ABC DEF GHI", "ABC DEF GHI JKL", "Unrelated"],
                "mixed_case_only": ["Abc dE", "AbC", "AbcDe", "abc dEf ghi", "Unrelated"],
                "sentences": [
                    "This is an example sentence.",  # no data smell expected
                    "This is an eXample sentence.",  # data smell expected (mixed case)
                    "This is an ExamPle sentence.",  # data smell expected (mixed case)
                    "this is an example sentence.",  # data smell expected (lowercase only)
                    "THIS IS AN EXAMPLE SENTENCE.",  # data smell expected (uppercase only)
                ],
                # Strings which should not trigger a Casing Smell
                "negative": [
                    "-1",  # Integers
                    "5",
                    "2.5",  # Floats
                    "-3.8",
                    ""  # Empty string
                ],
                # Strings which should not trigger a Casing Smell
                "negative2": [
                    # All words are either all lowercase or all uppercase
                    # => Should still not be flagged.
                    "A test sentence which should not be flagged.",
                    "www.google.de",  # All lowercase but may not be seen as a data smell
                    "WWW.GOOGLE.DE",  # All uppercase but may not be seen as a data smell
                    "www.gOogle.de",  # Mixed but may not be seen as a data smell
                    "www.GooGle.de"   # Mixed but may not be seen as a data smell
                ],
            },
            "tests": [
                {
                    "title": "test_lowercase_only_wordcount1_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "lowercase_only", "same_case_wordcount_threshold": 1, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["abc", "abc def", "abc def ghi", "abc def ghi jkl"],
                    },
                },
                {
                    "title": "test_lowercase_only_wordcount2_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "lowercase_only", "same_case_wordcount_threshold": 2, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["abc def", "abc def ghi", "abc def ghi jkl"],
                    },
                },
                {
                    "title": "test_lowercase_only_wordcount3_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "lowercase_only", "same_case_wordcount_threshold": 3, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["abc def ghi", "abc def ghi jkl"],
                    },
                },
                {
                    "title": "test_lowercase_only_wordcount3_mostly0.6",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "lowercase_only", "same_case_wordcount_threshold": 3, "mostly": 0.6},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": ["abc def ghi", "abc def ghi jkl"],
                    },
                },
                {
                    "title": "test_uppercase_only_wordcount1_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "uppercase_only", "same_case_wordcount_threshold": 1, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["ABC", "ABC DEF", "ABC DEF GHI", "ABC DEF GHI JKL"],
                    },
                },
                {
                    "title": "test_uppercase_only_wordcount2_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "uppercase_only", "same_case_wordcount_threshold": 2, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["ABC DEF", "ABC DEF GHI", "ABC DEF GHI JKL"],
                    },
                },
                {
                    "title": "test_uppercase_only_wordcount3_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "uppercase_only", "same_case_wordcount_threshold": 3, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["ABC DEF GHI", "ABC DEF GHI JKL"],
                    },
                },
                {
                    "title": "test_uppercase_only_wordcount3_mostly0.6",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "uppercase_only", "same_case_wordcount_threshold": 3, "mostly": 0.6},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": ["ABC DEF GHI", "ABC DEF GHI JKL"],
                    },
                },
                {
                    # NOTE: The value of same_case_wordcount_threshold does not matter
                    # in this case (only relevant for testing the cases with lowercase only
                    # and uppercase only).
                    "title": "test_mixed_case_only_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mixed_case_only", "same_case_wordcount_threshold": 3, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": ["Abc dE", "AbC", "AbcDe", "abc dEf ghi"],
                    },
                },
                {
                    # NOTE: The value of same_case_wordcount_threshold does not matter
                    # in this case (only relevant for testing the cases with lowercase only
                    # and uppercase only).
                    "title": "test_mixed_case_only_mostly0.2",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mixed_case_only", "same_case_wordcount_threshold": 3, "mostly": 0.2},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": ["Abc dE", "AbC", "AbcDe", "abc dEf ghi"],
                    },
                },
                {
                    "title": "test_sentences_wordcount2_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "sentences", "same_case_wordcount_threshold": 2, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": [
                            "This is an eXample sentence.",  # mixed case
                            "This is an ExamPle sentence.",  # mixed case
                            "this is an example sentence.",  # lowercase only
                            "THIS IS AN EXAMPLE SENTENCE.",  # uppercase only
                        ],
                    },
                },
                {
                    "title": "test_sentences_wordcount5_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    # NOTE: Sentence has exactly 5 words
                    "in": {"column": "sentences", "same_case_wordcount_threshold": 5, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": [
                            "This is an eXample sentence.",  # mixed case
                            "This is an ExamPle sentence.",  # mixed case
                            "this is an example sentence.",  # lowercase only
                            "THIS IS AN EXAMPLE SENTENCE.",  # uppercase only
                        ],
                    },
                },
                {
                    "title": "test_sentences_wordcount6_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    # Same case should not be triggered (sentence has 5 words, threshold set
                    # to 6 words).
                    "in": {"column": "sentences", "same_case_wordcount_threshold": 6, "mostly": 1},
                    "out": {
                        "success": False,
                        "partial_unexpected_list": [
                            "This is an eXample sentence.",  # mixed case
                            "This is an ExamPle sentence.",  # mixed case
                        ],
                    },
                },
                {
                    "title": "test_sentences_wordcount6_mostly0.6",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    # Same case should not be triggered (sentence has 5 words, threshold set
                    # to 6 words).
                    "in": {"column": "sentences", "same_case_wordcount_threshold": 6, "mostly": 0.6},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [
                            "This is an eXample sentence.",  # mixed case
                            "This is an ExamPle sentence.",  # mixed case
                        ],
                    },
                },
                {
                    # Ensure no Casing Smell is detected for strings in the
                    # "negative" column.
                    "title": "test_negative_wordcount1_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "negative", "same_case_wordcount_threshold": 1, "mostly": 1},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": [],
                    },
                },
                {
                    # Ensure no Casing Smell is detected for strings in the
                    # "negative2" column.
                    "title": "test_negative2_wordcount2_mostly1",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "negative2", "same_case_wordcount_threshold": 2, "mostly": 1},
                    "out": {
                        "success": True,
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

    map_metric = "column_values.custom.not_contains_casing_smell"

    success_keys = ("mostly", "same_case_wordcount_threshold")

    default_kwarg_values: Dict[str, Any] = {
        "same_case_wordcount_threshold": 2
    }


expectation = ExpectColumnValuesToNotContainCasingSmell()
expectation.register_data_smell()
del expectation
