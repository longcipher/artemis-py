import json
from decimal import Decimal

scientific_notation = "9e-05"
float_num = format(Decimal(scientific_notation), "f")

data = {"value": float_num}

json_string = json.dumps(data, indent=4, default=str)

print(json_string)
