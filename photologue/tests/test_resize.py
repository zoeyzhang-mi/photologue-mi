import unittest

from django.core.exceptions import ValidationError

from ..models import PhotoSize, PhotoSizeCache
from .factories import PORTRAIT_IMAGE_PATH, SQUARE_IMAGE_PATH, PhotoFactory
from .helpers import PhotologueBaseTest


class PhotoSizeTest(unittest.TestCase):

    def test_clean_wont_allow_zero_dimension_and_crop(self):
        """Tests if ValidationError is raised by clean method if with or height
        is set to 0 and crop is set to true"""
        s = PhotoSize(name='test', width=400, crop=True)
        self.assertRaises(ValidationError, s.clean)


class ImageResizeTest(PhotologueBaseTest):

    def setUp(self):
        super().setUp()
        # Portrait.
        self.pp = PhotoFactory(image__from_path=PORTRAIT_IMAGE_PATH)
        # Square.
        self.ps = PhotoFactory(image__from_path=SQUARE_IMAGE_PATH)

    def tearDown(self):
        super().tearDown()
        self.pp.delete()
        self.ps.delete()

    def test_resize_to_fit(self):
        self.assertEqual(self.pl.get_testPhotoSize_size(), (100, 75))
        self.assertEqual(self.pp.get_testPhotoSize_size(), (75, 100))
        self.assertEqual(self.ps.get_testPhotoSize_size(), (100, 100))

    def test_resize_to_fit_width(self):
        self.s.size = (100, 0)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (100, 75))
        self.assertEqual(self.pp.get_testPhotoSize_size(), (100, 133))
        self.assertEqual(self.ps.get_testPhotoSize_size(), (100, 100))

    def test_resize_to_fit_width_enlarge(self):
        self.s.size = (400, 0)
        self.s.upscale = True
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (400, 300))
        self.assertEqual(self.pp.get_testPhotoSize_size(), (400, 533))
        self.assertEqual(self.ps.get_testPhotoSize_size(), (400, 400))

    def test_resize_to_fit_height(self):
        self.s.size = (0, 100)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (133, 100))
        self.assertEqual(self.pp.get_testPhotoSize_size(), (75, 100))
        self.assertEqual(self.ps.get_testPhotoSize_size(), (100, 100))

    def test_resize_to_fit_height_enlarge(self):
        self.s.size = (0, 400)
        self.s.upscale = True
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (533, 400))
        self.assertEqual(self.pp.get_testPhotoSize_size(), (300, 400))
        self.assertEqual(self.ps.get_testPhotoSize_size(), (400, 400))

    def test_resize_and_crop(self):
        self.s.crop = True
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), self.s.size)
        self.assertEqual(self.pp.get_testPhotoSize_size(), self.s.size)
        self.assertEqual(self.ps.get_testPhotoSize_size(), self.s.size)

    def test_resize_rounding_to_fit(self):
        self.s.size = (113, 113)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (113, 85))
        self.assertEqual(self.pp.get_testPhotoSize_size(), (85, 113))
        self.assertEqual(self.ps.get_testPhotoSize_size(), (113, 113))

    def test_resize_rounding_cropped(self):
        self.s.size = (113, 113)
        self.s.crop = True
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), self.s.size)
        self.assertEqual(self.pp.get_testPhotoSize_size(), self.s.size)
        self.assertEqual(self.ps.get_testPhotoSize_size(), self.s.size)

    def test_resize_one_dimension_width(self):
        self.s.size = (100, 150)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (100, 75))

    def test_resize_one_dimension_height(self):
        self.s.size = (200, 75)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (100, 75))

    def test_resize_no_upscale(self):
        self.s.size = (1000, 1000)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (200, 150))

    def test_resize_no_upscale_mixed_height(self):
        self.s.size = (400, 75)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (100, 75))

    def test_resize_no_upscale_mixed_width(self):
        self.s.size = (100, 300)
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (100, 75))

    def test_resize_no_upscale_crop(self):
        self.s.size = (1000, 1000)
        self.s.crop = True
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (1000, 1000))

    def test_resize_upscale(self):
        self.s.size = (1000, 1000)
        self.s.upscale = True
        self.s.save()
        self.assertEqual(self.pl.get_testPhotoSize_size(), (1000, 750))
        self.assertEqual(self.pp.get_testPhotoSize_size(), (750, 1000))
        self.assertEqual(self.ps.get_testPhotoSize_size(), (1000, 1000))


class PhotoSizeCacheTest(PhotologueBaseTest):

    def test(self):
        cache = PhotoSizeCache()
        self.assertEqual(cache.sizes['testPhotoSize'], self.s)
