

import gc
gc.collect()

import os
import json
import time


from interface.basic.logger import Logging


# =========================== #
#       Files & Folders       #
# =========================== #


class Loc:
    extension: str = ""
    def __init__(self, path: str, name: str = None, is_logging: bool = None, style: str = None, **kwargs):
        self.path = path
        self.logging = Logging(name, is_logging, self, style=style)

    @property
    def exists(self):
        try:
            return os.stat(self.path).st_size > 0
        except FileNotFoundError:
            return False

    @classmethod
    def at(cls, name: str, extension: str | None = None, folder = None, is_logging: bool = None, style: str = None, **kwargs):
        extension = extension if extension is not None else cls.extension if not '.' in name else ''
        folder = str(folder) if folder is not None else None
        return cls(
            f"{folder if folder is not None else ''}{'' if folder is None or folder.endswith('/') else '/'}"
            + f"{name}{'.' if extension != '' else ''}{extension}",
            is_logging=is_logging, style=style, name=f"{cls.__name__}: '{name}'", **kwargs
        )

    def __str__(self):
        return self.path

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def read(self, message: str | None = None, encoding: str = "utf-8") -> dict | list | str | None:
        try:
            content = self._read(encoding)
            self.logging(
                f"Read {self.__class__.__name__}: {self.path}{' | ' + message if message is not None else ''}", level="SUCCESS"
            )
            return content
        except Exception as e:
            self.logging(
                f"Error when reading {self.__class__.__name__}: {self.path} | {e}{' | ' + message if message is not None else ''}",
                level="ERROR"
            )
            return None

    def write(self, data, message: str | None = None, encoding: str = "utf-8"):
        try:
            res = self._write(data, encoding)
            self.logging(
                f"Write {self.__class__.__name__}: {self.path}{' | ' + message if message is not None else ''}", level="SUCCESS"
            )
            return res
        except Exception as e:
            self.logging(
                f"Error when writing {self.__class__.__name__}: {self.path} | {e}{' | ' + message if message is not None else ''}",
                level="ERROR"
            )
            return False

    def append(self, data, message: str | None = None, encoding: str = "utf-8"):
        try:
            res = self._append(data, encoding)
            self.logging(
                f"Append {self.__class__.__name__}: {self.path}{' | ' + message if message is not None else ''}", level="SUCCESS"
            )
            return res
        except Exception as e:
            self.logging(
                f"Error when appending {self.__class__.__name__}: {self.path} | {e}{' | ' + message if message is not None else ''}",
                level="ERROR"
            )
            return False

    def _read(self, encoding: str = "utf-8"):
        ...

    def _write(self, data, encoding: str = "utf-8"):
        ...

    def _append(self, data, encoding: str = "utf-8"):
        ...

    def remove(self, message: str | None = None):
        try:
            os.remove(self.path)
            self.logging(
                f"Removed {self.__class__.__name__}: {self.path}{' | ' + message if message is not None else ''}", level="SUCCESS"
            )
        except Exception as e:
            self.logging(
                f"Error when removing {self.__class__.__name__}: {self.path} | {e}{' | ' + message if message is not None else ''}",
                level="ERROR"
            )


gc.collect()


class Folder(Loc):
    def _read(self, encoding: str = "utf-8"):
        return os.listdir(self.path)

    def _write(self, data, encoding: str = "utf-8"):
        raise NotImplementedError(f"{self.__class__.__name__}.write() is not implemented")

    def _append(self, data, encoding: str = "utf-8"):
        raise NotImplementedError(f"{self.__class__.__name__}.append() is not implemented")


gc.collect()


class JsonFile(Loc):
    extension = "json"

    def _read(self, encoding: str = "utf-8"):
        with open(self.path, 'r', encoding=encoding) as f:
            return json.load(f)

    def _write(self, data, encoding: str = "utf-8"):
        with open(self.path, 'w', encoding=encoding) as f:
            json.dump(data, f)
        return True

    def _append(self, data, encoding: str = "utf-8"):
        raise NotImplementedError(f"{self.__class__.__name__}.append() is not implemented")


