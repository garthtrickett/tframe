import mn_core as core
import mn_mu as m
import tensorflow.compat.v1 as tf
from tframe import console
from tframe.utils.misc import date_string
from tframe.layers.advanced import Dense
from tframe.layers.slhw import SLHighway


# -----------------------------------------------------------------------------
# Define model here
# -----------------------------------------------------------------------------
model_name = 'slhw'
id = 2
def model(th):
  assert isinstance(th, m.Config)
  model = m.get_container(th, flatten=True)
  model.add(Dense(th.layer_width, th.spatial_activation))
  model.add(SLHighway(
    config_string=th.group_string,
    num_layers=th.num_layers,
    head_size=th.head_size,
    activation=th.spatial_activation,
    gutter=th.gutter,
    gutter_bias=th.gutter_bias,
  ))
  model.register_extractor(SLHighway.extractor)
  return m.finalize(th, model)


def main(_):
  console.start('{} on MNIST task'.format(model_name.upper()))

  th = core.th
  # ---------------------------------------------------------------------------
  # 0. date set setup
  # ---------------------------------------------------------------------------
  # ---------------------------------------------------------------------------
  # 1. folder/file names and device
  # ---------------------------------------------------------------------------
  th.job_dir += '/{:02d}_{}'.format(id, model_name)
  summ_name = model_name
  th.prefix = '{}_'.format(date_string())
  th.suffix = '_t00_test'
  th.visible_gpu_id = 0
  th.identifier = '01'

  # ---------------------------------------------------------------------------
  # 2. model setup
  # ---------------------------------------------------------------------------
  th.model = model

  th.group_string = '10x5'
  th.head_size = 25
  th.num_layers = 100
  th.gutter = True
  th.gutter_bias = 5

  th.spatial_activation = 'tanh'

  th.layer_width = 50
  # ---------------------------------------------------------------------------
  # 3. trainer setup
  # ---------------------------------------------------------------------------
  th.epoch = 10
  th.batch_size = 128
  th.validation_per_round = 1

  th.optimizer = tf.train.AdamOptimizer
  th.learning_rate = 0.0002

  th.patience = 5
  th.early_stop = False
  th.validate_train_set = True
  th.val_decimals = 6

  # ---------------------------------------------------------------------------
  # 4. summary and note setup
  th.export_tensors_upon_validation = True
  th.export_gates = True

  th.train = True
  th.save_model = False
  th.overwrite = True

  # ---------------------------------------------------------------------------
  # 5. other stuff and activate
  # ---------------------------------------------------------------------------
  th.mark = '{}({}(hs{})x{}-{})'.format(
    model_name, th.group_string, th.head_size,
    th.num_layers, th.spatial_activation)
  th.gather_summ_name = th.prefix + summ_name + th.suffix +  '.sum'
  core.activate()


if __name__ == '__main__':
  tf.app.run()

