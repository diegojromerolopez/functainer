import unittest
from unittest.mock import ANY, patch, Mock, call

from docker.errors import DockerException

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

    def test_http_request(self):
        def http_request(output_file_path: str):  # pragma: no cover
            import requests  # noqa
            response = requests.get('https://github.com')

            with open(output_file_path, 'wb') as output_file:
                output_file.write(str(response.status_code).encode('utf8'))

        with Functainer(function=http_request) as functainer:
            functainer.build(image_tag='requests_image', requirements=['requests==2.28.1'])
            functainer.run()
            output = functainer.output

        self.assertEqual(b'200', output)

    @patch('functainer.functainer.docker')
    def test_functainer_image_exists_check_parameters(self, mock_docker):
        mock_docker_client = Mock()
        mock_docker_image = Mock()
        mock_docker_client.images.get.return_value = mock_docker_image
        mock_docker_client.containers.run.return_value = Mock()
        mock_docker.from_env.return_value = mock_docker_client

        functainer = Functainer(function=basic_contents_output)
        functainer.build(image_tag='test_image_tag', build_container_kwargs={'tag': 'my_tag'})
        functainer.run(run_container_kwargs={'name': 'my_container'})
        functainer.close()

        self.assertEqual([call.from_env()], mock_docker.method_calls)
        self.assertEqual([
            call.images.get(name='test_image_tag'),
            call.containers.run(
                image=mock_docker_image,
                command='python3 /tmp/functainer_temp/executor.py',
                volumes=[ANY, ANY],
                remove=True, user=ANY, name='my_container'
            ),
            call.close()
        ], mock_docker_client.method_calls)

    @patch('functainer.functainer.docker')
    def test_functainer_image_does_not_exist_check_parameters(self, mock_docker):
        mock_docker.errors.DockerException = DockerException
        mock_docker_client = Mock()
        mock_docker_image = Mock()
        mock_docker_client.images.get.side_effect = DockerException()
        mock_docker_client.images.build.return_value = mock_docker_image, ANY
        mock_docker_client.containers.run.return_value = Mock()
        mock_docker.from_env.return_value = mock_docker_client

        functainer = Functainer(function=basic_contents_output)
        functainer.build(image_tag='test_image_tag', build_container_kwargs={'tag': 'my_tag'})
        functainer.run(run_container_kwargs={'name': 'my_container'})
        functainer.close()

        self.assertEqual([call.from_env()], mock_docker.method_calls)
        self.assertEqual([
            call.images.get(name='test_image_tag'),
            call.images.build(path=ANY, buildargs={'FROM_IMAGE': 'python:latest', 'REQUIREMENTS': ''}, tag='my_tag'),
            call.containers.run(
                image=mock_docker_image,
                command='python3 /tmp/functainer_temp/executor.py',
                volumes=[ANY, ANY], remove=True, user=ANY, name='my_container'
            ),
            call.close()
        ], mock_docker_client.method_calls)

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
