from __future__ import absolute_import

import tensorflow as tf

from ..core import Function
from ..layers.layer import Layer
from ..layers.common import Activation

from .. import pedia


class Net(Function):
  """Function which can packet sub-functions automatically when calling add
     method"""
  def __init__(self, name, level=0):
    """Instantiate Net, a name must be given"""
    self._name = name
    self._level = level

    self.chain = []
    self.inputs = None

  @property
  def group_name(self):
    return self._name

  def _link(self, inputs, **kwargs):
    # Check inputs
    if inputs is None:
      if self.inputs is None:
        raise ValueError('Input not defined')
      inputs = self.inputs

    # Check chain
    assert isinstance(self.chain, list)
    if len(self.chain) == 0:
      raise ValueError('Net is empty')

    with_logits = kwargs.get(pedia.with_logits, False)

    outputs = inputs
    logits = None
    # Link all functions in chain
    for f in self.chain:
      # Logits are always inputs of activation layers
      if isinstance(f, Activation):
        logits = outputs

      if isinstance(f, Net) and with_logits:
        outputs, logits = f(outputs, **kwargs)
      else:
        outputs = f(outputs)

    # Return
    if with_logits:
      return outputs, logits
    else:
      return outputs

  def add(self, f):
    if isinstance(f, tf.Tensor):
      # If f is a placeholder
      self.inputs = f
      tf.add_to_collection(pedia.default_feed_dict, f)
    elif isinstance(f, Net) or self._level > 0:
      # Net should be added directly into self.chain
      self.chain += [f]
    elif isinstance(f, Layer):
      # If layer is a nucleus or the 1st layer added into this Net
      if f.is_nucleus or len(self.chain) == 0:
        self._wrap_and_add(f)
      # Otherwise add this layer to last Net of self.chain
      if not isinstance(self.chain[-1], Net):
        raise TypeError('Last object of self.chain must be a Net')
      self.chain[-1].add(f)
    else:
      raise ValueError('Object added to a Net must be a Layer or a Net')

  def _wrap_and_add(self, layer):
    assert isinstance(layer, Layer)
    # Specify the name of the Net
    if not layer.is_nucleus:
      name = 'Preprocess'
    else:
      name = layer.abbreviation
      index = 1
      get_name = lambda: '{}{}'.format(name, index)
      for f in self.chain:
        if isinstance(f, Net) and f.group_name == get_name():
          index += 1
      # Now we get the name
      name = get_name()

    # Wrap the layer into a new Net
    self.add(Net(name, level=self._level+1))