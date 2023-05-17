import argparse
import json

parser = argparse.ArgumentParser(description="A simple argument parser")
parser.add_argument('--data', type=int, help='data_value')
args = parser.parse_args()

data = {'field1':args.data, 'field2':args.data*2}

print(json.dumps(data))