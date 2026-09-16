"""Regression tests for optional shared-image offsets and legacy compatibility."""
import unittest
import struct

from trexpro_wf import encode_image, pack, unpack, validate_trexpro_container


class SharedImageOffsetsTests(unittest.TestCase):
    def test_nonadjacent_duplicates_keep_logical_order_and_pixels(self):
        a = encode_image(bytes([240, 160, 32, 255]) * 1200, 40, 30)
        b = encode_image(bytes([240, 160, 32, 128]) * 1200, 40, 30)
        c = encode_image(bytes([32, 160, 240, 255]) * 1200, 40, 30)
        images = [a, b, a, c, b, a]
        params = {'3': {'2': 1}}
        for compressed in (False, True):
            with self.subTest(compressed=compressed):
                baseline = pack(params, images, compress=compressed)
                candidate = pack(params, images, compress=compressed, deduplicate_images=True)
                validate_trexpro_container(candidate)
                self.assertEqual(unpack(candidate)[:2], unpack(baseline)[:2])
                self.assertEqual(unpack(candidate)[1], images)
                # QuickLZ's uncompressed tail can grow when block boundaries move.
                # Deduplication guarantees a smaller expanded body, not every file.
                self.assertLess(struct.unpack_from('<I', candidate, 32)[0],
                                struct.unpack_from('<I', baseline, 32)[0])

    def test_unique_assets_and_opt_out_are_byte_identical(self):
        images = [encode_image(bytes([n, 90, 20, 255]) * 1200, 40, 30) for n in (1, 2)]
        for compressed in (False, True):
            baseline = pack({'3': {'2': 1}}, images, compress=compressed)
            self.assertEqual(baseline, pack({'3': {'2': 1}}, images,
                                           compress=compressed, deduplicate_images=True))


if __name__ == '__main__':
    unittest.main()
