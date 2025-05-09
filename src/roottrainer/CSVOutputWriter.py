import os
import sys
from datetime import datetime
from typing import TextIO

import yaml
from pathlib import Path

from utils.utils import get_filename_from_path

config_path: str = ""
if len(sys.argv) > 1:
    config_path = str(sys.argv[1])
if config_path == "":
    config_path = "./config/config.yml"
config_filename: str = get_filename_from_path(config_path)
config = yaml.safe_load(open(config_path))


class CSVOutputWriter:
    def __init__(self, output_dir: str):
        self.output_dir: str = output_dir
        self.file: TextIO | None = None
        self.work_dir: Path = Path(__file__).parent.parent.parent

    def __del__(self):
        self.close()

    def open(self,
             file_name: str = "{}-{}-{}.csv".format(
                 config_filename,
                 config['simulation']['round'],
                 datetime.now().strftime("%Y-%m-%d-%H-%M-%S")),
             truncate: bool = True):
        """
        Open the file with `file_name`. If `truncate`, will clear file content before writing.
        :param file_name: the name of the file to be written on.
        :param truncate: whether to clear file content before writing or not.
        :return:
        """
        Path(self.work_dir / self.output_dir).mkdir(parents=True, exist_ok=True)
        mode: str = 'w' if truncate else 'a'
        # print(os.chdir(self.work_dir))
        self.file = open(self.work_dir / (self.output_dir + "/" + file_name), mode)

    def write(self, texts: list[any], separator: str = ',', newline: bool = True):
        for text in texts[:-1]:
            self.file.write(str(text) + separator)
        self.file.write(str(texts[-1]) + ('\n' if newline else ''))

    def close(self):
        if self.file is not None:
            self.file.close()
            print(os.path.realpath(self.file.name))
