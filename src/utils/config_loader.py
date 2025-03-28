import yaml
from src.utils.logger import setup_logging

# Instantiate a logger for the config loader
logger = setup_logging("config_loader")


def load_yaml_config(file_path: str):
    """
    Loads and validates a YAML configuration file.

    :param file_path: Path to the YAML file.
    :return: Parsed configuration dictionary or None if an error occurs.
    """
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
            if not config:
                raise ValueError("Invalid or empty configuration file.")
            return config
    except Exception as e:
        logger.exception(f"Failed to load YAML file {file_path}: {e}")
        return None


def validate_config(config: dict, required_keys: list):
    """
    Validates that the required keys exist in the configuration.

    :param config: The configuration dictionary to validate.
    :param required_keys: A list of keys that must exist in the configuration.
    :raises ValueError: If any required key is missing.
    """
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(
            f"Missing required keys in configuration: {missing_keys}"
        )
