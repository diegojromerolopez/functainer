import os
import unittest
from typing import BinaryIO
from docker.errors import ContainerError

from functainer.decorator import functainerize


@functainerize(python_command='python2', from_image='boomset/ubuntu-python27-mysql')
def old_python(output_file_path):  # pragma: no cover
    with open(output_file_path, 'w') as output_file:
        output_file.write(str(5 / 2))


@functainerize(requirements=[], returning='contents')
def basic_contents_output(output_file_path: str):  # pragma: no cover
    with open(output_file_path, 'wb') as output_file:
        output_file.write(b'output')


@functainerize(requirements=[], returning='file')
def basic_file_output(output_file_path: str):  # pragma: no cover
    with open(output_file_path, 'wb') as output_file:
        output_file.write(b'output')


@functainerize(returning='invalid')
def basic_invalid_output(output_file_path: str):  # pragma: no cover
    with open(output_file_path, 'wb') as output_file:
        output_file.write(b'output')


@functainerize(requirements=['pandas==1.5.0'])
def package_installation(output_file_path: str):  # pragma: no cover
    import pandas as pd

    df = pd.DataFrame(['value1', 'value2'])

    df.to_pickle(path=output_file_path)


class TestDecorator(unittest.TestCase):
    def test_old_python(self):
        output_file_path = old_python()
        with open(output_file_path, mode='rb') as output_file:
            output_file_contents = output_file.read()

        os.unlink(output_file_path)

        # Note we are testing the integer division that happened in python2
        self.assertEqual(b'2', output_file_contents)

    def test_basic_contents_output(self):
        output: bytes = basic_contents_output()

        self.assertEqual(b'output', output)

    def test_basic_file_output(self):
        output_file: BinaryIO = basic_file_output()
        output = output_file.read()
        output_file.close()

        self.assertEqual(b'output', output)

    def test_basic_invalid_output(self):
        with self.assertRaises(ValueError) as exception_context:
            basic_invalid_output()

        self.assertEqual('Invalid returning value. Valid values are: \'file_path\', \'file_path\', or \'contents\'',
                         str(exception_context.exception))

    def test_package_installation(self):
        expected_output = (
            b'\x80\x05\x95J\x02\x00\x00\x00\x00\x00\x00\x8c\x11pandas.core.frame\x94\x8c'
            b'\tDataFrame\x94\x93\x94)\x81\x94}\x94(\x8c\x04_mgr\x94\x8c\x1epandas.core.'
            b'internals.managers\x94\x8c\x0cBlockManager\x94\x93\x94\x8c\x16pandas._libs.i'
            b'nternals\x94\x8c\x0f_unpickle_block\x94\x93\x94\x8c\x15numpy.core.multiarray'
            b'\x94\x8c\x0c_reconstruct\x94\x93\x94\x8c\x05numpy\x94\x8c\x07ndarray\x94'
            b'\x93\x94K\x00\x85\x94C\x01b\x94\x87\x94R\x94(K\x01K\x01K\x02\x86\x94h'
            b'\x0f\x8c\x05dtype\x94\x93\x94\x8c\x02O8\x94\x89\x88\x87\x94R\x94(K'
            b'\x03\x8c\x01|\x94NNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK?t\x94b\x89]\x94(\x8c'
            b'\x06value1\x94\x8c\x06value2\x94et\x94b\x8c\x08builtins\x94\x8c\x05slice\x94'
            b'\x93\x94K\x00K\x01K\x01\x87\x94R\x94K\x02\x87\x94R\x94\x85\x94]\x94(\x8c'
            b'\x18pandas.core.indexes.base\x94\x8c\n_new_Index\x94\x93\x94\x8c\x19panda'
            b's.core.indexes.range\x94\x8c\nRangeIndex\x94\x93\x94}\x94(\x8c\x04nam'
            b'e\x94N\x8c\x05start\x94K\x00\x8c\x04stop\x94K\x01\x8c\x04step\x94K\x01u'
            b'\x86\x94R\x94h-h0}\x94(h2Nh3K\x00h4K\x02h5K\x01u\x86\x94R\x94e\x86\x94R\x94'
            b'\x8c\x04_typ\x94\x8c\tdataframe\x94\x8c\t_metadata\x94]\x94\x8c\x05attrs'
            b'\x94}\x94\x8c\x06_flags\x94}\x94\x8c\x17allows_duplicate_labels\x94\x88sub.')

        output_file_path = package_installation()
        with open(output_file_path, mode='rb') as output_file:
            output_file_contents = output_file.read()

        os.unlink(output_file_path)

        self.assertEqual(expected_output, output_file_contents)

    def test_local_function(self):
        @functainerize(requirements=[], returning='contents')
        def local_func(output_file_path: str):  # pragma: no cover
            with open(output_file_path, 'wb') as output_file:
                output_file.write(b'local_func output')

        output: bytes = local_func()

        self.assertEqual(b'local_func output', output)

    def test_local_exit_function(self):
        @functainerize(returning='contents', run_container_kwargs={'stderr': True})
        def local_func(output_file_path: str):  # pragma: no cover
            import sys
            sys.exit(1)

        with self.assertRaises(ContainerError) as exc_context:
            local_func()

        self.assertEqual(
            'Command \'python3 /tmp/functainer_temp/executor.py\' in image '
            '\'sha256:3ec4b7b2691b641d08b51f50c017c0722d58f6c21a7f10c7547fe64a1409b2b7\' '
            'returned non-zero exit status 1: b\'\'',
            str(exc_context.exception)
        )
