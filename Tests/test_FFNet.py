import unittest
import numpy as np

from create_test_model import create_test_model

from NNets import FFNet

class TestFFNet(unittest.TestCase):

    def test_shape_binary(self):
        model = lambda: create_test_model(10, 1)
        model = FFNet(model)
        pred = model.predict_on_batch(np.ones((1, 10)))
        self.assertEqual(pred.shape, (1, 1))

    def test_shape_binary_multiple(self):
        model = lambda: create_test_model(10, 1)
        model = FFNet(model)
        pred = model.predict_on_batch(np.ones((10, 10)))
        self.assertEqual(pred.shape, (10, 1))
        
    def test_shape_multilabel(self):
        model = lambda: create_test_model(10, 10)
        model = FFNet(model)
        pred = model.predict_on_batch(np.ones((1, 10)))
        self.assertEqual(pred.shape, (1, 10))

    def test_shape_multilabel_multiple(self):
        model = lambda: create_test_model(10, 10)
        model = FFNet(model)
        pred = model.predict_on_batch(np.ones((10, 10)))
        self.assertEqual(pred.shape, (10, 10))
        
    def test_get_weights(self):
        model = lambda: create_test_model(10, 10)
        model = FFNet(model)
        weights = model.get_weights()
        
    def test_set_weights(self):
        model = lambda: create_test_model(10, 10)
        model = FFNet(model)
        weights = model.get_weights()
        for w in weights:
            w = w*2
        model.set_weights(weights)

if __name__ == '__main__':
    unittest.main()