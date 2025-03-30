import os
from datetime import datetime, timedelta
from src.utils.logger import setup_logging  # Import the logger setup function

# Instantiate the logger
logger = setup_logging("file_utils")


def delete_old_csv_files(directory: str, days: int):
    """
    Deletes CSV files in the specified directory that are older than the given
    number of days.

    :param directory: Directory containing the CSV files.
    :param days: Number of days to keep files.
        Files older than this will be deleted.
    """
    now = datetime.now()
    cutoff_time = now - timedelta(days=days)

    if not os.path.exists(directory):
        logger.warning(
            f"⚠️ Directory {directory} does not exist. Skipping deletion."
        )
        return

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if file_name.endswith(".csv") and os.path.isfile(file_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time < cutoff_time:
                try:
                    os.remove(file_path)
                    logger.info(f"🗑️ Deleted old file: {file_path}")
                except Exception as e:
                    logger.error(f"❌ Failed to delete file {file_path}: {e}")
