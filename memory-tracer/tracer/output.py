import csv
import gzip
import os
import shutil
from enum import Enum
from typing import Dict, List

from tracer.config import DATA_DIR


# Enum to define the type of files this handler can manage
class FileType(Enum):
    TRANSACTION = "transactions"
    CALL_FRAME = "call_frames"


class Handler:
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
        self.directory = os.path.join(DATA_DIR, f"from_{self.start_block}_to_{self.end_block}")
        self.file_name = os.path.join(self.directory, f"{self.file_type.value}.csv")

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
            FileType.CALL_FRAME: ["id", "function", "line_number", "file"],
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
        with open(self.file_name, "rb") as f_in:
            with gzip.open(f"{self.file_name}.gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        delete_source and os.remove(self.file_name)

    def __del__(self):
        """
        Ensure the CSV file is closed properly when the instance is deleted.
        """
        if hasattr(self, "csv_file"):
            self.csv_file.close()
