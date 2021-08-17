from dataclasses import dataclass
import os
from typing import List

import pytest

from datasmelldetection.core.detector import (
    DetectionStatistics,
    DetectionResult
)
from datasmelldetection.detectors.great_expectations.context import GreatExpectationsContextBuilder
from datasmelldetection.detectors.great_expectations.converter import StandardResultConverter
from datasmelldetection.detectors.great_expectations.dataset import FileBasedDatasetManager
from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmellRegistry,
    DataSmellType
)
from datasmelldetection.detectors.great_expectations.detector import (
    DetectorBuilder,
    DataSmellAwareConfiguration,
)
from datasmelldetection.detectors.great_expectations.expectations import (
    ExpectColumnValuesToNotContainExtremeValueSmell,
    ExpectColumnValuesToNotContainSuspectSignSmell,
    ExpectColumnValuesToNotContainIntegerAsFloatingPointNumberSmell,
    ExpectColumnValuesToNotContainLongDataValueSmell,
    ExpectColumnValuesToNotContainIntegerAsStringSmell,
    ExpectColumnValuesToNotContainFloatingPointNumberAsStringSmell,
    ExpectColumnValuesToNotContainCasingSmell,
    ExpectColumnValuesToNotContainDuplicatedValueSmell
)
from great_expectations.core import ExpectationValidationResult

cwd = os.getcwd()

# NOTE: From view of root directory of package
_test_data_directory = os.path.join(cwd, "tests/test_sets")
_test_great_expectations_directory = os.path.join(cwd, "../great_expectations")
context_builder = GreatExpectationsContextBuilder(
    _test_great_expectations_directory,
    _test_data_directory
)
context = context_builder.build()

dataset_manager = FileBasedDatasetManager(context=context)
# Import dataset which has been created to test the detection of data smells.
data_smell_testset = dataset_manager.get_dataset("data_smell_testset.csv")


@dataclass
class DetectorTestCase:
    # The name of the test which is contained in the expectation that is raised
    # if the test fails.
    title: str

    # The configuration used for profiling
    configuration: DataSmellAwareConfiguration

    # All detection results which must be returned by the data smell detection
    # process.
    expected_detection_results: List[DetectionResult]


testcases: List[DetectorTestCase] = [
    DetectorTestCase(
        title="parameterset1",
        configuration=DataSmellAwareConfiguration(
            column_names=None,  # All columns
            data_smell_configuration={
                DataSmellType.EXTREME_VALUE_SMELL: {"mostly": 1, "threshold": 3},
                DataSmellType.SUSPECT_SIGN_SMELL: {"mostly": 1, "percentile_threshold": 0.25},
                DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL: {"mostly": 0.6, "epsilon": 0.15},
                DataSmellType.LONG_DATA_VALUE_SMELL: {"mostly": 1, "length_threshold": 30},
                DataSmellType.INTEGER_AS_STRING_SMELL: {"mostly": 0.2},
                DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL: {"mostly": 0.2},
                DataSmellType.CASING_SMELL: {"mostly": 1, "same_case_wordcount_threshold": 2},
                DataSmellType.DUPLICATED_VALUE_SMELL: {"mostly": 1}
            }
        ),
        expected_detection_results=[
            DetectionResult(
                column_name="int1",
                data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
                faulty_elements=[-300],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=1),
            ),
            DetectionResult(
                column_name="int1",
                data_smell_type=DataSmellType.SUSPECT_SIGN_SMELL,
                faulty_elements=[-300],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=1),
            ),
            DetectionResult(
                column_name="float1",
                data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
                faulty_elements=[-300.5],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=1),
            ),
            DetectionResult(
                column_name="float1",
                data_smell_type=DataSmellType.SUSPECT_SIGN_SMELL,
                faulty_elements=[-300.5],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=1),
            ),
            DetectionResult(
                column_name="float2",
                data_smell_type=DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL,
                faulty_elements=[1.1, 4.9, 5.1, 8.9, 9.1],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=5),
            ),
            DetectionResult(
                column_name="string1",
                data_smell_type=DataSmellType.LONG_DATA_VALUE_SMELL,
                faulty_elements=["Pseudopseudohypoparathyroidism"],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=1),
            ),
            DetectionResult(
                column_name="string2",
                data_smell_type=DataSmellType.INTEGER_AS_STRING_SMELL,
                faulty_elements=["2", "-3", "4", "-5", "6", "-7", "8", "-30", "9", "-10"],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=10),
            ),
            DetectionResult(
                column_name="string3",
                data_smell_type=DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL,
                faulty_elements=[
                    "-2.2",
                    "3.8",
                    "-4.9",
                    "5.1",
                    "-6.2",
                    "7.8",
                    "-8.9",
                    "9.1",
                    "-10.2",
                    "11.8"
                ],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=10),
            ),
            DetectionResult(
                column_name="string1",
                data_smell_type=DataSmellType.CASING_SMELL,
                faulty_elements=[
                    "abc def ghi",
                    "abc def ghi",
                    "cAsing 1",
                    "CaSing 2",
                    "all lowercase",
                    "ALL UPPERCASE",
                ],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=6),
            ),
            DetectionResult(
                column_name="string1",
                data_smell_type=DataSmellType.DUPLICATED_VALUE_SMELL,
                faulty_elements=[
                    "abc def ghi",
                    "abc def ghi",
                ],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=2),
            ),
            DetectionResult(
                column_name="int2",
                data_smell_type=DataSmellType.DUPLICATED_VALUE_SMELL,
                faulty_elements=[
                    8,
                    8
                ],
                statistics=DetectionStatistics(total_element_count=10, faulty_element_count=2),
            )
        ]
    )
]


