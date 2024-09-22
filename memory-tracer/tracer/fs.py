import csv
import gzip
import os
import shutil
from enum import Enum
from typing import Dict, Iterator, List

from tracer.config import DATA_DIR


# Enum to define the type of files this handler can manage
class FileType(Enum):
    TRANSACTION = "transactions"
    CALL_FRAME = "call_frames"


class OutputHandler:
    def __init__(self, start_block: int, end_block: int, file_type: FileType):
        """
        Initialize the Handler instance for a specific file type.

        Args:
            start_block (int): The starting block number.
            end_block (int): The ending block number.
            file_type (FileType): The type of file to handle (TRANSACTION or CALL_FRAME).
        """
        self.start_block = start_block
        self.end_block = end_block
        self.file_type = file_type
        self.directory = os.path.join(DATA_DIR, f"{self.start_block}_to_{self.end_block}")
        self.file_name = os.path.join(self.directory, f"{self.file_type.value}.csv")
        self.compressed_file_name = f"{self.file_name}.gz"

        # Ensure the directory exists
        os.makedirs(self.directory, exist_ok=True)

        # Open the CSV file and initialize the CSV writer with appropriate headers
        self.csv_file = open(self.file_name, "w", newline="")
        self.writer = self.create_writer()
        self.writer.writeheader()

    def create_writer(self):
        """
        Create a CSV writer based on the file type.

        Returns:
            csv.DictWriter: The CSV writer instance configured with appropriate headers.
        """
        # Define fieldnames based on file type
        fieldnames = {
            FileType.TRANSACTION: ["id", "block", "tx_hash", "tx_gas", "to"],
            FileType.CALL_FRAME: [
                "transaction_id",
                "call_depth",
                "opcode",
                "memory_access_offset",
                "memory_access_size",
                "opcode_gas_cost",
                "pre_active_memory_size",
                "post_active_memory_size",
                "memory_expansion",
            ],
        }.get(self.file_type, [])

        if not fieldnames:
            raise ValueError(f"Unsupported file type: {self.file_type}")

        return csv.DictWriter(
            self.csv_file, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
        )

    def write(self, data: List[Dict[str, str]]):
        """
        Write a list of dictionaries to the CSV file.

        Args:
            data (List[Dict[str, str]]): The data to write to the file.
        """
        for entry in data:
            self.writer.writerow(entry)

    def compress(self, delete_source=True):
        """
        Compress the CSV file into a gzip format and remove the original file.
        """
        # Important to close the file so that buffers are written to disk
        self.csv_file.close()

        with open(self.file_name, "rb") as f_in:
            with gzip.open(self.compressed_file_name, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        delete_source and os.remove(self.file_name)

    def __del__(self):
        """
        Ensure the CSV file is closed properly when the instance is deleted.
        """
        self.csv_file.close()


class CSVIterator:
    def __init__(self, file_path: str):
        """
        Initialize the CSVIterator instance.

        Args:
            file_path (str): Path to the gzip-compressed CSV file.
        """
        self.file_path = file_path
        self._file = None
        self._csv_reader = None
        self.header = None

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        """
        self._file = gzip.open(self.file_path, "rt", encoding="utf-8")
        self._csv_reader = csv.reader(self._file)
        self.header = next(self._csv_reader)  # Read and skip the header row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.
        """
        if self._file:
            self._file.close()

    def __iter__(self) -> Iterator[Dict[str, str]]:
        """
        Return an iterator over the rows of the CSV file, skipping the header.

        Returns:
            Iterator[Dict[str, str]]: An iterator over the CSV rows as dictionaries.
        """
        if self._csv_reader is None:
            raise RuntimeError("Iterator not initialized. Ensure you use the context manager.")

        # Process each row, skipping the header
        for row in self._csv_reader:
            yield dict(zip(self.header, row))
