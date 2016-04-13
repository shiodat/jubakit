# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import jubatus

from .base import BaseSchema, BaseDataset, BaseService, GenericConfig
from .loader.array import ArrayLoader, ZipArrayLoader
from .loader.chain import SupervisedDataChainLoader
from .compat import *

class Schema(BaseSchema):
  LABEL = 'label'

  def __init__(self, mapping, fallback=None):
    if fallback == self.LABEL:
      raise RuntimeError('label key cannot be specified as fallback schema')

    label_keys = filter(lambda k: mapping[k] == self.LABEL, mapping.keys())
    if len(label_keys) == 0:
      raise RuntimeError('label key is not specified in schema')
    elif 1 < len(label_keys):
      raise RuntimeError('label key must be unique in schema')

    self._label_key = label_keys[0]

    super(Schema, self).__init__(mapping, fallback)

  def transform(self, row):
    """
    Classifier schema transforms the row into Datum and its associated label.
    """
    label = row.get(self._label_key, None)
    d = self.transform_as_datum(row, None, [self._label_key])
    return (label, d)

class Dataset(BaseDataset):
  @classmethod
  def from_array(self, data, labels, feature_names=None, label_names=None, static=True):
    """
    Parameters
    ----------
    data : array of shape [n_samples, n_features]
    labels : array of shape [n_samples]
    feature_names : array of shape [n_features], optional
    label_names : array of shape [n_labels], optional
    """
    # Label is feeded with '_label' key from Loader.
    loader = SupervisedDataChainLoader(
      ArrayLoader(data, feature_names),
      ZipArrayLoader(_label=labels),
      label_names,
    )

    # Create schema.
    schema = Schema({'_label': Schema.LABEL}, Schema.NUMBER)

    return Dataset(loader, schema, static)

  def get_labels(self):
    if not self._static:
      raise RuntimeException('non-static datasets cannot fetch list of labels')

    for (idx, (label, d)) in self:
      yield label

class Classifier(BaseService):
  @classmethod
  def name(cls):
    return 'classifier'

  @classmethod
  def _client_class(cls):
    return jubatus.classifier.client.Classifier

  def train(self, dataset):
    cli = self._client()
    for (idx, (label, d)) in dataset:
      assert label is not None
      result = cli.train([jubatus.classifier.types.LabeledDatum(str(label), d)])
      assert result == 1
      yield (idx, label)

  def classify(self, dataset):
    cli = self._client()
    for (idx, (label, d)) in dataset:
      # Do classification for the record.
      result = cli.classify([d])
      assert len(result) == 1

      # Create the list of (label, score) desc sorted by score.
      label_score_sorted = [(ent.label, ent.score) for ent in sorted(result[0], key=lambda x: x.score, reverse=True)]

      # Note: label may become None.
      yield (idx, label, label_score_sorted)

class Config(GenericConfig):
  @classmethod
  def _default_method(cls):
    return 'AROW'

  @classmethod
  def _default_parameter(cls):
    return {'regularization_weight': 1.0}
