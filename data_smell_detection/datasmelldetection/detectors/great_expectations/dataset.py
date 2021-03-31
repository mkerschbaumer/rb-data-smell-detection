from typing import Set, Optional, Iterator
from great_expectations import DataContext
from great_expectations.core.batch import BatchRequest
from great_expectations.dataset.pandas_dataset import PandasDataset
import great_expectations

import datasmelldetection.core


class GreatExpectationsDataset(datasmelldetection.core.Dataset):
    """
    A thin wrapper around :class:`great_expectations.dataset.Dataset`

    This class is required in order to allow consistent retrieval of column names.
    """

    def __init__(self, dataset: great_expectations.dataset.Dataset):
        """
        :param dataset: The :class:`great_expectations.dataset.Dataset` which should be
            wrapped.
        """

        self._dataset = dataset

    def get_column_names(self) -> Set[str]:
        """
        :return: The column names of the wrapped dataset.
        """
        return set(self._dataset.get_table_columns())

    def get_great_expectations_dataset(self) -> great_expectations.dataset.Dataset:
        """
        :return: The wrapped :class:`great_expectations.dataset.Dataset`.
        """
        return self._dataset


# Internal convenience function for constructing batch request (for default Great
# Expectations setup)
def _build_batch_request(filename: Optional[str]) -> BatchRequest:
    if filename is None:
        # No filename specified => construct BatchRequest to get all available batches
        batch_identifiers = {}
    else:
        batch_identifiers = {"filename": filename}

    return BatchRequest(
        datasource_name="csv_data_source",
        data_connector_name="csv_data_connector",
        data_asset_name="csv_asset",
        partition_request={"batch_identifiers": batch_identifiers}
    )


class GreatExpectationsDatasetManager(datasmelldetection.core.DatasetManager):
    """
    A class for managing :class:`.Dataset` instances.

    This class is designed to import CSV files from a given data directory. A Great Expectations
    directory is required.
    """

    def __init__(self, context_root_dir: str, data_directory: str):
        """
        :param context_root_dir: A directory containing the great_expectations.yml configuration
            file. This directory is used as the context root directory for creating a
            :class:`great_expectations.DataContext` instance.
        :param data_directory: A directory which contains CSV files that should be imported.
        """
        runtime_environment = {
            "data_directory": data_directory
        }
        context: DataContext = DataContext(
            context_root_dir=context_root_dir,
            runtime_environment=runtime_environment
        )

        self._datasource = context.get_datasource("csv_data_source")

    def get_available_dataset_identifiers(self) -> Set[str]:
        """
        :return: The set of available dataset identifiers (e.g. file names) which are present
            in the data directory.
        """

        # Build batch request with no filename => needed to get all available
        # batch definitions
        batch_request = _build_batch_request(None)
        batch_definitions = self._datasource.get_available_batch_definitions(batch_request)

        def extract_filename(x):
            return x["partition_definition"]["filename"]

        # Get available filenames
        filenames: Iterator[str] = map(extract_filename, batch_definitions)
        return set(filenames)

    def get_dataset(self, dataset_identifier: str) -> GreatExpectationsDataset:
        """
        :param dataset_identifier: The dataset identifier (e.g. file name of the CSV file)
            to import.
        :return: The imported dataset.
        """

        batch_request = _build_batch_request(filename=dataset_identifier)
        batch = self._datasource.get_single_batch_from_batch_request(batch_request)
        # Convert imported batch to DataAsset
        dataset: great_expectations.dataset.Dataset = PandasDataset(batch.data.dataframe)
        return GreatExpectationsDataset(dataset)
