import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def load_environment_variables(env_path="config/.env"):
    """
    Load environment variables from a .env file.

    :param env_path: Path to the .env file.
    :return: Dictionary of environment variables.
    """
    load_dotenv(dotenv_path=env_path)
    return {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME")
    }


def create_database_engine(env_vars):
    """
    Create a SQLAlchemy engine using the provided environment variables.

    :param env_vars: Dictionary of environment variables.
    :return: SQLAlchemy engine instance.
    """
    DATABASE_URL = (
        f"postgresql://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}@"
        f"{env_vars['DB_HOST']}:{env_vars['DB_PORT']}/{env_vars['DB_NAME']}"
    )
    return create_engine(DATABASE_URL)
