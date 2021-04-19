from dataclasses import dataclass
from typing import Any, Dict, Optional

from datasmelldetection.detectors.great_expectations.datasmell import DataSmellMetadata

# General information about a data smell. This dataclass is primarily intended
# to store information about data smells in order to test their presence in
# data smell registries or expectation suites.
@dataclass
class DataSmellInformation:
    # Metadata about a data smell (e.g. column types and smell type which is
    # detected).
    metadata: DataSmellMetadata

    # The expectation type of an Expectation class (of Great Expectations)
    # which implements the data smell detection.
    expectation_type: str

    # Kwargs which should be used to evaluate the expectation.
    kwargs: Dict[str, Any]
