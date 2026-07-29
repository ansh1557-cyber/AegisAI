"""
Test Execution Validator
"""

import MetaTrader5 as mt5

from engine.mt5_connector import MT5Connector
from engine.execution_validator import ExecutionValidator


MT5Connector().connect()


request = {

    "volume": 0.02,

    "price": 4032.49,

    "sl": 4029.00,

    "tp": 4040.00,

    "type": mt5.ORDER_TYPE_BUY,

}


validator = ExecutionValidator()


result = validator.validate(request)


print("\n========== VALIDATION ==========\n")


for check in result["checks"]:
    print(check)


print("\nApproved:", result["approved"])


mt5.shutdown()