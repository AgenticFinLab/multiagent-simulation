"""
Reading runtime parameters from a configuration file.


This config will load the config file and then create folders for the project.
We assume that we are in the root folder of the project:

- base_path
    - data (data_path)
    - {ix_project_name}--{user_project_name} (project_name)
        - {execute_id}  (log_path)
            - checkpoints
            - results
            - loggings
            - visualizations
    - record_path.csv


"run_id": None,  # run id
"base_path": None,  # base path of the project
"base_project_name": None,
"user_project_name": None,
"fix_project_name": None, --> base_project_name--data_name--model_name
"project_name": None, --> fix_project_name--user_project_name
"project_path": None,
"exe_id": None,  # id of the logging name
"exe_path": None,  # path of the logging
"config_path": None,  # path of the config file
"config_name": None,
"model_name": None,
"data_name": None,
"record_path": None,  # path of the record of config
"""

import os
import sys
import time
import json
import argparse
import logging
import shutil
from pathlib import Path
from typing import Any, IO
from functools import reduce
from operator import getitem
from datetime import datetime
from collections import OrderedDict, namedtuple

import torch
import yaml
import numpy as np
import pandas as pd


logging.getLogger("httpx").setLevel(logging.CRITICAL)


def set_path(
    user_path: str,
    default_path: str = "Default",
    is_create_default: bool = True,
) -> str:
    """
    Check whether the path exists.

    :param path: The path to be checked. This path can be the one set by the user.
    :param log_name: The name of the path to be checked.
    """
    HOMEPATH = str(Path.home())
    user_path = user_path.replace("~", HOMEPATH)
    # If the path exists, return the path
    f_path = (
        user_path
        if os.path.exists(user_path)
        else default_path if os.path.exists(default_path) else None
    )
    if f_path is None and is_create_default:
        f_path = default_path
        f_path = Path(f_path).as_posix()
        os.makedirs(f_path, exist_ok=True)

    return f_path


def query_values(content: dict, query: str) -> list:
    """Obtain the values from the nested dictionary based on the query."""
    return [
        next((reduce(getitem, k.split("|"), content) for _ in (1,) if k), None)
        for k in query.split(";")
        if k
    ]


def format_str(ori_string: str):
    """Make the string to be a valid name."""
    # Replace every special character with '-'
    special_chars = ["/", "\\", "#", "?", "%", ":"]
    for char in special_chars:
        ori_string = ori_string.replace(char, "-")
    return ori_string


class Loader(yaml.SafeLoader):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""

        try:
            self.root_path = os.path.split(stream.name)[0]
        except AttributeError:
            self.root_path = os.path.curdir

        super().__init__(stream)


