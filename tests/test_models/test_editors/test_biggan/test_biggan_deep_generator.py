# Copyright (c) OpenMMLab. All rights reserved.
from copy import deepcopy
from functools import partial

import pytest
import torch

# yapf:disable
from mmedit.models.editors.biggan import BigGANDeepGenerator
from mmedit.registry import MODULES

# yapf:enable


class TestBigGANDeepGenerator(object):

    @classmethod
    def setup_class(cls):
        cls.noise = torch.randn((3, 120))
        num_classes = 1000
        cls.label = torch.randint(0, num_classes, (3, ))
        cls.default_config = dict(
            type='BigGANDeepGenerator',
            output_scale=128,
            num_classes=num_classes,
            base_channels=4)

    def test_biggan_deep_generator(self):

        # test default setting with builder
        g = MODULES.build(self.default_config)
        assert isinstance(g, BigGANDeepGenerator)
        res = g(self.noise, self.label)
        assert res.shape == (3, 3, 128, 128)

        # test 'return_noise'
        res = g(self.noise, self.label, return_noise=True)
        assert res['fake_img'].shape == (3, 3, 128, 128)
        assert res['noise_batch'].shape == (3, 120)
        assert res['label'].shape == (3, )

        res = g(None, None, num_batches=3, return_noise=True)
        assert res['fake_img'].shape == (3, 3, 128, 128)
        assert res['noise_batch'].shape == (3, 120)
        assert res['label'].shape == (3, )

        # test callable
        noise = torch.randn
        label = partial(torch.randint, 0, 1000)
        res = g(noise, label, num_batches=2)
        assert res.shape == (2, 3, 128, 128)

        # test different output scale
        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=256))
        g = MODULES.build(cfg)
        noise = torch.randn((3, 120))
        res = g(noise, self.label)
        assert res.shape == (3, 3, 256, 256)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 256, 256)

        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=512))
        g = MODULES.build(cfg)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 512, 512)

        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=64))
        g = MODULES.build(cfg)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 64, 64)

        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=32))
        g = MODULES.build(cfg)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 32, 32)

        # test with `concat_noise=False`
        cfg = deepcopy(self.default_config)
        cfg.update(dict(concat_noise=False))
        g = MODULES.build(cfg)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test with `with_spectral_norm=False`
        cfg = deepcopy(self.default_config)
        cfg.update(dict(with_spectral_norm=False))
        g = MODULES.build(cfg)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test different num_classes
        cfg = deepcopy(self.default_config)
        cfg.update(
            dict(
                num_classes=0, with_shared_embedding=False,
                concat_noise=False))
        g = MODULES.build(cfg)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test no shared embedding
        cfg = deepcopy(self.default_config)
        cfg.update(dict(with_shared_embedding=False, concat_noise=False))
        g = MODULES.build(cfg)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test torch-sn
        cfg = deepcopy(self.default_config)
        cfg.update(dict(sn_style='torch'))
        g = MODULES.build(cfg)
        res = g(self.noise, self.label)
        assert res.shape == (3, 3, 128, 128)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason='requires cuda')
    def test_biggan_deep_generator_cuda(self):

        # test default setting with builder
        g = MODULES.build(self.default_config).cuda()
        assert isinstance(g, BigGANDeepGenerator)
        res = g(self.noise.cuda(), self.label.cuda())
        assert res.shape == (3, 3, 128, 128)

        # test 'return_noise'
        res = g(self.noise.cuda(), self.label.cuda(), return_noise=True)
        assert res['fake_img'].shape == (3, 3, 128, 128)
        assert res['noise_batch'].shape == (3, 120)
        assert res['label'].shape == (3, )

        res = g(None, None, num_batches=3, return_noise=True)
        assert res['fake_img'].shape == (3, 3, 128, 128)
        assert res['noise_batch'].shape == (3, 120)
        assert res['label'].shape == (3, )

        # test callable
        noise = torch.randn
        label = partial(torch.randint, 0, 1000)
        res = g(noise, label, num_batches=2)
        assert res.shape == (2, 3, 128, 128)

        # test different output scale
        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=256))
        g = MODULES.build(cfg).cuda()
        noise = torch.randn((3, 120))
        res = g(noise.cuda(), self.label.cuda())
        assert res.shape == (3, 3, 256, 256)
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 256, 256)

        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=512))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 512, 512)

        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=64))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 64, 64)

        cfg = deepcopy(self.default_config)
        cfg.update(dict(output_scale=32))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 32, 32)

        # test with `concat_noise=False`
        cfg = deepcopy(self.default_config)
        cfg.update(dict(concat_noise=False))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test with `with_spectral_norm=False`
        cfg = deepcopy(self.default_config)
        cfg.update(dict(with_spectral_norm=False))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test different num_classes
        cfg = deepcopy(self.default_config)
        cfg.update(
            dict(
                num_classes=0, with_shared_embedding=False,
                concat_noise=False))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test no shared embedding
        cfg = deepcopy(self.default_config)
        cfg.update(dict(with_shared_embedding=False, concat_noise=False))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)

        # test torch-sn
        cfg = deepcopy(self.default_config)
        cfg.update(dict(sn_style='torch'))
        g = MODULES.build(cfg).cuda()
        res = g(None, None, num_batches=3)
        assert res.shape == (3, 3, 128, 128)