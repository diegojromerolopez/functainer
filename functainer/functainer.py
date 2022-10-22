from pathlib import Path
from typing import List, Optional, Callable, Dict

import docker
import inspect
import os
import re
import tempfile

from docker.models.images import Image

from functainer.exceptions import FunctainerException


class Functainer:
    @classmethod
    def __assert(cls, cond: bool, exc_msg: str):
        if not cond:
            raise FunctainerException(exc_msg)

    def __init__(self, function: Callable[[], None]):
        self.__function = function
        self.__image: Optional[Image] = None
        self.__output_file_path: Optional[Path] = None
        self.__docker_client = docker.from_env()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()

    def build(self, image_tag: str, from_image: str = 'python:latest',
              requirements: Optional[List[str]] = None,
              build_container_kwargs: Optional[Dict] = None
              ):
        self.__assert(self.__docker_client is not None, exc_msg='docker client is not initialized')

        if requirements is None:
            requirements = []

        if build_container_kwargs is None:
            build_container_kwargs = {
                'nocache': False,
                'tag': image_tag
            }

        try:
            self.__image = self.__docker_client.images.get(name=image_tag)
        except docker.errors.DockerException:
            self.__image, _ = self.__docker_client.images.build(
                path=os.path.dirname(os.path.realpath(__file__)),
                buildargs={'FROM_IMAGE': from_image, 'REQUIREMENTS': ' '.join(requirements)},
                **build_container_kwargs
            )

    def run(self, python_command: str = 'python3', run_container_kwargs: Optional[Dict] = None):
        self.__assert(self.__docker_client is not None, exc_msg='docker client is not initialized')
        self.__assert(self.__image is not None, exc_msg='image is not built yet')

        if run_container_kwargs is None:
            run_container_kwargs = {}

        func_code = self.__function_code()

        # Prepare executor file contents based on the template
        current_dir_path = os.path.dirname(os.path.abspath(__file__))
        executor_file_path = os.path.join(current_dir_path, 'executor.py.tpl')
        with open(executor_file_path) as executor_file:
            executor_file_contents = executor_file.read()
            executor_file_contents = executor_file_contents.replace('__function_definition__', func_code)
            executor_file_contents = executor_file_contents.replace('__function_call__', self.__function.__name__)

        # Write executor file (replaced) contents in a temporal file
        with tempfile.TemporaryDirectory() as temp_dir_path:
            temp_executor_file_path = os.path.join(temp_dir_path, 'executor.py')
            with open(temp_executor_file_path, 'w') as temp_executor_file:
                temp_executor_file.write(executor_file_contents)

            # Create a temporal file that will be used to write the output of the container
            output_fd, self.__output_file_path = tempfile.mkstemp(text=False)

            self.__docker_client.containers.run(
                image=self.__image,
                command=f'{python_command} /tmp/functainer_temp/executor.py',
                volumes=[
                    f'{temp_dir_path}:/tmp/functainer_temp',
                    f'{self.__output_file_path}:/tmp/functainer_output'
                ],
                remove=True,
                user=f'{os.getuid()}:{os.getgid()}',
                **run_container_kwargs
            )

    @property
    def output_file_path(self):
        self.__assert(self.__output_file_path is not None, exc_msg='container has not run yet')

        return self.__output_file_path

    @property
    def output_file(self):
        return open(self.output_file_path, 'rb')

    @property
    def output(self, rm_output_file=True):
        with self.output_file as output_file:
            contents = output_file.read()
        if rm_output_file:
            os.unlink(self.__output_file_path)
        return contents

    def close(self):
        self.__assert(self.__docker_client is not None, exc_msg='docker client is not initialized')

        self.__docker_client.close()
        self.__docker_client = None

    def rm_image(self, force: bool = False):
        self.__assert(self.__image is not None, exc_msg='image is not built yet')

        self.__image.remove(force=force)

    # TODO: find another way of getting the function code
    def __function_code(self):
        # Remove indentation
        func_code_lines = inspect.getsourcelines(self.__function)[0]
        if func_code_lines[0].startswith(' '):
            i = 0
            while func_code_lines[0][i] == ' ':
                i += 1
            indentation = i - 1
            func_code_lines = [func_code_line[indentation+1:] for func_code_line in func_code_lines]

        func_code = ''.join(func_code_lines)

        # TODO: find another way to remove the decorator of the function code
        if func_code[0] == '@':
            func_code = re.sub('^@.+', '', func_code)
        return func_code
