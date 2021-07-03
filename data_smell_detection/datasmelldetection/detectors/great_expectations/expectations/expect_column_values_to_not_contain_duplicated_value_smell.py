from great_expectations.expectations.core import ExpectColumnValuesToBeUnique
from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmell,
    DataSmellMetadata
)


class ExpectColumnValuesToNotContainDuplicatedValueSmell(ExpectColumnValuesToBeUnique, DataSmell):
    """
    Detect if a duplicate value smell is present.

    The ExpectColumnValuesToBeUnique expectation from Great Expectations
    is used.
    """

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.DUPLICATED_VALUE_SMELL,
        # Data smell for all supported data types
        profiler_data_types={ProfilerDataType.STRING, ProfilerDataType.INT}
    )

    # NOTE: library_metadata not set since the ExpectColumnValuesToBeUnique
    # expectation sets it.


# Perform registration of data smell at DataSmellRegistry
expectation = ExpectColumnValuesToNotContainDuplicatedValueSmell()
expectation.register_data_smell()
