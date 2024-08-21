import ast
import astor  # To convert AST back to source code
import logging
import subprocess


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class AssertInserter(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        logger.info(f"Analyzing function: {node.name}")
        new_body = []

        # Insert an assertion at the start of the function to check inputs
        if node.args.args:  # If the function has arguments
            for arg in node.args.args:
                if isinstance(arg, ast.arg):
                    assert_stmt = ast.Assert(
                        test=ast.Compare(
                            left=ast.Name(id=arg.arg, ctx=ast.Load()),
                            ops=[ast.IsNot()],
                            comparators=[ast.Constant(value=None)]
                        ),
                        msg=ast.Constant(value=f"{arg.arg} should not be None")
                    )
                    new_body.append(assert_stmt)
                    logger.info(f"  - Inserted assert statement at start of function: {arg.arg} should not be None")
        
        # Visit and modify the rest of the function body
        for stmt in node.body:
            new_body.append(self.visit(stmt))
        
        # Insert an assertion at the end of the function for postconditions
        if isinstance(new_body[-1], ast.Return):
            return_value = new_body[-1].value
            assert_stmt = ast.Assert(
                test=ast.Compare(
                    left=return_value,
                    ops=[ast.IsNot()],
                    comparators=[ast.Constant(value=None)]
                ),
                msg=ast.Constant(value="Return value should not be None")
            )
            new_body.insert(-1, assert_stmt)
            logger.info(f"  - Inserted assert statement before return: Return value should not be None")
        
        node.body = new_body
        return node

    def visit_Assign(self, node):
        logger.info(f"  - Found assignment at line {node.lineno}")
        # Insert assertions after assignments to check critical state transitions
        if isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
            assert_stmt = ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id=target, ctx=ast.Load()),
                    ops=[ast.IsNot()],
                    comparators=[ast.Constant(value=None)]
                ),
                msg=ast.Constant(value=f"{target} should not be None after assignment")
            )
            logger.info(f"  - Inserted assert statement after assignment: {target} should not be None")
            return [node, assert_stmt]
        return node

    def visit_If(self, node):
        logger.info(f"  - Found if statement at line {node.lineno}")
        self.generic_visit(node)
        return node

    def visit_Try(self, node):
        logger.info(f"  - Found try-except block at line {node.lineno}")
        self.generic_visit(node)
        for handler in node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                assert_stmt = ast.Assert(
                    test=ast.Constant(value=False),
                    msg=ast.Constant(value="Unhandled exception occurred")
                )
                handler.body.append(assert_stmt)
                logger.info(f"  - Inserted assert statement in except block: Unhandled exception occurred")
        return node

# Example code to analyze and modify
code = """
from typing import Union


class Account:
    balance: Union[int, float]

global account
account = Account()

def process_transaction(account: Account, amount: Union[int, float]) -> Union[int, float]:
    if account.balance < amount:
        raise ValueError("Insufficient funds")
    account.balance -= amount
    return account.balance
"""

# Parse the code into an AST
tree = ast.parse(code)

# Apply the AssertInserter to the AST
transformer = AssertInserter()
transformed_tree = transformer.visit(tree)

# Convert the modified AST back to source code
modified_code = astor.to_source(transformed_tree)
print('================================================================')
print('result:')
print(modified_code)
print('================================================================')

# Get the function name to name the file
function_name = transformer.function_name if hasattr(transformer, 'function_name') else 'modified_code'
filename = f"{function_name}.py"

# Write the modified code to a new file
with open(filename, 'w') as f:
    f.write(modified_code)

logger.info(f"Modified code saved to {filename}")

# Run CrossHair on the new file and capture the output
logger.info(f"Running CrossHair on {filename}")
result = subprocess.run(['crosshair', 'check', '--analysis_kind', 'asserts',
                         filename], capture_output=True, text=True)

# Log the output to both logger and terminal
logger.info(result.stdout)
logger.error(result.stderr)
print(result.stdout)
print(result.stderr)
