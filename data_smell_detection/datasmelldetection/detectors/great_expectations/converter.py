from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any

from great_expectations.profile.base import ProfilerDataType
from great_expectations.validator.validator import (
    ExpectationSuiteValidationResult,
    ExpectationValidationResult
)

from datasmelldetection.core.detector import (
    DetectionResult,
    DetectionStatistics
)
from .datasmell import DataSmellRegistry


@dataclass
class ExtendedDetectionResult(DetectionResult):
    """
    Great Expectations specific extensions of the
    :class:`~datasmelldetection.core.detector.DetectionResult` class.
    """

    column_type: ProfilerDataType
    """The type of the column where a data smell was detected."""  # pylint: disable=W0105

    expectation_kwargs: Dict[str, Any]
    """
    The kwargs which were used to evaluate the corresponding Great Expectations
    Expectation which performed the data smell detection.
    """  # pylint: disable=W0105


class DetectionResultConverter(ABC):
    """
    An abstract base class for classes which perform the conversion from
    :class:`great_expectations.validator.validator.ExpectationSuiteValidationResult`
    objects to
    :class:`~.ExtendedDetectionResult` instances.
    """

    def __init__(self):
        self._meta: Dict[str, Any] = {}

    @abstractmethod
    def convert(self, result: ExpectationSuiteValidationResult) -> Iterable[ExtendedDetectionResult]:
        """
        Perform the conversion from an
        :class:`~great_expectations.validator.validator.ExpectationSuiteValidationResult`
        object
        to :class:`~.ExtendedDetectionResult` instances.
        """

    @property
    def meta(self) -> Dict[str, Any]:
        """Additional meta information which converters can use."""
        return self._meta

    @meta.setter
    def meta(self, new_meta: Dict[str, Any]):
        self._meta = new_meta


class StandardResultConverter(DetectionResultConverter):
    """
    A detection result converter which extracts information
    from the
    :class:`great_expectations.validator.validator.ExpectationSuiteValidationResult`
    for the fields in :class:`~.ExtendedDetectionResult`.

    In order to get the column type of a checked column, it is assumed that the
    meta dictionary of the :class:`.DetectionResultConverter` class contains the
    key "column_types" which is of type Dict[str, ProfilerDataType]. It is
    required to set the described meta dictionary before invoking the
    convert method of this class.
    """

    def __init__(self, registry: DataSmellRegistry):
        """
        :param registry: The data smell registry which manages the data smells which
            should be detected.
        """
        self._registry = registry

    @property
    def registry(self) -> DataSmellRegistry:
        """
        The data smell registry which manages the data smells which should be
        detected.
        """
        return self._registry

    @registry.setter
    def registry(self, new_registry: DataSmellRegistry):
        # TODO: Validate argument
        self._registry = new_registry

    def filter_callback(self, result: ExpectationValidationResult) -> bool:
        """
        :param result: The
            :class:`~great_expectations.validator.validator.ExpectationValidationResult`
            which should be checked.
        :return: Return True if the corresponding
            :class:`~great_expectations.validator.validator.ExpectationValidationResult`
            object should be used for constructing a
            :class:`~.ExtendedDetectionResult`
            object.
        """
        return result.success is False

    def convert(
            self,
            validation_suite_result: ExpectationSuiteValidationResult
    ) -> Iterable[ExtendedDetectionResult]:
        """
        Perform the conversion to detection results.

        :param validation_suite_result: The object which contains the validated
            expectation suite.
        :return: The resulting data smell detection results.
        """
        # Lookup dictionary which maps the expectation type (as found in an
        # ExpectationSuiteValidationResult to data smell types.
        data_smell_type_dict = self.registry.get_expectation_type_to_data_smell_type_dict()

        detected_data_smells = []

        # Validated expectations (unfiltered)
        expectation_validation_results: List[ExpectationValidationResult] = \
            validation_suite_result.results

        # Only keep relevant results
        filtered_validation_results: Iterable[ExpectationValidationResult] = \
            filter(self.filter_callback, expectation_validation_results)

        for validation_result in filtered_validation_results:
            detection_statistics = DetectionStatistics(
                total_element_count=validation_result.result["element_count"],
                faulty_element_count=validation_result.result["unexpected_count"]
            )

            # Column where the data smell is present
            column_name = validation_result.expectation_config["kwargs"]["column"]
            # A subset of fault elements which contain the data smell.
            faulty_elements = validation_result.result["partial_unexpected_list"]
            # The type of the data smell which is present in the corresponding
            # column.
            expectation_type: str = validation_result.expectation_config["expectation_type"]
            data_smell_type = data_smell_type_dict[expectation_type]
            # Get column type from passed meta information
            column_type: ProfilerDataType = self.meta["column_types"][column_name]

            detection_result = ExtendedDetectionResult(
                column_name=column_name,
                statistics=detection_statistics,
                faulty_elements=faulty_elements,
                data_smell_type=data_smell_type,
                column_type=column_type,
                expectation_kwargs=validation_result.expectation_config["kwargs"]
            )
            detected_data_smells.append(detection_result)

        return detected_data_smells
