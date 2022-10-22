from typing import List, Optional, Callable, BinaryIO, Union, Dict

from functainer.functainer import Functainer


def func2functainer(
        function: Callable[[], None],
        image_tag: str,
        python_command: str = 'python3',
        from_image: str = 'python:latest',
        requirements: Optional[List[str]] = None,
        returning: str = 'file_path',
        build_container_kwargs: Optional[Dict] = None,
        run_container_kwargs: Optional[Dict] = None
) -> Union[str, BinaryIO, bytes]:

    functainer = Functainer(function=function)
    functainer.build(image_tag=image_tag, from_image=from_image,
                     requirements=requirements,
                     build_container_kwargs=build_container_kwargs)

    try:
        functainer.run(python_command=python_command,
                       run_container_kwargs=run_container_kwargs)
        return __output_return(functainer=functainer, returning=returning)
    finally:
        functainer.close()


def __output_return(functainer: Functainer, returning: str = 'file_path') -> Union[str, BinaryIO, bytes]:
    if returning == 'file_path':
        return functainer.output_file_path
    elif returning == 'file':
        return functainer.output_file
    elif returning == 'contents':
        return functainer.output

    raise ValueError(
        'Invalid returning value. Valid values are: \'file_path\', \'file_path\', or \'contents\''
    )
