# jubakit: Jubatus Toolkit

jubakit is a Python module to access Jubatus features easily.
jubakit can be used in conjunction with [scikit-learn](http://scikit-learn.org/) so that you can use powerful features like cross validation and model evaluation.

## Install

```
pip install jubakit
```

### Requirements

* [Jubatus](http://jubat.us/en/quickstart.html) needs to be installed.
* Although not mandatory, [scikit-learn](http://scikit-learn.org/stable/install.html) is required to use some features like K-fold cross validation.

```
pip install scikit-learn
```

## Quick Start

```py
from jubakit.classifier import Classifier, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load a CSV file.
loader = CSVLoader('iris.csv')

# Define types for each column in the CSV file.
schema = Schema({
  'Species': Schema.LABEL,
  'Sepal.Length': Schema.NUMBER,
  'Sepal.Width': Schema.NUMBER,
  'Petal.Length': Schema.NUMBER,
  'Petal.Width': Schema.NUMBER,
})

# Get the shuffled dataset.
dataset = Dataset(loader, schema).shuffle()

# Run the classifier service (`jubaclassifier` process).
classifier = Classifier.run(Config())

# Train the classifier.
for _ in classifier.train(dataset): pass

# Classify using the trained classifier.
for (idx, label, result) in classifier.classify(dataset):
  print("true label: {0}, estimated label: {1}".format(label, result[0][0]))
```

## Examples by Task

See the `example` directory for working examples.

| Example                   | Topics                                        | Requires scikit-learn |
|---------------------------|-----------------------------------------------|-----------------------|
| classifier_csv.py         | Simple usage of Classifier and CSV file       |                       |
| classifier_libsvm.py      | Simple usage of Classifier and LIBSVM file    | ✓                     |
| classifier_kfold.py       | K-fold validation and cross validation        | ✓                     |
| classifier_parameter.py   | Finding best hyper parameter                  | ✓                     |

## Concepts

* **Loader** fetches data from various data sources (e.g., CSV file, RDBMS, MQ, Twitter stream, etc.) in key-value format.
* **Schema** defines the data type (string feature, numeric feature, ground truth (label), etc.) for each keys of data loaded by Loader.
* **Dataset** is an abstract representation of a sequence of data that binds Loader and Schema.
* **Service** receives Dataset and make update/analyze RPC call to Jubatus servers.
* **Metrics** can be used to evaluate a performance (precision) of a model.