# Create a separate DataSmellRegistry for reproducibility of unit tests (don't
# use default_registry).
@pytest.fixture
def registry() -> DataSmellRegistry:
    registry = DataSmellRegistry()

    # Only register data smells which are actually contained in the data smell testset
    # (to ensure that only the expected data smells are found and no unexpected:w
    # data smells).
    ExpectColumnValuesToNotContainExtremeValueSmell().register_data_smell(registry=registry)
    ExpectColumnValuesToNotContainSuspectSignSmell().register_data_smell(registry=registry)
    ExpectColumnValuesToNotContainIntegerAsFloatingPointNumberSmell().register_data_smell(registry=registry)
    ExpectColumnValuesToNotContainLongDataValueSmell().register_data_smell(registry=registry)
    ExpectColumnValuesToNotContainIntegerAsStringSmell().register_data_smell(registry=registry)
    ExpectColumnValuesToNotContainFloatingPointNumberAsStringSmell().register_data_smell(registry=registry)
    ExpectColumnValuesToNotContainCasingSmell().register_data_smell(registry=registry)
    ExpectColumnValuesToNotContainDuplicatedValueSmell().register_data_smell(registry=registry)

    return registry


class TestDetectorBuilder:
    def test_creation(self, registry):
        builder = DetectorBuilder(context=context, dataset=data_smell_testset)
        for testcase in testcases:
            converter: StandardResultConverter = StandardResultConverter(registry)
            detector = builder.\
                set_registry(registry).\
                set_configuration(testcase.configuration).\
                set_converter(converter).\
                build()
            detection_results = detector.detect()
            assert len(detection_results) == len(testcase.expected_detection_results), testcase.title
            invalid_elements: List[ExpectationValidationResult] = \
                converter.get_invalid_validation_results()
            assert len(invalid_elements) == 0

            # Ensure that for each expected DetectionResult there is a DetectionResult
            # returned by the data smell detection process.
            for expected_detection_result in testcase.expected_detection_results:
                # Return a bool whether other DetectionResult to compare matches the currently
                # processed expected DetectionResult. Only compare the the column name,
                # data smell type and faulty elements
                def is_match_expected_detection_result(other: DetectionResult):
                    other_element_count = other.statistics.faulty_element_count
                    expected_element_count = expected_detection_result.statistics.faulty_element_count
                    expected_faulty_elements = set(expected_detection_result.faulty_elements)
                    return other.column_name == expected_detection_result.column_name and \
                           other.data_smell_type == expected_detection_result.data_smell_type and \
                           other_element_count == expected_element_count and \
                           expected_faulty_elements == set(other.faulty_elements)

                # Ensure a matching DetectionResult object was returned
                assert any(map(is_match_expected_detection_result, detection_results)), \
                    testcase.title
