"""
File I/O utilities for the embeddings generation module.
"""
import json
import os
from typing import List, Dict, Any
from pathlib import Path


class FileHandler:
    """
    Provides file I/O operations for the embeddings generation module.
    """

    @staticmethod
    def read_json_file(file_path: str) -> List[Dict[str, Any]]:
        """
        Read and parse a JSON file containing content chunks.

        Args:
            file_path: Path to the JSON file

        Returns:
            List[Dict[str, Any]]: Parsed JSON data as a list of chunk dictionaries

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
            ValueError: If the JSON doesn't contain a list of chunks
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {str(e)}", e.doc, e.pos)

        if not isinstance(data, list):
            raise ValueError(f"JSON file {file_path} must contain a list of chunks, got {type(data).__name__}")

        return data

    @staticmethod
    def write_json_file(file_path: str, data: List[Dict[str, Any]]) -> None:
        """
        Write data to a JSON file.

        Args:
            file_path: Path where the JSON file should be written
            data: Data to write to the file

        Raises:
            IOError: If there's an error writing the file
        """
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
        """
        Validate a file path.

        Args:
            file_path: Path to validate
            must_exist: Whether the file must exist

        Returns:
            bool: True if the path is valid
        """
        if not file_path or not isinstance(file_path, str):
            return False

        path = Path(file_path)

        if must_exist and not path.exists():
            return False

        # Check if parent directory is writable (for write operations)
        if not must_exist:
            parent_dir = path.parent
            if not parent_dir.exists():
                # Check if we can create the parent directory
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                    parent_dir.rmdir()  # Clean up if we created it
                except:
                    return False

        return True

    @staticmethod
    def read_text_file(file_path: str) -> str:
        """
        Read the contents of a text file.

        Args:
            file_path: Path to the text file

        Returns:
            str: Contents of the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory
        """
        Path(directory_path).mkdir(parents=True, exist_ok=True)