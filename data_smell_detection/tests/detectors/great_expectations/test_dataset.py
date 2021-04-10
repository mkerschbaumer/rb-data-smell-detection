import os
import great_expectations

from datasmelldetection.detectors.great_expectations.dataset import GreatExpectationsDatasetManager
from datasmelldetection.detectors.great_expectations.context import GreatExpectationsContextBuilder
from datasmelldetection.core import Dataset

cwd = os.getcwd()

# NOTE: From view of root directory of package
_test_data_directory = os.path.join(cwd, "tests/test_sets")
_test_great_expectations_directory = os.path.join(cwd, "../great_expectations")
context_builder = GreatExpectationsContextBuilder(
    _test_great_expectations_directory,
    _test_data_directory
)
context = context_builder.build()

manager = GreatExpectationsDatasetManager(context=context)


class TestGreatExpectationsDatasetManager:
    def test_creation(self):
        GreatExpectationsDatasetManager(context=context)

    def test_get_available_dataset_identifiers(self):
        identifiers = manager.get_available_dataset_identifiers()
        assert isinstance(identifiers, set)
        assert len(identifiers) == 1
        assert "Titanic.csv" in identifiers

    def test_get_dataset(self):
        dataset = manager.get_dataset("Titanic.csv")
        assert isinstance(dataset, Dataset)


class TestGreatExpectationsDataset:
    def test_get_column_names(self):
        dataset = manager.get_dataset("Titanic.csv")

        expected_column_names = ["Name", "PClass", "Age", "Sex", "Survived", "SexCode"]
        column_names = dataset.get_column_names()
        # Ensure all expected column names are present
        assert all([name in column_names for name in expected_column_names])

    def test_get_great_expectations_dataset(self):
        dataset = manager.get_dataset("Titanic.csv")

        # Extract Great Expectations dataset
        ge_dataset = dataset.get_great_expectations_dataset()
        assert isinstance(ge_dataset, great_expectations.dataset.Dataset)
