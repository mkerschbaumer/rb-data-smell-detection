from typing import Optional

from great_expectations import DataContext

class GreatExpectationsContextBuilder:
    """
    A builder class which simplifies the creation of
    :class:`great_expectations.DataContext` instances.

    The reason why the context creation is abstracted using a builder is that the
    :class:`~.dataset.FileBasedDatasetManager`
    class internally uses Great Expectations batch requests which assume that a
    specific CSV-file data source exists. The mentioned data source has a
    dynamic base_directory parameter which is set using a runtime parameter.
    This builder class abstracts the initialization in order to simplify context
    creation.
    """

    def __init__(self, context_root_dir: str, data_directory: str):
        """
        :param context_root_dir: A directory containing the great_expectations.yml configuration
            file. This directory is used as the context root directory for creating a
            :class:`~great_expectations.DataContext` instance.
        :param data_directory: A directory which contains CSV files that should be imported.
        """
        self.set_context_root_dir(context_root_dir)
        self.set_data_directory(data_directory)
        pass

    def set_context_root_dir(self, context_root_dir: str):
        """
        :param context_root_dir: The root directory which the
            :class:`~great_expectations.DataContext` instance should use.
        :return: An object of class :class:`~.GreatExpectationsContextBuilder`
            to allow chaining.
        """
        self._context_root_dir = context_root_dir
        return self

    def set_data_directory(self, data_directory: str):
        """
        :param data_directory: The directory path which contains the CSV files
            which should be analyzed.
        :return: An object of class :class:`~.GreatExpectationsContextBuilder`
            to allow chaining.
        """
        self._data_directory = data_directory
        return self

    def build(self) -> DataContext:
        """
        Build the Great Expectations context object.

        :return: The resulting :class:`~great_expectations.DataContext` object.
        """
        runtime_environment = {
            "data_directory": self._data_directory
        }

        return DataContext(
            context_root_dir=self._context_root_dir,
            runtime_environment=runtime_environment
        )
