#!/bin/bash
set -e
for V in 0.0.2 0.1.0
do
  pip uninstall -y sockit
  pip install "sockit==${V}"
  sockit -i test.json -o "results-${V}.json"
done
for V in 0.2.0 0.2.1 0.3.0 0.3.1
do
  pip uninstall -y sockit
  pip install "sockit==${V}"
  sockit title -i test.json -o "results-${V}.json"
done
pip uninstall -y sockit
python compare.py test.json results-*.json >compare.csv
