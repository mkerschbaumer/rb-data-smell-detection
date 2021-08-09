import json
from typing import Dict, Any

from great_expectations.expectations.core import ExpectColumnValuesToNotBeNull
from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmell,
    DataSmellMetadata
)


class ExpectColumnValuesToNotContainMissingValueSmell(ExpectColumnValuesToNotBeNull, DataSmell):
    """
    Detect if a missing value smell is present.

    The ExpectColumnValuesToNotBeNull expectation from Great Expectations
    is used.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.MISSING_VALUE_SMELL,
        # Data smell for all supported data types
        profiler_data_types=set([e for e in ProfilerDataType])
    )

    # NOTE: library_metadata not set since the ExpectColumnValuesToNotBeNull
    # expectation sets it.

    default_kwarg_values: Dict[str, Any] = {
        "mostly": 0.95
    }

# Perform registration of data smell at DataSmellRegistry
expectation = ExpectColumnValuesToNotContainMissingValueSmell()
expectation.register_data_smell()

if __name__ == "__main__":
    diagnostics_report = expectation.run_diagnostics()
    print(json.dumps(diagnostics_report, indent=2))
