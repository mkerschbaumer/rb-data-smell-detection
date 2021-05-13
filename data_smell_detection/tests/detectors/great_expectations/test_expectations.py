# Check whether the expectations which implement data smell detection work as intended.
# "Examples" are executed to test the behaviour.
from typing import List
from great_expectations.expectations.expectation import Expectation

from datasmelldetection.detectors.great_expectations.expectations import (
    ExpectColumnValuesToNotContainSuspectSignSmell,
    ExpectColumnValuesToNotContainIntegerAsStringSmell,
    ExpectColumnValuesToNotContainFloatingPointNumberAsStringSmell,
    ExpectColumnValuesToNotContainLongDataValueSmell,
)

from .helper_functions import check_expectation_examples


class TestExpectations:
    expectations_to_test: List[Expectation] = [
        ExpectColumnValuesToNotContainSuspectSignSmell(),
        ExpectColumnValuesToNotContainIntegerAsStringSmell(),
        ExpectColumnValuesToNotContainFloatingPointNumberAsStringSmell(),
        ExpectColumnValuesToNotContainLongDataValueSmell()
    ]

    def test_examples_of_all_expectations(self):
        for expectation in self.expectations_to_test:
            print(f"Executing tests for {expectation.expectation_type}")
            check_expectation_examples(expectation)
