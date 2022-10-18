from typing import List, Optional, Callable, BinaryIO, Union, Dict

import docker
import inspect
import os
import tempfile


def func2functainer(
        function: Callable[[], None],
        python_command: str = 'python3',
        image: str = 'python:latest',
        requirements: Optional[List[str]] = None,
        returning: str = 'file_path',
        build_container_kwargs: Optional[Dict] = None,
        run_container_kwargs: Optional[Dict] = None
) -> Union[str, BinaryIO, bytes]:

    if requirements is None:
        requirements = []

    image_tag = f"{function.__module__}__{function.__name__}"
    if build_container_kwargs is None:
        build_container_kwargs = {
            'nocache': False,
            'tag': image_tag
        }

    if run_container_kwargs is None:
        run_container_kwargs = {}

    func_code = ''.join(inspect.getsourcelines(function)[0][1:])

    docker_client = docker.from_env()

    try:
        image = docker_client.images.get(name=image_tag)
    except docker.errors.ImageNotFound:
        image, _ = docker_client.images.build(
            path=os.path.dirname(os.path.realpath(__file__)),
            buildargs={'IMAGE_NAME': image, 'REQUIREMENTS': ' '.join(requirements)},
            **build_container_kwargs
        )

    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    executor_file_path = os.path.join(current_dir_path, 'executor.py.tpl')
    with open(executor_file_path) as executor_file:
        executor_file_contents = executor_file.read()
        executor_file_contents = executor_file_contents.replace('__function_definition__', func_code)
        executor_file_contents = executor_file_contents.replace('__function_call__', function.__name__)

    with tempfile.TemporaryDirectory() as temp_dir_path:
        temp_executor_file_path = os.path.join(temp_dir_path, 'executor.py')
        with open(temp_executor_file_path, 'w') as temp_executor_file:
            temp_executor_file.write(executor_file_contents)

        output_fd, output_file_path = tempfile.mkstemp(text=False)

        docker_client.containers.run(
            image=image,
            command=f'{python_command} /tmp/functainer_temp/executor.py',
            volumes=[
                f'{temp_dir_path}:/tmp/functainer_temp',
                f'{output_file_path}:/tmp/functainer_output'
            ],
            remove=True,
            user=f'{os.getuid()}:{os.getgid()}',
            **run_container_kwargs
        )

    docker_client.close()

    if returning == 'file_path':
        return output_file_path
    elif returning == 'file':
        return os.fdopen(output_fd, 'rb')
    elif returning == 'contents':
        with open(output_file_path, 'rb') as output_file:
            contents = output_file.read()
        os.unlink(output_file_path)
        return contents

    raise ValueError(
        'Invalid returning value. Valid values are: \'file_path\', \'file_path\', or \'contents\''
    )
