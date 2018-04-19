from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from tframe import console
from tframe import SaveMode

from tframe.config import Flag
from tframe.trainers.trainer import Trainer, TrainerHub


class SmartTrainer(Trainer):
  """The so-called 'smart training' refers to automatically tuning learning
      rate and early stopping during training under some criteria

     Model save mechanism: SaveMode.ON_RECORD

     Smart training is based on the trend of model metric. A criteria called
     'bad apples' will accumulate, decrease or reset according to the metric
     trend. Once the amount of bad apples reached to a specific number,
      they will be cleared and the learning rate of model optimizer will be
      decayed.

     Bad apples will increase by 1 when
     (1) no new record appears in the current round
     Bad apples will decrease be 1 when
     (1) all(metric.trend < 0)
     Bad apples will be reset when
     (1) new metric record appears
     (2) learning rate decays

    """
  def __init__(
      self,
      model,
      training_set=None,
      validation_set=None,
      snapshot=None,
      probe=None):
    # Call parent's constructor
    Trainer.__init__(
      self, model, training_set, validation_set, snapshot, probe)
    # Override trainer hub with SmartTrainerHub
    self.th = SmartTrainerHub(self)

  # region : Train

  def _sanity_check(self):
    # Smart training relies on model.metric on the validation data set,
    # .. so their existence should be guaranteed
    if not self.th.validation_on:
      raise AssertionError('!! validation must be on during smart training')

  def _advanced_strategy(self, rnd):
    """This method will be called after Metric.end_round method"""
    if self.metric.trend_is_promising and self.th.bad_apples > 0:
      self.th.bad_apples -= 1
    if self.metric.get_idle_rounds(rnd) > 0:
      self.th.bad_apples += 1
      if self.th.bad_apples > self.th.max_bad_apples:
        # Decay learning rate and reset bad apples
        self.model.tune_lr(coef=self.th.lr_decay)
        self.th.bad_apples = 0
    else:
      # Reset bad apples when new record appears
      self.th.bad_apples = 0

    # Show bad apple count
    console.supplement('{} bad apples found.'.format(self.th.bad_apples))

  # endregion : Train


class SmartTrainerHub(TrainerHub):
  """"""
  # Class attributes
  lr_decay = Flag.float(0.6, 'Learning rate decay coefficient')
  max_bad_apples = Flag.integer(4, 'Max bad apple number')

  def __init__(self, trainer=None):
    # Call parent's constructor
    TrainerHub.__init__(self, trainer)
    # Freeze options
    self.save_mode.freeze(SaveMode.ON_RECORD)
    self.early_stop.freeze(True)
    # Append attributes
    self.bad_apples = 0


SmartTrainerHub.register()
SmartTrainer.HubClass = SmartTrainerHub
