# functainer
[Dockerize](https://www.docker.com/) a function and run it in a container directly from Python.

**WARNING: pre-alpha state project, use only under your responsibility!**

## What's this?
A way to run Python functions in a container without having to worry about docker.

## Why?
- To keep some code with different dependencies than your main code.
- Because, why not?

## Requirements
You must have [docker](https://www.docker.com/) installed in your machine and 
[docker python package](https://pypi.org/project/docker/)
(see [requirements.txt](requirements.txt) file).

## Instructions
1. Define a function that
   1. takes a file path as lone parameter,
   2. must have all imports locally, and
   3. will write the output in the file whose file path is the parameter.
2. Use the **functainerize decorator** to run it on a container.
3. That's all.

```python
@functainerize(image='python:3.10', requirements=['pandas==1.5.0'])
def package_installation(output_file_path: str):
    import pandas as pd

    url = "https://raw.githubusercontent.com/cs109/2014_data/master/countries.csv"
    df = pd.read_csv(url)
    
    # Do some operations with the dataset

    df.to_pickle(path=output_file_path)
```

For more examples, see the [test_decorator.py](functainer/tests/test_decorator.py) file.

## TODO
- [ ] Check that the decorated function has the required parameter.
- [ ] Remove requirement to import everything locally.
- [ ] Add more tests.
- [ ] Add async version.

## Author
Diego J. Romero López

## License
[MIT](LICENSE)