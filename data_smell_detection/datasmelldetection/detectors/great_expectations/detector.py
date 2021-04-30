from dataclasses import dataclass
from typing import Set, Optional, Iterable, Dict, Any
from great_expectations.profile.base import DatasetProfiler
from great_expectations import DataContext
from great_expectations.validator.validator import ExpectationSuiteValidationResult

from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.core.detector import (
    ConfigurableDetector,
    DetectionResult, Configuration
)
from .dataset import GreatExpectationsDataset
from .datasmell import DataSmellRegistry, default_registry
from .converter import (
    DetectionResultConverter,
    ExtendedDetectionResult,
    StandardResultConverter
)
from .profiler import DataSmellAwareProfiler


@dataclass
class GreatExpectationsConfiguration(Configuration):
    """
    A configuration class which controls how data smell detection is performed
    by the :class:`.GreatExpectationsDetector`.
    """

    data_smell_configuration: Optional[Dict[DataSmellType, Dict[str, Any]]]
    """
    Data smell specific kwargs which should be used for data smell detection.
    Kwargs can be seen as parameters to configure how a data smell should be
    detected. This field is meant to be passed to the
    :class:`.DataSmellAwareProfiler` as the "data_smell_configuration"
    configuration value.
    """  # pylint: disable=W0105


class GreatExpectationsDetector(ConfigurableDetector):
    def __init__(
            self,
            context: DataContext,
            dataset: GreatExpectationsDataset,
            profiler: DatasetProfiler,
            registry: DataSmellRegistry,
            converter: DetectionResultConverter):
        self.context = context
        self.dataset = dataset
        self.profiler = profiler
        self.registry = registry
        self.converter = converter

    @property
    def dataset(self) -> GreatExpectationsDataset:
        """The dataset to use."""
        return self._dataset

    @dataset.setter
    def dataset(self, new_dataset: GreatExpectationsDataset):
        # TODO: Validate argument
        self._dataset = new_dataset

    @property
    def profiler(self) -> DatasetProfiler:
        """The profiler to use."""
        return self._profiler

    @profiler.setter
    def profiler(self, new_profiler: DatasetProfiler):
        # TODO: Validate argument
        self._profiler = new_profiler

    @property
    def registry(self) -> DataSmellRegistry:
        """The data smell registry to use."""
        return self._registry

    @registry.setter
    def registry(self, new_registry: DataSmellRegistry):
        # TODO: Validate argument
        self._registry = new_registry

    @property
    def context(self) -> DataContext:
        """The Great Expectations data context."""
        return self._context

    @context.setter
    def context(self, new_context: DataContext):
        # TODO: Validate argument
        self._context = new_context

    @property
    def converter(self) -> DetectionResultConverter:
        """
        The converter object used which converts an
        ExpectationSuiteValidationResult object to a list of detection result
        objects.
        """
        return self._converter

    @converter.setter
    def converter(self, new_context: DataContext):
        # TODO: Validate argument
        self._converter = new_context

    def detect(self) -> Iterable[ExtendedDetectionResult]:
        suite, _ = self.profiler.profile(
            data_asset=self.dataset.get_great_expectations_dataset(),
            profiler_configuration={
                "registry": self.registry
            }
        )

        # Import dataset
        validator = self.context.get_validator(
            batch_request=self._dataset.get_batch_request(),
            expectation_suite=suite
        )
        validation_result: ExpectationSuiteValidationResult = validator.validate()

        self.converter.meta = {
            "column_types": suite.meta["columns"]
        }
        detected_smells = self.converter.convert(validation_result)

        return detected_smells

    def get_supported_data_smell_types(self) -> Set[DataSmellType]:
        return self._registry.get_registered_data_smells()


class DetectorBuilder:
    def __init__(
            self,
            context: DataContext,
            dataset: GreatExpectationsDataset):
        # Great Expectations context
        self._context = context
        # Dataset which should be checked for data smells
        self._dataset = dataset
        # Data smell registry to use
        self._registry: Optional[DataSmellRegistry] = None
        # The Great Expectations DatasetProfiler to use for data smell
        # detection
        self._profiler: Optional[DatasetProfiler] = None
        # The DetectionResultConverter used to convert
        # ExpectationSuiteValidationResult objects to a list of
        # DetectionResult objects.
        self._converter: Optional[DetectionResultConverter] = None

    def set_context(self, context: DataContext):
        self._context = context
        return self

    def set_dataset(self, dataset: GreatExpectationsDataset):
        self._dataset = dataset
        return self

    def set_registry(self, registry: DataSmellRegistry):
        self._registry = registry
        return self

    def set_profiler(self, profiler: DatasetProfiler):
        self._profiler = profiler
        return self

    def set_converter(self, converter: DetectionResultConverter):
        self._converter = converter
        return self

    def build(self) -> GreatExpectationsDetector:
        # Ensure a non-null data smell registry is present
        registry: Optional[DataSmellRegistry] = self._registry
        if registry is None:
            registry = default_registry

        # Create the default profiler if the user didn't provide a non-null
        # profiler object.
        profiler: Optional[DatasetProfiler] = self._profiler
        if profiler is None:
            profiler = DataSmellAwareProfiler()

        # Create the standard converter if the user didn't explicitly provide
        # a DetectionResultConverter.
        converter: Optional[DetectionResultConverter] = self._converter
        if converter is None:
            converter = StandardResultConverter(registry=registry)

        return GreatExpectationsDetector(
            context=self._context,
            dataset=self._dataset,
            registry=registry,
            profiler=profiler,
            converter=converter
        )
