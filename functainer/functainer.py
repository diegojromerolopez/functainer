from typing import List, Optional, Callable

import docker
import inspect
import os
import tempfile

.github
def func2functainer(function: Callable[[], None],
                    image: str = 'python:latest',
                    requirements: Optional[List[str]] = None) -> str:
    if requirements is None:
        requirements = []

    func_code = ''.join(inspect.getsourcelines(function)[0][1:])

    docker_client = docker.from_env()
    image, _ = docker_client.images.build(
        path=os.path.dirname(os.path.realpath(__file__)),
        buildargs={'IMAGE_NAME': image, 'REQUIREMENTS': ' '.join(requirements)},
        rm=True
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

        _output_fd, output_file_path = tempfile.mkstemp(text=False)

        docker_client.containers.run(
            image=image,
            command='python3 /tmp/dockerizer_temp/executor.py',
            volumes=[
                f'{temp_dir_path}:/tmp/dockerizer_temp',
                f'{output_file_path}:/tmp/dockerizer_output'
            ],
            remove=True
        )

    docker_client.close()
    return output_file_path