gc.collect()


class TextFile(Loc):
    extension = "txt"

    def _read(self, encoding: str = "utf-8"):
        with open(self.path, 'r', encoding=encoding) as f:
            return f.read()

    def _write(self, data, encoding: str = "utf-8"):
        with open(self.path, 'w', encoding=encoding) as f:
            f.write(data)
        return True

    def _append(self, data, encoding: str = "utf-8"):
        with open(self.path, 'a', encoding=encoding) as f:
            f.write(data)
        return True


gc.collect()


# =========================== #
#           Settings          #
# =========================== #


class Settings:

    def __init__(self, file: JsonFile = None, phone=None, template: str | None= "default", name: str = "settings", **kwargs):
        self.file = file
        self.template = template
        self.phone = phone
        self.name = name

    """ Properties """

    @property
    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("file")
        data.pop("phone")
        data.pop("name")
        return data

    @property
    def templates(self) -> list[str]:
        data = self.file_read()
        data = list(data.keys())
        if "template" in data:
            data.remove("template")
        return data

    """ Reading / Writing """

    def file_read(self) -> dict:
        if self.file is None:
            return {}
        data = self.file.read(f"Reading {self.__class__.__name__}")
        if data is None:
            return {}
        return data

    def file_write(self, data: dict) -> None:
        if isinstance(self.file, JsonFile):
            self.file.write(data, message=f"Saving {self.__class__.__name__}")

    def wifi_read(self) -> dict:
        if self.phone is None:
            return {}
        config = self.phone.get_data(self.name)
        if not config:
            return {}
        return config

    def wifi_write(self, data: dict) -> None:
        if self.phone is not None:
            self.phone.write(**{self.name: data})

    def _add_template(self, config: dict):
        if self.file and config:
            data = self.file_read()
            name = config.get("template", "")
            if name is not None:
                if name not in data:
                    data[name] = config
                else:
                    for key, value in config.items():
                        data[name][key] = value
                data["template"] = name
            self.file_write(data)

    def _set_template(self, config: dict):
        if not config:
            return
        for name, value in config.items():
            if hasattr(self, name):
                setattr(self, name, value)

    """ User """

    def download(self) -> 'Settings':
        """ Download data from phone and save to file and load. """
        config = self.wifi_read()
        if not config:
            return self
        print(config)
        self._add_template(config)
        self._set_template(config)
        return self

    def load(self, value: str | None = None) -> 'Settings':
        """ Pick a template from local and update current data. """
        data = self.file_read()
        if not data:
            return self
        value = value if value is not None else data.get("template", "default")
        if value in data:
            self._set_template(data.get(value))
        return self

    def upload(self, value: str | None = None) -> 'Settings':
        """ Send template to phone. """
        data = self.file_read()
        value = value if value is not None else data.get("template", "default")
        if value in data:
            self.wifi_write(data.get(value))
        return self

    def remove(self, value: str) -> 'Settings':
        """ Remove template and initialize again. """
        data = self.file_read()
        if value in data:
            data.pop(value)
            if data.get("template") == value:
                data.pop("template")
        self.file_write(data)
        self.initialise()
        return self

    def initialise(self) -> 'Settings':
        data = self.file_read()
        value = data.get("template") if self.template is None else self.template
        if not value:
            return self
        self._set_template(data.get(value))
        return self

    def save(self) -> 'Settings':
        if isinstance(self.file, JsonFile):
            self.file.write({self.template: self.to_dict}, message=f"Saving template '{self.template}' of {self.__class__.__name__}")
        return self

    """ Making it. """

    @staticmethod
    def make_file(name: str, path: str = None, folder = None, is_logging: bool = None, style: str = None):
        if isinstance(path, str):
            file = JsonFile(path=path, name=name, is_logging=is_logging, style=style)
        else:
            file = JsonFile.at(name=name, folder=folder, is_logging=is_logging, style=style)
        return file

    @classmethod
    def from_file(cls, file: JsonFile | None = None, name: str | None = None, path: str | None = None, folder = None,
                  is_logging: bool = None, style: str = None, **kwargs):
        file = cls.make_file(name=name, path=path, folder=folder, is_logging=is_logging, style=style) if name is not None else file

        data = file.read(message=f"Getting {cls.__name__}")
        if not isinstance(data, dict):
            return cls(file=file, **kwargs)

        data.update(kwargs)
        return cls(file=file, **data)

    def save_as(self, name: str, path: str = None, folder = None, is_logging: bool = None, style: str = None):
        file = self.make_file(name=name, path=path, folder=folder, is_logging=is_logging, style=style)
        instance = self.__class__(file=file, **self.to_dict)
        instance.save()
        return instance

    def open(self, data: dict | None = None):
        if isinstance(self.file, JsonFile) and data is None:
            data = self.file.read(message=f"Getting {self.__class__.__name__}")
        if not isinstance(data, dict):
            return
        for key, value in data.items():
            if key in self.to_dict.keys():
                setattr(self, key, value)


