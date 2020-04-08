"""

This Module provides some Function which are considered util. They are not necessary to run the code but ease it a lot.

In total the following different Utilities classes are provided:
 - Logger: this class initializes a logging instance which can be used to log all activities.
 - ClassAttrHandler: this class provides some functionalities with respect to classes and their respective attributes.
 - Decorators: this class provides a set of different Decorators which can be used to add functionalities to functions

"""
from os.path import isdir, join
from os import makedirs, stat, environ, getcwd
import logging
from sys import stdout
from random import random
import time
from datetime import datetime
import json
import yaml
import re
from shutil import rmtree
from functools import wraps
from pathlib import Path

"""
Contains:
- Logger
- yml_reader
- get_date
- Dict_to_object
- Class Attribute Handler
- Decorator
    - run_time
    - show_args
    - counter
    - retry
    - retry_with_exponential_stalling
    - accepted_args
    - accepted_args_classes
    - accepted_args_type
    - container_non_empty
    - class_has_object
- Size
- Project_structure Displayer
- SubstringFinder
- Date_Filterer
- Project_Initializer
"""


def read_config(conf, obj_notation=False):
    with open(conf, "r") as stream:
        config = yaml.safe_load(stream)
    return config if not obj_notation else Dict_to_Obj(config)


class Logger:
    """
    This class adds a logging instance which can be imported in other modules and used to track code and activities.
    All logs to are written to stdout and also in a logging file. The logging file is identified via a timestamp and written into ./logs/

    Usage: Import this class at the beginning of a module. You can then access the log attribute and use it as a logging instance
    Example:
        File: Costume_Module_py

        1 from Utilities import Logger
        2 log = Logger.log
        ...
        10. log.info('Control is here')
        ...
        18 log.error('Function "foo()" did not return a valid value')
    """

    if not isdir("logs"):
        makedirs("logs")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s,%(msecs)d - file: %(module)s  - func: %(funcName)s - line: %(lineno)d - %(levelname)s - msg: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(
                join(
                    "logs",
                    "log_{0}_{1}".format(
                        __name__, time.strftime("%Y-%m-%d", time.gmtime())
                    ),
                )
            ),
            logging.StreamHandler(stdout),
        ],
    )
    log = logging.getLogger(__name__)


# This module itself also uses a logging instance.
log = Logger.log


def get_date():
    return datetime.now().date().isoformat()


class Dict_to_Obj:
    """
    This class constructs an object notation out of a dictionary.
    """

    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b) if isinstance(b, dict) else b)


class ClassAttrHandler(object):
    """
    This class provides some functionalities with respect to class instance attributes.
    Additional functionalities allow iterating over the object, transform all container attributes to their corresponding
    size, deleting empty attributes and getting a list of strings containg all attributes label or attribute values.
    Usage: costume classes can inherit from this class in order to have additional functionalities with respect to attributes.
    Example:
        File: Costume_Module_py

        1 class Myclass(ClassattrHandler):
        2   def __init__(self,attribute_1, attribute_2):
        3       self.attribute_1 = attribute_1
        4       self.attribute_2 = attribute_2
        5       self.all_string_attributes = self.__get_attributes_values(str)
        6
        7   def foo(self):
        8       for attr_label, attr_value in self:
        9           ....
    """

    def __iter__(self):
        """
        Enables class attributes to be iterated over. Simply let the target class this class.
        Class attributes can then be iterated over by using a for loop.

        Example:
            def Myclass(ClassattrHandler):
                def __init__(....

                def iterage_over_attibutes(self):
                    for attr, value in self:
                        ...

        In this Example, the class "Myclass" inherits the ClassAttrHandler which therefore allows it to iterate over its attributes.
        This is achieved via a "for ... in self" loop which yields the attributes and the corresponding value
        """
        for attr, value in self.__dict__.items():
            yield attr, value

    def _return_container_size(self):
        """
        Transforms all class instances attributes of container type into its corresponding length.

        :return: all attributes represent their length value
        """
        for i in self:
            if Decorators._is_container(i[0]):
                self.__dict__[i[0]] = len(i[1])
            else:
                self.__dict__[i[0]] = "No Container attribute"

    def _delete_empty_attributes(self):
        """
        Drop all attributes which are empty from the instance.

        :return: the same object which no longer has any empty attribute
        """
        attrs_to_delete = [val for val, attr in self if not attr]
        for attr in attrs_to_delete:
            delattr(self, attr)

    def _get_attributes_labels(self, attr_type=None):
        """
        Returns a list of an object's attributes labels. If provided with attr_type, only attributes labels of a certain type are written into the list

        :param attr_type: Optional argument to restrict the attribute list to attributes of the given type.
        :return: a list of strings containing all attributes labels
        """
        return (
            [attr_label for attr_label, attr_val in self]
            if not attr_type
            else [
                attr_label
                for attr_label, attr_val in self
                if isinstance(attr_val, attr_type)
            ]
        )

    def _get_attributes_values(self, attr_type=None):
        """
        Returns a list of an object's attributes values. If provided with attr_type, only attributes values of a certain type are written into the list

        :param attr_type: Optional argument to restrict the attribute list to attributes of the given type.
        :return: a list of strings containing all attributes values
        """
        return (
            [attr_val for attr_label, attr_val in self]
            if not attr_type
            else [
                attr_val
                for attr_label, attr_val in self
                if isinstance(attr_val, attr_type)
            ]
        )


