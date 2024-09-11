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
- If a type hint is present, it inserts a corresponding isinstance check.  
- If no type hints are provided, the tool falls back to a general None check.  
- So, consequently, additionally to CrossHair checks, it could serve as additional python type-checking tool