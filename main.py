from fastmcp import FastMCP
import random
import json


mcp=FastMCP("Simple calculator server")

@mcp.tool
def add(a: float, b: float) -> float:
    """Returns the sum of two numbers."""
    return a + b

#Tool to generate a random number
@mcp.tool
def random_number(min_value: int, max_value: int) -> int:
    """Generates a random integer between min_value and max_value."""
    return random.randint(min_value, max_value)


@mcp.resource("info://server")
def server_info() -> str:
    """Returns information about the server in JSON format."""
    info = {
        "name": "Simple Calculator Server",
        "version": "1.0",
        "description": "A server that performs basic arithmetic operations and generates random numbers.",
        "tools": ["add", "random_number"],
        "author": "Your Name"
    }
    return json.dumps(info, indent=4)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0" , port=8080)