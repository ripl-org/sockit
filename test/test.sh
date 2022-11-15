pip uninstall -y sockit
pip install sockit==0.0.2
sockit -i test.json -o test-results-0.0.2.json
pip uninstall -y sockit
pip install sockit==0.1.0
sockit -i test.json -o test-results-0.1.0.json
pip uninstall -y sockit
pip install sockit==0.2.0
sockit title -i test.json -o test-results-0.2.0.json
pip uninstall -y sockit
pip install sockit==0.2.1
sockit title -i test.json -o test-results-0.2.1.json
pip uninstall -y sockit
pip install sockit==0.3.0
sockit title -i test.json -o test-results-0.3.0.json
pip uninstall -y sockit
python compare.py test.json test-results-0.0.2.json test-results-0.1.0.json test-results-0.1.0.json test-results-0.2.0.json test-results-0.2.1.json test-results-0.3.0.json > test-comparison.csv
