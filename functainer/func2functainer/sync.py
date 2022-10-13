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
        run_container_kwargs: Optional[Dict] = None
) -> Union[str, BinaryIO, bytes]:

    if requirements is None:
        requirements = []

    if run_container_kwargs is None:
        run_container_kwargs = {}

    func_code = ''.join(inspect.getsourcelines(function)[0][1:])

    resources_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
    docker_client = docker.from_env()
    image, _ = docker_client.images.build(
        path=resources_path,
        buildargs={'IMAGE_NAME': image, 'REQUIREMENTS': ' '.join(requirements)}
    )

    executor_file_path = os.path.join(resources_path, 'executor.py.tpl')
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
            command=f'{python_command} /tmp/dockerizer_temp/executor.py',
            volumes=[
                f'{temp_dir_path}:/tmp/dockerizer_temp',
                f'{output_file_path}:/tmp/dockerizer_output'
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