gc.collect()


# =========================== #
#           Logging           #
# =========================== #


class LogFile(TextFile):

    def __init__(self, path: str, name: str = None, **kwargs):
        super().__init__(path, name=name, is_logging=False)
        self.started = self.exists

    def __call__(self, data: dict):
        return self.log(data)

    def log(self, data: dict):
        if self.started:
            self.append(data)
            return True
        else:
            self.started = self.write(data)
            return self.started

    def _read(self, encoding: str = "utf-8"):
        with open(self.path, 'r', encoding=encoding) as f:
            return json.loads("[\n" + f.read() + "\n]")

    def _write(self, data: dict, encoding: str = "utf-8"):
        with open(self.path, 'w', encoding=encoding) as f:
            f.write(json.dumps(data))
        return True

    def _append(self, data: dict, encoding: str = "utf-8"):
        with open(self.path, 'a', encoding=encoding) as f:
            f.writelines("," + json.dumps(data))
        return True


gc.collect()


class LogManager(Folder):

    def __init__(self, path: str, name: str = None, is_logging: bool = None, style: str = None,
                 naming: str = "log", size: int = 5000, amount: int = 5, make_new: bool = True, clock=None):
        super().__init__(path, name=name, is_logging=is_logging, style=style)
        self.name = naming
        self.size = size
        self.amount = amount
        self.clock = clock
        self.make_new = make_new

        # Make new file if new document
        if make_new:
            self.new_file()

    @property
    def files(self):
        fs = self.read()
        if not isinstance(fs, list):
            return []
        files = []
        for file in fs:
            if file.endswith(".txt"):
                files.append(LogFile.at(file, folder=self))
        return files

    @property
    def now(self):
        date = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(*time.localtime()[:6]) if self.clock is None else self.clock.iso
        return date.replace(":", "_").replace("-", "_")

    def continue_on_file(self):
        # Get file
        if len(self.files) == 0:
            file = LogFile.at(f"{self.name}_{self.now}", folder=self)
            self.files.append(file)
        else:
            file = self.files[-1]
            try:
                if os.stat(file.path).st_size > self.size:
                    self.files.append(LogFile.at(f"{self.name}_{self.now}", folder=self))
            except FileNotFoundError:
                pass
            while len(self.files) > self.amount:
                self.files[0].remove()
        return file

    def new_file(self):
        file = LogFile.at(f"{self.name}_{self.now}", folder=self)

        while len(self.files) > self.amount:
            self.files[0].remove()
        return file

    def log(self, data: dict):
        # Make new file if new document
        if self.make_new:
            file = self.new_file()
            self.make_new = False
        else:
            file = self.continue_on_file()
        # Log to file
        return file.log(data)

    def __call__(self, data: dict):
        return self.log(data)


gc.collect()

