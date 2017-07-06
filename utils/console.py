from __future__ import absolute_import

import pprint
import time

from sys import stdout


_config = {
  'default_line_width': 80,
  'default_title': 'main',
  'prompt': '>>',
  'sub_prompt': '...',
  'tail_width': 12
}
_config['bar_width'] = _config['default_line_width'] - _config['tail_width'] - 2

_cache = {}
_pp = pprint.PrettyPrinter()


def start(title=None, width=None):
  title = title or _config['default_title']
  width = width or _config['default_line_width']
  print("-> Start of %s\n%s" % (title, '-' * width))
  _cache["title"] = title


def end(width=None):
  title = _cache.pop("title", _config['default_title'])
  width = width or _config['default_line_width']
  print("%s\n|> End of %s" % (('-' * width), title))


def section(contents):
  print("=" * _config['default_line_width'])
  print(":: %s" %  contents)
  print("=" * _config['default_line_width'])


def show_status(content):
  print("%s %s" % (_config['prompt'], content))


def supplement(content):
  print("{} {}".format(_config['sub_prompt'], content))


def pprint(content):
  _pp.pprint(content)


def print_progress(index, total, start_time=None):
  """
  Print progress bar, the line which cursor is positioned will be overwritten
  
  :param index: positive scalar, indicating current work progress
  :param total: positive scalar, indicating total work 
  :param start_time: if provided, ETA will be displayed to the right of
                      the progress bar
  """
  if start_time is not None:
    duration = time.time() - start_time
    eta = duration / index * (total - index)
    tail = "ETA: {:.0f}s".format(eta)
  else:
    tail = "{:.0f}%".format(100 * index / total)

  left = int(index * _config['bar_width']/ total)
  right = _config['bar_width'] - left
  mid = '=' if index == total else '>'
  stdout.write('[%s%s%s] %s' %
               ('=' * left, mid, ' ' * right, tail))
  stdout.flush()


def write_line(content):
  stdout.write("\r{}\n".format(content))
  stdout.flush()


def clear_line():
  stdout.write("\r{}\r".format(" " * (_config['bar_width'] +
                                      _config['tail_width'])))
  stdout.flush()