class Decorators:
    """
    This class provides a set of functionalities with respect to decorate functions. These decorators are considered
    util as they prevent to repeat the same code, add functionalities to a function on the fly, allows a lot of type
    and input checking and so on.

    All the functions defined inside this class take a function as an input and return a decorated function.
    """

    @staticmethod
    def run_time(func):
        """
        When decorating a function with this decorator, it indiactes the function's run time in a hh:mm:ss after
        the function returns

        Example:
            @Decorators.run_time
            1 def foo(x):
                ....
            10 foo(10)
            11

        :param func: function to decorate
        :return: decorated function which indicates function run time
        """
        assert callable(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            end = time.time()
            m, s = divmod(end - start, 60)
            h, m = divmod(m, 60)
            ms = int(s % 1 * 1000)
            s, m, h = int(round(s, 0)), int(round(m, 0)), int(round(h, 0))
            log.info(
                f'Execution Time (hh:mm:sec) for function "{func.__name__}": {h:02d}:{m:02d}:{s:02d},{ms:03d}'
            )
            return ret

        return wrapper

    @staticmethod
    def show_args(func):
        """
        When decorating a function with this decorator, it indicates the arguments passed to the function.

        Example:
            @Decorators.show_args
            1 def foo(x):
                ....
            10 foo(10)
            11

        :param func: function to decorate
        :return: decorated function which indicates function's arguments
        """
        assert callable(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            log.info(f"Executing '{func.__name__}' with args {args} and {kwargs}")
            ret = func(*args, **kwargs)
            return ret

        return wrapper

    @staticmethod
    def counter(func):
        """
        When decorating a function with this decorator, it indicates how often the function has been called.

        Example:
            @Decorators.show_args
            1 def foo(x):
                ....
            10 foo(10)
            11

        :param func: function to decorate
        :return: decorated function which indicates how often the function has been called
        """
        assert callable(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.count = wrapper.count + 1
            res = func(*args, **kwargs)
            log.info(
                f"Number of times '{func.__name__}' has been called: {wrapper.count}x"
            )
            return res

        wrapper.count = 0
        return wrapper

    @staticmethod
    def retry(
        times, delay,
    ):
        """
        When decorating a function with this decorator, it tries to execute it. If the function returns sucessfully,
        control is passed to the code right after the function. If however, a function fails to return sucessfully,
        it is called once more until trying to succesfully finish it. This procedure is repeated until the functions
        returns sucessfully or if the number of limits of retries is hit. Furthermore, the delay parameters adds
        a sleeping time after each try.

        Target: This decorator is useful for functions which performs requests from the Internet. For instance, if a server
        is temporarily unreachable, the request is requested in a fixed delay after the first failure.

        :param times: how many tries to execute the function
        :param delay: waiting period between two function calls
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                t = 1
                while t <= times:
                    try:
                        log.info(f'Trying to execute "{func.__name__}" ({t}/{times})')
                        res = func(*args, **kwargs)
                        log.info(f'Succesfully executed "{func.__name__}".')
                        return res
                    except Exception as e:
                        log.warning("Execution failed for the following reason:", e)
                        t += 1
                        if t <= times:
                            time.sleep(delay)
                        else:
                            log.error(
                                f'Function "{func.__name__}" could not be executed after {times} tries'
                            )

            return wrapper

        return decorator

    @staticmethod
    def retry_with_exponential_stalling(times, white_noise=False):
        """
        When decorating a function with this decorator, it tries to execute it. If the function returns sucessfully,
        control is passed to the code right after the function. If however, a function fails to return sucessfully,
        it is called once more until trying to succesfully finish it. This procedure is repeated until the functions
        returns sucessfully or if the number of limits of retries is hit. Furthermore, the delay parameters adds
        a sleeping time after each try.

        Target: This decorator is useful for functions which performs requests from the Internet. For instance, if a server
        is temporarily unreachable, the request is requested in a fixed delay after the first failure.

        :param times: how many tries to execute the function
        :param delay: waiting period between two function calls
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                t, delay = 1, 2 if not white_noise else 2 + random()
                while t <= times:
                    try:
                        log.info(f'Trying to execute "{func.__name__}" ({t}/{times})')
                        res = func(*args, **kwargs)
                        log.info(f'Succesfully executed "{func.__name__}".')
                        return res
                    except Exception as e:
                        log.warning("Execution failed for the following reason:", e)
                        t += 1
                        if t <= times:
                            log.info(
                                f"Stalling {round(delay, 3)} secs before next execution try."
                            )
                            time.sleep(delay)
                            delay *= 2
                        else:
                            log.error(
                                f'Function "{func.__name__}" could not be executed after {times} tries'
                            )

            return wrapper

        return decorator

    @staticmethod
    def accepted_arguments(accepted_args: list):
        """
        When decorating a function with this decorator, the function's arguments are checked against a list of valid arguments.
        If an invalid argument is encoutered, the function is not executed.

        :param accepted_args:
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args):
                try:
                    assert all([a in accepted_args for a in args])
                except AssertionError:
                    raise SyntaxError(
                        f"Encountered a non-valid argument.\nValid arguments are: {accepted_args}"
                    )
                result = func(*args)
                return result

            return wrapper

        return decorator

    @staticmethod
    def accepted_arguments_within_classes(accepted_args):
        """
        When decorating a function with this decorator, the function's arguments are checked against a list of valid arguments.
        If an invalid argument is encoutered, the function is not executed. This decorator is basically the same as "accepted_arguments"
        decorator except that it is aimed for functions within classes (i.e. containg a "self" parameter). In these setup, the class instance
        itself is passed as the first argument. Therefore, this Decorator only checks the second till last argument for correctness.

        :param accepted_args:
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args):
                try:
                    assert all([a in accepted_args for a in args[1:]])
                except AssertionError:
                    raise SyntaxError(
                        f"Encountered a non-valid argument.\nValid arguments are: {accepted_args}"
                    )
                result = func(*args)
                return result

            return wrapper

        return decorator

    @staticmethod
    def accepted_argument_types(*decorator_args):
        """
        When decorating a function with this decorator, the function's arguments types are checked against a list of valid types.
        The types are provided in the same order as the corresponding arguments such that they match.

        :param decorator_args:
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                check_args = dict(zip(decorator_args, args))
                for argument_types, arguments in check_args.items():
                    try:
                        assert isinstance(arguments, argument_types)
                    except AssertionError:
                        raise TypeError(
                            f"Argument Types do not match expected types.\nExpected {type(arguments)} but got {argument_types}"
                        )
                result = func(*args, **kwargs)
                return result

            return wrapper

        return decorator

    @staticmethod
    def class_object_has_attr(attribute):
        """
        When decorating a class method with this function, it checks if the class instance has a given attribute.
        It allows chaining to get deep levels of attributes. Note that this decorator can only be used by class methods.

        :param attribute:
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    assert has_deep_attr(args[0], attribute)
                    result = func(*args, **kwargs)
                    return result
                except AssertionError:
                    log.error(
                        f"The object '{object}' does not have the required attribute {attribute}."
                    )

            return wrapper

        return decorator

    @classmethod
    def container_non_empty(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for argument in args:
                if cls._is_container(argument):
                    cls._check_if_empty_container(argument)
            result = func(*args, **kwargs)
            return result

        return wrapper

    @staticmethod
    def _is_container(obj):
        return hasattr(type(obj), "__iter__")

    @staticmethod
    def _check_if_empty_container(obj):
        """ to be added"""
        obj_type = type(obj)
        cond = {
            list: len,
            dict: len,
            str: len,
            tuple: len,
            set: len,
            # np.ndarray : np.size,
            # pd.core.frame.DataFrame : len, #or pd.core.frame.DataFrame.empty
        }
        func = cond[obj_type]
        if not func(obj):
            raise IndexError(f"Container {obj} is empty")


def get_deep_attr(obj, attrs):
    """
    This function is a helper function which allows attributes checking for nested/composed attributes.

    :param obj:
    :param attrs:
    :return:
    """
    for attr in attrs.split("."):
        obj = getattr(obj, attr)
    return obj


def has_deep_attr(obj, attrs):
    """
    This function is a helper function which allows attributes checking for nested/composed attributes.

    :param obj:
    :param attrs:
    :return:
    """
    try:
        get_deep_attr(obj, attrs)
        return True
    except AttributeError:
        return False


def convert_bytes(num):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0


def file_size(file):
    file_info = stat(file)
    return convert_bytes(file_info.st_size)


class DisplayablePath(object):
    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(
            list(path for path in root.iterdir() if criteria(path)),
            key=lambda s: str(s).lower(),
        )
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(
                    path, parent=displayable_root, is_last=is_last, criteria=criteria
                )
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))


def display_tree(directory):
    paths = DisplayablePath.make_tree(Path(directory))
    with open("project_dir.txt", "a") as myfile:
        for path in paths:
            myfile.write(path.displayable())


class Date_Filterer:
    def __init__(self, items, delta_days):
        self.items = items
        self.delta_days = delta_days
        self.unique_write_days = []
        self.days_to_delete = []

    @staticmethod
    def as_date_time(date_str):
        return datetime.strptime(date_str, "%Y-%M-%d")

    @staticmethod
    def extract_date_from_name(file: str) -> str:
        """
        Function used to extract the datetime in a filename

        :param file: string of the filename
        :type file: str
        :return: a substring containing the datetime in YYYYMMDD_HHMM format
        :rtype: str
        """
        try:
            date_time = re.search("^\d{4}[.-]\d{2}[.-]\d{2}\/?", file).group(0)
            return date_time[:-1]
        except AttributeError:
            return ""

    def get_unique_write_days(self):
        self.unique_write_days = sorted(
            list(
                set(
                    [
                        self.extract_date_from_name(file)
                        for file in self.items
                        if self.extract_date_from_name(file)
                    ]
                )
            )
        )
        log.info(
            f"The following unique days of data writes have been found {self.unique_write_days}"
        )
        return self

    def get_days_to_delete(self):
        if self.unique_write_days:
            newest_writes = self.unique_write_days[-1]
            log.info(f"Most recent write is from {newest_writes}")
            older_writes = self.unique_write_days[:-1]
            log.info(f"Last recent write is from {self.unique_write_days[0]}")
            self.days_to_delete = [
                day
                for day in older_writes
                if (self.as_date_time(newest_writes) - self.as_date_time(day)).days
                >= self.delta_days
            ]
            return self

    def get_files_to_delete(self):
        files_to_delete = [
            file
            for file in self.items
            if any([file.startswith(day) for day in self.days_to_delete])
        ]
        if files_to_delete:
            log.info(
                f"The following files are about to be deleted as they are {self.delta_days} days apart from the recent writes:\n {files_to_delete}"
            )
        else:
            log.info(
                f"No files were found that would have been deleted as they are {self.delta_days} days apart from the recent writes."
            )
        return files_to_delete

    def get_final_files(self):
        return self.get_unique_write_days().get_days_to_delete().get_files_to_delete()


class SubstringFinder(Logger):
    """
    Class which contains some methods for grouping regex operations on strings to identify predefined values within the strings
    """

    @staticmethod
    def extract_datetime(file: str) -> str:
        """
        Function used to extract the datetime in a filename

        :param file: string of the filename
        :return: a substring containing the datetime in YYYYMMDD_HHMM format
        """
        try:
            date_time = re.search("\d{8}[_-]\d{4,6}", file).group(0)
            if "-" in date_time:
                date_time = date_time.replace("-", "_")
            return date_time
        except AttributeError:
            return ""

    @staticmethod
    def extract_date_from_name(file: str) -> str:
        """
        Function used to extract the datetime in a filename

        :param file: string of the filename
        :type file: str
        :return: a substring containing the datetime in YYYYMMDD_HHMM format
        :rtype: str
        """
        try:
            date_time = re.search("^\d{4}[.-]\d{2}[.-]\d{2}\/?", file).group(0)
            return date_time[:-1]
        except AttributeError:
            return ""

    @staticmethod
    def extract_date(file: str) -> str:
        """
        Function used to extract the date in a filename

        :param file: string of the filename
        :return: a substring containing the date in YYYYMMDD format
        """
        date_time = SubstringFinder.extract_datetime(file)
        try:
            date = re.search("\d{8}", date_time).group(0)
            return date
        except AttributeError:
            return ""

    @staticmethod
    def extract_time(file: str) -> str:
        """
        Function used to extract the time in a filename

        :param file: string of the filename
        :return: a substring containing the time in HHMM format
        """
        date_time = SubstringFinder.extract_datetime(file)
        try:
            time = re.search("[_-]\d{4,6}", date_time).group(0)
            time = time[1:]
            return time
        except AttributeError:
            return ""


class Project_Initializer(Logger):
    # def create makefile
    def __init__(
        self,
        user=environ["USERNAME"],
        e_mail="John.Doe@ibm.com",
        python_version="3.7",
        main_file="app.py",
        root_dir=getcwd(),
        dirs=["data", "logs", "models", "reports", "src", "docs", "ims"],
        requirements=True,
        docker=True,
        readme=True,
        conda_env=True,
    ):
        self.user = user
        self.e_mail = e_mail
        self.python_version = python_version
        self.main_file = main_file
        self.root_dir = root_dir
        self.dirs = dirs
        self.requirements = requirements
        self.docker = docker
        self.readme = readme
        self.conda_env = conda_env
        self.log.info(
            """You just initiliazed a Machine Learning project creater instance. Usage is as follows:
        1. Option: You can create a standardized Project by calling OBJECT.standard_initialization
        2. Option: You may modifiy different steps by changing function's input. Recommended function calling is therefore:
        OBJECT.create_standard_directories()
        OBJECT.create_standard_sub_directories()
        OBJECT.create_mainfile()
        OBJECT.create_requirements(#add your costume packages here)
        OBJECT.create_docker_file()
        OBJECT.create_ReadMe()
        OBJECT.create_Conda_env(#add jupyter launcher here of wanted)
        OBJECT.create_Sphinx_ToDo_list()
        """
        )

    def create_directory(self, directory):
        if not isdir(directory):
            makedirs(directory)
            self.log.info("Created directory {0}".format(directory))
        else:
            self.log.info("Directory {0} already exists".format(directory))

    def create_docker_file(self):
        docker_cmd = """
        FROM python:{0} 
        MAINTAINER {1} "{2}"
        RUN mkdir /app
        COPY . /app
        WORKDIR /app
        RUN echo "Following dependencies will be installed"
        RUN cat requirements.txt
        RUN pip install -r requirements.txt
        RUN ls /app/src
        ENTRYPOINT ["python"] 
        CMD ["src/{3}" ]
        """.format(
            self.python_version, self.user, self.e_mail, self.main_file
        )
        with open("Dockerfile", "w") as docker:
            docker.write(docker_cmd)

    def create_requirements(
        self,
        standard_packages=[
            "pandas==0.24.2",
            "numpy==1.16.2",
            "seaborn",
            "matplotlib==3.0.3",
            "scikit-learn==0.20.3",
            "jupyterlab==0.35.4",
        ],  # sphinx
        add_packages=[],
    ):
        all_packages = standard_packages + add_packages
        packages_writer = "\n".join(all_packages)
        with open("requirements.txt", "w") as require:
            require.write(packages_writer)

    def create_Conda_env(self, env_name, jupyter, conda_path):
        try:
            assert env_name
        except AssertionError:
            self.log.error("You did not specify an environment name")
        self.conda_env_name = env_name
        if not conda_path:
            conda_activate = environ["CONDA_PREFIX_1"]
        else:
            conda_activate = join(conda_path)
        if not isfile("requirements.txt"):
            raise FileExistsError(
                "No requirements.txt file has been found. Please ensure that file exists with corresponding requirements"
            )
        env_cmd = """
@echo off
call {0}\\Scripts\\activate.bat
call conda create --name {1} --yes
call conda activate {1}
FOR /F "delims=~" %%f in (requirements.txt) DO call conda install --yes "%%f" || call conda install --yes -c conda-forge "%%f" || call pip install "%%f"
echo All requirements have been installed
echo You can safely delete this file now
cmd /K
        """.format(
            conda_activate, env_name
        )
        with open("setup_conda_env.bat", "w") as env_setup:
            env_setup.write(env_cmd)
        self.log.info(
            'Created "setup_conda_env.bat" batch file for generating conda environment'
        )
        if jupyter:
            try:
                assert jupyter in ["lab", "notebook"]
            except AssertionError:
                self.log.error(
                    'Jupyter kernels can only be called via "lab" or "notebook". Please use one of them.'
                )
            self.create_Jupyter_launcher(conda_activate, jupyter)

    def create_Jupyter_launcher(self, conda_activate, jupyter_instance):
        self.log.info(
            "Please ensure that Jupyter lab/notebook is defined in the requirements.txt file"
        )
        jupyter_cmd = """
call {0}\\Scripts\\activate.bat
call conda activate {1}
call jupyter {2}
        """.format(
            conda_activate, self.conda_env_name, jupyter_instance
        )
        with open("launch_jupyter.bat", "w") as jupyter:
            jupyter.write(jupyter_cmd)
        self.log.info(
            'Created "launch_jupyter.bat" batch file for launching a Jupyter lab'
        )

    def create_ReadMe(self):
        readme_cmd = """
# Application
# Prerequisites
python >= {0}
# Documentation
Add documentation info here
# Usage
# Author
Author of this repo = {1}
Contact Information = {2}
        """.format(
            self.python_version, self.user, self.e_mail
        )
        with open("README.md", "w") as readme:
            readme.write(readme_cmd)
        self.log.info("Created a README.md file")

    def create_MainFile(self):
        assert isdir("src")
        open(self.main_file, "a").close()

    def create_standard_directories(self):
        for d in self.dirs:
            self.create_directory(d)

    def create_standard_sub_directories(self):
        self.create_data_sub_dirs()
        self.create_src_sub_dirs()

    def create_data_sub_dirs(self, sub_dirs=["raw", "external", "processed"]):
        assert isdir("data")
        for sub_d in sub_dirs:
            d = join("data", sub_d)
            if not isdir(d):
                makedirs(d)
                self.log.info("Created directory {0}".format(d))
            else:
                self.log.info("Directory {0} already exists".format(d))

    def create_src_sub_dirs(self, sub_dirs=["exploration", "models", "visualisation"]):
        assert isdir("src")
        for sub_d in sub_dirs:
            d = join("src", sub_d)
            if not isdir(d):
                makedirs(d)
                self.log.info("Created directory {0}".format(d))
            else:
                self.log.info("Directory {0} already exists".format(d))

    def create_Sphinx_ToDo_list(self):
        sphinx_todo = """
    Some common options for using the Sphinx documentation module.
    1. "conf.py":
        This file contains configuration for the makefile. Some costume options can be added here to costumize the Sphinx documentation module.

        a.) PATH: you might need to hard code the path of the module if extensions and modules are not in the same directory. The command for inserting $MYPATH$ is
        sys.path.insert(0, os.path.abspath($MYPATH$))
        b.) Extensions: Any costume Sphinx extensions can be added here to enhance the documentation quality. The following commands adds some general extensions:
        extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.ifconfig',
        'sphinx.ext.viewcode',
        'sphinx.ext.autosummary',
        'sphinx.ext.inheritance_diagram',
        'sphinx.ext.graphviz'
        ]
        c.) Include_init_code: by default, Sphinx does not display the documentation for __init__ functions of classes. Add the following command to include it:
        def skip(app, what, name, obj, would_skip, options):
            if name == "__init__":
                return False
            return would_skip
    2. "DOCUMENTATION.rst":
        This file contains the documentation code. It should explain all the different tasks, dependencies and structure of the module. Though it is autogenerated
        by the Sphinx module, some general usages for source code documentation can be shown here:

        a.) Modules and classes: to include a module within all its classes, you can use the following exemplary commands. This example is taken for a module 
        called "Data_Manager_Helper" using the two classes "Cloudant_Table_Manager" and "Cloudant_Tables"
        .. automodule:: Data_Manager_Helper
        .. autoclass:: Cloudant_Tables
            :members:
        .. autoclass:: Cloudant_Table_Manager
            :members:
        b.) Autosummary: can be used to include summaries of structured which are not composed of classes. For instance, the Module "GlobalConstants"
        contains the credentials for a Cloudant instance, stored in "_Cloudant_Credentials"
        .. autosummary::
            GlobalConstants._Cloudant_Credentials
            """
        with open("sphinx_hints.txt", "w") as sphinx:
            sphinx.write(sphinx_todo)

    def standard_initialization(self, add_jupyter_launcher=True):
        self.log.info("Setting up whole Machine Learning project parts")
        self.create_standard_directories()
        self.create_standard_sub_directories()
        if self.requirements:
            self.create_requirements()
        if self.docker:
            self.create_docker_file()
        if self.readme:
            self.create_ReadMe()
        if self.conda_env:
            self.create_Conda_env(jupyter="lab")
        self.log.info("Finished setting up all parts")
