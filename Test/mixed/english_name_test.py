"""English filename test file.

Used to test that files with English names are indexed correctly
alongside Chinese-named files in the same directory.
"""

VALUE = 42


def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    print(add(1, 2))
