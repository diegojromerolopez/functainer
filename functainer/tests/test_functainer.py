import unittest
from unittest.mock import ANY

from functainer.exceptions import FunctainerException
from functainer.functainer import Functainer


def basic_contents_output(output_file_path: str):  # pragma: no cover
    with open(output_file_path, 'wb') as output_file:
        output_file.write(b'output')


class TestFunctainer(unittest.TestCase):
    def test_functainer(self):
        functainer = Functainer(function=basic_contents_output)
        functainer.build(image_tag='test_image_tag')
        functainer.run()
        output = functainer.output
        functainer.close()

        self.assertEqual(b'output', output)

    def test_functainer_as_context_manager(self):
        with Functainer(function=basic_contents_output) as functainer:
            functainer.build(image_tag='test_image_tag')
            functainer.run()
            output = functainer.output

        self.assertEqual(b'output', output)

    def test_build_without_initialized_docker_client(self):
        functainer = Functainer(function=ANY)
        functainer.close()
        with self.assertRaises(FunctainerException) as exc_context:
            functainer.build(image_tag='test_image_tag')

        self.assertEqual('docker client is not initialized', str(exc_context.exception))

    def test_run_without_initialized_docker_client(self):
        functainer = Functainer(function=basic_contents_output)
        functainer.build(image_tag='test_image_tag')
        functainer.close()
        with self.assertRaises(FunctainerException) as exc_context:
            functainer.run()

        self.assertEqual('docker client is not initialized', str(exc_context.exception))

    def test_run_without_initialized_image(self):
        functainer = Functainer(function=basic_contents_output)
        with self.assertRaises(FunctainerException) as exc_context:
            functainer.run()

        self.assertEqual('image is not built yet', str(exc_context.exception))

    def test_output_file_path_without_having_run(self):
        functainer = Functainer(function=basic_contents_output)
        with self.assertRaises(FunctainerException) as exc_context:
            _ = functainer.output_file_path

        self.assertEqual('container has not run yet', str(exc_context.exception))

    def test_close_without_initialized_docker_client(self):
        functainer = Functainer(function=basic_contents_output)
        functainer.close()
        with self.assertRaises(FunctainerException) as exc_context:
            functainer.close()

        self.assertEqual('docker client is not initialized', str(exc_context.exception))

    def test_rm_image_without_initialized_image(self):
        functainer = Functainer(function=basic_contents_output)
        with self.assertRaises(FunctainerException) as exc_context:
            functainer.rm_image()

        self.assertEqual('image is not built yet', str(exc_context.exception))
