import os
import configargparse

CONFIG = None
secret_token = os.getenv("SECRET_KEY")
database_connection = os.getenv("DATABASE_URL") or "sqlite:///data.db"

arg_parser = configargparse.ArgParser(default_config_files=["config.txt"])

arg_parser.add("-c", "--config", is_config_file=True, help="Config file")

arg_parser.add(
    "-t", "--secret_token", default=secret_token, help="Discord bot login token"
)

arg_parser.add(
    "-p", "--command_prefix", default="$", help="The symbol used before commands"
)

arg_parser.add(
    "-d",
    "--database_connection",
    default=database_connection,
    help="An SQLAlchemy connection string",
)


def parse_args():
    global CONFIG
    CONFIG = arg_parser.parse_args()
