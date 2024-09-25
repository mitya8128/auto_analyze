experiments in automatic code verification and check for correctness  

#### Description  
Program automatically inserts assert statements into some critical places in code for further analysis using [CrossHair](https://github.com/pschanely/CrossHair).  
  
#### Setup  
`pip install -r requirements`

#### Usage  
for analysis of single .py file:  
`python analysis_file.py <path to file>`  
  
for analysis of project directory:  
`python analysis_directory.py <path to directory>`

#### Notes  
- Checks for Python type hints in function arguments and return types.  
- If a type hint is present, it inserts a corresponding isinstance check (now it's only for simple types).  
- If no type hints are provided, the tool falls back to a general None check.  
- So, consequently, additionally to CrossHair checks, it could serve as additional python type-checking tool  

#### Example  
Suppose we need to analyse such code:  
```python
from typing import Union


class Account:

    def __init__(self, balance: Union[int, float]):
        self.balance = balance


def process_transaction(account: Account, amount: Union[int, float]) ->Union[
    int, float]:
    if account.balance < amount:
        raise ValueError('Insufficient funds')
    account.balance -= amount
    return account.balance
```  
command python analyse_file.py <`test_snippet.py`>  returns  
```
Analyzing function: __init__
  - Inserted None check for balance
  - Found assignment at line 7
Analyzing function: process_transaction
  - Inserted type check for account: expected type Account
  - Inserted None check for amount
  - Found if statement at line 12
  - Inserted general None check for return value

===========================================================


Modified code:

from typing import Union


class Account:

    def __init__(self, balance: Union[int, float]):
        assert balance is not None, 'balance should not be None'
        self.balance = balance


def process_transaction(account: Account, amount: Union[int, float]) ->Union[
    int, float]:
    assert isinstance(account, Account), 'account should be of type Account'
    assert amount is not None, 'amount should not be None'
    if account.balance < amount:
        raise ValueError('Insufficient funds')
    account.balance -= amount
    assert account.balance is not None, 'Return value should not be None'
    return account.balance



===========================================================

Modified code saved to test_snippet_modified.py
Running CrossHair on test_snippet_modified.py
CrossHair output for test_snippet_modified.py:
<path to new file>:17: error: ValueError: Insufficient funds when calling process_transaction(Account(-1.0), 0.0)
```  

in stdout 

and saves the modified version of original code.
