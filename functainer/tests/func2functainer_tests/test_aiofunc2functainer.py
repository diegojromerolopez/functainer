import asyncio
import unittest

from functainer.aiodecorator import aiofunctainerize


@aiofunctainerize(requirements=[], returning='contents')
async def basic_contents_output(output_file_path: str):  # pragma: no cover
    with open(output_file_path, 'wb') as output_file:
        output_file.write(b'output')


class TestAioFunc2Functainer(unittest.IsolatedAsyncioTestCase):
    async def test_basic_contents_output(self):
        output = await basic_contents_output()

        self.assertEqual(b'output', output)