class Config:
    """
    Retrieving configuration parameters by parsing a configuration file
    using the YAML configuration file parser.
    """

    logging = None
    _instance = None

    @staticmethod
    def construct_join(loader: Loader, node: yaml.Node) -> Any:
        """Support os.path.join at node."""
        seq = loader.construct_sequence(node)
        return "/".join([str(i) for i in seq])

    @staticmethod
    def construct_include(loader: Loader, node: yaml.Node) -> Any:
        """Include file referenced at node."""
        filename = os.path.abspath(
            os.path.join(loader.root_path, loader.construct_scalar(node))
        )
        extension = os.path.splitext(filename)[1].lstrip(".")

        extension = os.path.splitext(filename)[1].lstrip(".")
        with open(filename, "r", encoding="utf-8") as config_file:
            if extension in ("yaml", "yml"):
                return yaml.load(config_file, Loader)
            elif extension in ("json",):
                return json.load(config_file)
            else:
                return "".join(config_file.readlines())

    @staticmethod
    def construct_merge_include(loader: Loader, node: yaml.Node) -> Any:
        """
        Include multiple files referenced at node with tag `!minclude`.

        For merging multiple files under one include, the format of should be
        <>;;<>;;
        where <> will be the path of one config file while `;;` is used to
        separate the files
        Lead to: !minclude: <>;;<>;;
        """
        # load the files as a whole
        to_be_include = loader.construct_scalar(node)
        include_files = to_be_include.split(";;")

        merged_content = {}
        for file in include_files:
            filepath = os.path.abspath(os.path.join(loader.root_path, file))

            extension = os.path.splitext(filepath)[1].lstrip(".")
            file_content = {}
            with open(filepath, "r", encoding="utf-8") as config_file:
                if extension in ("yaml", "yml"):
                    file_content = yaml.load(config_file, Loader)
                elif extension in ("json",):
                    file_content = json.load(config_file)
                else:
                    file_content = "".join(config_file.readlines())
            merged_content.update(file_content)

        return merged_content

    def __new__(cls):
        if cls._instance is None:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-c",
                "--config",
                type=str,
                help="Configuration file used by the project.",
            )
            parser.add_argument(
                "-b",
                "--base",
                type=str,
                help="The base path where the project loads and saves info.",
            )
            parser.add_argument(
                "-p",
                "--project",
                type=str,
                help="The name of the project",
            )
            parser.add_argument(
                "-u",
                "--user",
                type=str,
                default="",
                help="The additional user information added to the project name based on the config file",
            )
            parser.add_argument(
                "-r",
                "--record",
                type=str,
                default="experiments.csv",
                help="Record the project details under the folder.",
            )
            parser.add_argument(
                "-l", "--log", type=str, default="info", help="Log messages level."
            )

            args = parser.parse_args()
            Config.args = args

            cls._instance = super(Config, cls).__new__(cls)

            if "config_file" in os.environ:
                filepath = os.environ["config_file"]
            else:
                filepath = args.config

            # add the tag to support the !include
            yaml.add_constructor("!include", Config.construct_include, Loader)
            yaml.add_constructor("!minclude", Config.construct_merge_include, Loader)
            yaml.add_constructor("!join", Config.construct_join, Loader)

            if os.path.isfile(filepath):
                with open(filepath, "r", encoding="utf-8") as config_file:
                    config = yaml.load(config_file, Loader)
            else:
                # if the configuration file does not exist, raise an error
                raise ValueError("A configuration file must be supplied.")

            # The config file must contain  parts
            #  data, environment, model, train, logging, evaluation
            Config.data = Config.namedtuple_from_dict(config["data"])
            Config.env = Config.namedtuple_from_dict(config["environment"])
            Config.model = Config.namedtuple_from_dict(config["model"])
            Config.train = Config.namedtuple_from_dict(config["train"])
            Config.logging = Config.namedtuple_from_dict(config["logging"])
            Config.eval = Config.namedtuple_from_dict(config["evaluation"])

            # Get the path of the home directory
            HOMEPATH = str(Path.home())

            # Customizable dictionary of global parameters
            # Log id is the folder name of all logging information
            # include:
            #   - checkpoint_path,
            #   - result_path,
            #   -logging_path,
            #   - visualization_path
            # base_path is where to save projects
            # project_name is the name of the project
            # base_path/project_name
            Config.params: dict = {
                "run_id": None,  # run id
                "base_path": None,  # base path of the project
                "base_project_name": None,
                "user_project_name": None,
                "fix_project_name": None,
                "project_name": None,
                "project_path": None,
                "exe_id": None,  # id of the logging name
                "exe_path": None,  # path of the logging
                "config_path": None,  # path of the config file
                "config_name": None,
                "model_name": None,
                "data_name": None,
                "record_path": None,  # path of the record of config
            }
            #
            # A run ID is unique in an experiment
            # The precisions are unique for all parts of the model
            Config.params["run_id"] = os.getpid()

            # Extract the settings from the command line
            base_path = Config.args.base.replace("~", HOMEPATH)
            base_project_name = Config.args.project
            user_keys = Config.args.user
            record = Config.args.record

            Config.params["base_path"] = base_path
            os.makedirs(base_path, exist_ok=True)

            Config.params["base_project_name"] = base_project_name

            # Get the fix project name
            # Get the name of the data and the model
            model_name = format_str(Config.model.model_name)
            data_name = format_str(Config.data.data_name)
            Config.params["model_name"] = model_name
            Config.params["data_name"] = data_name
            exe_id, fix_name = Config.create_sub_folders()
            fix_project_name = f"{base_project_name}--{fix_name}"
            fix_project_name = format_str(fix_project_name)
            Config.params["fix_project_name"] = fix_project_name

            # Get the user project name
            # The user' config setting to enhance the project name
            # by adding these information to the project name
            values = query_values(config, user_keys)
            values = [format_str(str(value)) for value in values]
            user_keys = user_keys.split(";")
            Config.params["user_project_keys"] = dict(zip(user_keys, values))
            user_project_name = "--".join(values)
            Config.params["user_project_name"] = user_project_name

            project_name = fix_project_name
            if user_project_name != "":
                project_name = f"{fix_project_name}--{user_project_name}"

            Config.params["project_name"] = project_name
            project_path = os.path.join(base_path, project_name)
            Config.params["project_path"] = project_path
            os.makedirs(project_path, exist_ok=True)

            Config.params["exe_id"] = exe_id
            log_path = os.path.join(project_path, exe_id)
            Config.params["log_path"] = log_path

            # Get the prefix of the filename
            filename = os.path.basename(filepath)
            Config.params["config_path"] = filepath
            Config.params["config_name"] = filename

            Config.params["record_path"] = os.path.join(base_path, record)

            # Record the current running
            Config.set_records()

            # Set the data path
            data_path = Config().data.data_path.replace("~", HOMEPATH)
            Config.data = Config.data._replace(
                data_path=set_path(
                    os.path.join(data_path, Config.params["data_name"]),
                    default_path=os.path.join(
                        base_path, "data", Config.params["data_name"]
                    ),
                    is_create_default=True,
                )
            )
            # Set the logging path
            # project_path/log_path/logging
            # project_path/checkpoints
            # project_path/results
            # project_path/visualization
            # Set checkpoint

            # the basic saving dir name in
            # models/checkpoints/results/logging

            checkpoint_path = Config().logging.checkpoint_path
            result_path = Config().logging.result_path
            logging_path = Config().logging.logging_path
            visualization_path = Config().logging.visualization_path
            checkpoint_path = checkpoint_path.replace("~", HOMEPATH)
            Config.logging = Config.logging._replace(
                checkpoint_path=set_path(
                    checkpoint_path,
                    default_path=os.path.join(log_path, "checkpoints"),
                    is_create_default=True,
                )
            )
            Config.logging = Config.logging._replace(
                result_path=set_path(
                    result_path,
                    default_path=os.path.join(log_path, "results"),
                    is_create_default=True,
                )
            )
            Config.logging = Config.logging._replace(
                logging_path=set_path(
                    logging_path,
                    default_path=os.path.join(log_path, "loggings"),
                    is_create_default=True,
                )
            )
            Config.logging = Config.logging._replace(
                visualization_path=set_path(
                    visualization_path,
                    default_path=os.path.join(log_path, "visualizations"),
                    is_create_default=True,
                )
            )

            os.makedirs(Config().logging.checkpoint_path, exist_ok=True)
            os.makedirs(Config().logging.result_path, exist_ok=True)
            os.makedirs(Config().logging.visualization_path, exist_ok=True)
            os.makedirs(Config().logging.logging_path, exist_ok=True)

            # Saving the given config file to the corresponding
            target_path = os.path.join(log_path, filename)
            if not os.path.exists(target_path):
                shutil.copyfile(src=filepath, dst=target_path)

            # add the log file
            # thus, presenting logging info to the file
            if hasattr(Config().logging, "basic_log_type"):
                basic_log_type = Config().logging.basic_log_type
            else:
                basic_log_type = "info"

            numeric_level = getattr(logging, basic_log_type.upper(), None)

            if not isinstance(numeric_level, int):
                raise ValueError(f"Invalid log level: {basic_log_type}")

            formatter = logging.Formatter(
                fmt="[%(levelname)s][%(asctime)s]: %(message)s", datefmt="%H:%M:%S"
            )

            root_logger = logging.getLogger()
            root_logger.setLevel(numeric_level)

            # only print to the screen
            if hasattr(Config().logging, "stdout_log_type"):
                stdout_log_type = Config().logging.stdout_log_type
                stdout_log_numeric_level = getattr(
                    logging, stdout_log_type.upper(), None
                )
                stdout_handler = logging.StreamHandler(sys.stdout)
                stdout_handler.setLevel(stdout_log_numeric_level)
                stdout_handler.setFormatter(formatter)
                root_logger.addHandler(stdout_handler)

            if hasattr(Config().logging, "file_log_type"):
                file_log_type = Config().logging.file_log_type
                file_log_numeric_level = getattr(logging, file_log_type.upper(), None)
                log_name = time.strftime("%Y_%m_%d__%H_%M_%S.txt", time.localtime())
                log_file_name = os.path.join(
                    Config().logging.logging_path, file_log_type + "_" + log_name
                )

                file_handler = logging.FileHandler(log_file_name)
                file_handler.setLevel(file_log_numeric_level)
                file_handler.setFormatter(formatter)

                root_logger.addHandler(file_handler)

        return cls._instance

    @staticmethod
    def namedtuple_from_dict(obj):
        """Create a named tuple from a dictionary."""
        if isinstance(obj, dict):
            fields = sorted(obj.keys())
            namedtuple_type = namedtuple(
                typename="Config", field_names=fields, rename=True
            )
            field_value_pairs = OrderedDict(
                (str(field), Config.namedtuple_from_dict(obj[field]))
                for field in fields
            )
            try:
                return namedtuple_type(**field_value_pairs)
            except TypeError:
                # Cannot create namedtuple instance so fallback to dict (invalid attribute names)
                return dict(**field_value_pairs)
        elif isinstance(obj, (list, set, tuple, frozenset)):
            return [Config.namedtuple_from_dict(item) for item in obj]
        else:
            return obj

    @staticmethod
    def device() -> str:
        """Return the device to be used for training."""
        device = "cpu"

        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            if hasattr(Config().env, "device_id"):
                device = "cuda:" + str(Config().env.device_id)
            else:
                device = "cuda:" + str(np.random.randint(0, torch.cuda.device_count()))
        if torch.backends.mps.is_available():
            device = "mps"

        return device

    @staticmethod
    def items_to_dict(base_dict) -> dict:
        """
        Convert items of the dict to be dict if possible.

        The main purpose of this function is to address the
        condition of nested Config term, such as
        {"key1": Config(k11=5, k12=7),
         "key2": Config(k12=5, k22=Config(m=1, n=7))}
        """
        for key, value in base_dict.items():
            if not isinstance(value, dict):
                if hasattr(value, "_asdict"):
                    value = value._asdict()
                    value = Config().items_to_dict(value)
                    base_dict[key] = value
            else:
                value = Config().items_to_dict(value)
                base_dict[key] = value
        return base_dict

    @staticmethod
    def to_dict() -> dict:
        """Convert the current run-time configuration to a dict."""

        config_data = dict()
        config_data["train"] = Config.train._asdict()
        config_data["environment"] = Config.env._asdict()
        config_data["data"] = Config.data._asdict()
        config_data["model"] = Config.model._asdict()
        config_data["logging"] = Config.logging._asdict()
        config_data["evaluation"] = Config.eval._asdict()
        for term in [
            "train",
            "environment",
            "data",
            "model",
            "logging",
            "evaluation",
        ]:
            config_data[term] = Config().items_to_dict(config_data[term])

        return config_data

    @staticmethod
    def store() -> None:
        """Save the current run-time configuration to a file."""
        config_data = Config().to_dict()

        with open(Config.args.config, "w", encoding="utf8") as out:
            yaml.dump(config_data, out, default_flow_style=False)

    @staticmethod
    def create_sub_folders() -> None:
        """
        Create the basic save name for the current run-time configuration.
        This function is to create the unique name and will save the running
        details to the csv file under the config folder.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        run_id = Config.params["run_id"]

        # Example: 2023-10-05-14-30-45_6789
        data_name = Config.params["data_name"]
        model_name = Config.params["model_name"]
        group_name = f"{data_name}--{model_name}"
        unique_id = f"{timestamp}--{run_id}"

        return unique_id, group_name

    @staticmethod
    def set_records(status: str = "Incomplete") -> None:
        """
        Create the basic save name for the current run-time configuration.
        This function is to create the unique name and will save the running
        details to the csv file under the config folder.
        """
        record_path = Config.params["record_path"]

        # Create a new record for the current running
        # Use the pandas
        record_df = pd.DataFrame(
            {
                "base_path": [Config.params["base_path"]],
                "base_project_name": [Config.params["base_project_name"]],
                "user_project_name": [Config.params["user_project_name"]],
                "fix_project_name": [Config.params["fix_project_name"]],
                "project_name": [Config.params["project_name"]],
                "data_name": [Config.params["data_name"]],
                "model_name": [Config.params["model_name"]],
                "project_path": [Config.params["project_path"]],
                "exe_id": [Config.params["exe_id"]],
                "config_path": [Config.params["config_path"]],
                "status": status,
            }
        )
        # Define matching columns (first 10 keys)
        id_columns = record_df.columns.tolist()[:10]

        if not os.path.exists(record_path):
            # Create new file with headers
            record_df.to_csv(record_path, index=False)
        else:
            # Read existing data
            existing_df = pd.read_csv(record_path)

            # Check for matching ID
            mask = existing_df["exe_id"] == record_df.iloc[0]["exe_id"]
            if mask.any():
                # Update status for existing record(s)
                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                status = f"{status}@{timestamp}"
                existing_df.loc[mask, "status"] = status
                existing_df.to_csv(record_path, index=False)
            else:
                # Append new record
                record_df.to_csv(record_path, mode="a", header=False, index=False)