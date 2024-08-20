import ast
import astor  # To convert AST back to source code

class AssertInserter(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Insert an assertion at the start of the function to check inputs
        if node.args.args:  # If the function has arguments
            for arg in node.args.args:
                if arg.annotation:  # Insert assertion only if type is annotated
                    assert_stmt = ast.Assert(
                        test=ast.Compare(
                            left=ast.Name(id=arg.arg, ctx=ast.Load()),
                            ops=[ast.IsNot()],
                            comparators=[ast.Constant(value=None)]
                        ),
                        msg=ast.Constant(value=f"{arg.arg} should not be None")
                    )
                    node.body.insert(0, assert_stmt)
        
        # Visit and modify the rest of the function body
        self.generic_visit(node)
        
        # Insert an assertion at the end of the function for postconditions
        if isinstance(node.body[-1], ast.Return):
            return_value = node.body[-1].value
            assert_stmt = ast.Assert(
                test=ast.Compare(
                    left=return_value,
                    ops=[ast.IsNot()],
                    comparators=[ast.Constant(value=None)]
                ),
                msg=ast.Constant(value="Return value should not be None")
            )
            node.body.insert(-1, assert_stmt)
        
        return node

    def visit_Assign(self, node):
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
            return [node, assert_stmt]
        return node

    def visit_If(self, node):
        # Optionally, add checks in conditionals, but focus on core functionality
        self.generic_visit(node)
        return node

    def visit_Try(self, node):
        # Handle try-except blocks for error handling
        self.generic_visit(node)
        for handler in node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                assert_stmt = ast.Assert(
                    test=ast.Constant(value=False),
                    msg=ast.Constant(value="Unhandled exception occurred")
                )
                handler.body.append(assert_stmt)
        return node

# Example code to analyze and modify
code = """
def process_transaction(account, amount):
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
print(modified_code)

