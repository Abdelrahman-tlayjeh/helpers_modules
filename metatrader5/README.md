#  Metatrader5 automating helper 
 A helper class built for a simple automated-trading system to facilitate basic operations with the MetaTrader5 API, to use it, MetaTrader5 should be installed and the "Algo Trading" option should be enabled


## Usage example:

### - init connection with MT5 terminal
```python
from mt5 import Mt5

server:str = "broker-server" 
login:int = "login-id"
password:str = "login-password"

symbols_extension:str = ""
filling_type:str = "IOC"
deviation:int = 10

mt = Mt5(server, login, password, symbols_extension, filling_type)
try:
    mt.connect()
except Exception as e:
    print(f"Failed! {e}")
```

### - Show all account information
```python
for prop, value in mt.account_info.items():
    print(f"{prop}: {value}")
```
### - Open a trade
```python
try:
    order_result = mt.open_trade(
        "EURUSD",   #pair
        "BUY",      #type
        0.5,        #volume (lot size)
        1.0563,     #entry price
        1.0523,     #stop loss
        1.0593,     #take profit
        1000,       #magic number,
        "just testing", #note
        deviation,      #acceptable_change_in_price
    )
    print("Trade is successfully executed:")
    for prop, value in order_result._asdict().items():
        print(f"{prop}: {value}")
        
except Exception as e:
    print(f"Failed! {e}")
```