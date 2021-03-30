from abc import ABC, abstractmethod
from typing import Set


class Dataset(ABC):
    """An abstracted dataset."""

    @abstractmethod
    def get_column_names(self) -> Set[str]:
        """Return the column names of the dataset."""


class DatasetManager(ABC):
    """An abstract class for loading datasets."""

    @abstractmethod
    def get_available_dataset_identifiers(self) -> Set[str]:
        """
        Return the dataset identifiers (e.g. filenames) which can be loaded.
        """

    @abstractmethod
    def get_dataset(self, dataset_identifier: str) -> Dataset:
        """
        Load the specified dataset.
        """
