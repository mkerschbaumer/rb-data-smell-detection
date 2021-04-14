from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional, Set, Iterable

from datasmelldetection.core import DataSmellType


@dataclass
class DetectionStatistics:
    """Statistics about a detected data smell."""

    total_element_count: int
    """The total number of analyzed elements (rows)."""  # pylint: disable=W0105

    faulty_element_count: int
    """
    The number of analyzed elements (rows) which contained the corresponding data smell.
    """  # pylint: disable=W0105


@dataclass
class DetectionResult:
    """Information about a detected data smell."""

    data_smell_type: DataSmellType
    """The type of the detected data smell."""  # pylint: disable=W0105

    column_name: str
    """The column where the corresponding data smell was found."""  # pylint: disable=W0105

    statistics: DetectionStatistics
    """Statistics regarding the presence of the detected data smell."""  # pylint: disable=W0105

    faulty_elements: list
    """A subset of elements which contain the corresponding data smell."""  # pylint: disable=W0105


class Detector(ABC):
    """An abstract base class for detectors."""

    @abstractmethod
    def detect(self) -> Iterable[DetectionResult]:
        """Perform detection and return the found data smells in the form of detection results."""

    @abstractmethod
    def get_supported_data_smell_types(self) -> Set[DataSmellType]:
        """Return a set of data smell types which the detector can find in datasets."""


@dataclass
class Configuration:
    """A configuration class which controls how data smell detection is performed."""

    column_names: Optional[Set[str]]
    """
    The names of the columns where smell detection should be performed. If this attribute is
    provided, columns which are not mentioned are ignored.
    """  # pylint: disable=W0105


class ConfigurableDetector(Detector):
    """A :class:`.Detector` which can be configured using :class:`.Configuration` instances."""

    def __init__(self, configuration: Optional[Configuration]):
        self._configuration: Optional[Configuration] = configuration

    @property
    def configuration(self) -> Optional[Configuration]:
        """The configuration to use."""
        return self._configuration

    @configuration.setter
    def configuration(self, new_configuration: Optional[Configuration]):
        # TODO: Validate argument
        self._configuration = new_configuration
