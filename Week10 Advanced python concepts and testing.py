"""
Advanced Python Library - Single File Implementation
Demonstrates decorators, generators, context managers,
metaclasses, type hints and unit testing.
"""

import time
import functools
import logging
import argparse
from typing import Callable, TypeVar, Dict, Any, Iterator
from collections.abc import Hashable
from contextlib import ContextDecorator

logging.basicConfig(level=logging.INFO)

T = TypeVar("T")

# ============================
# Custom Exceptions
# ============================

class RetryError(Exception):
    """Raised when retry attempts fail"""


# ============================
# Decorators
# ============================

def timer(func: Callable[..., T]) -> Callable[..., T]:
    """Measure execution time"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        logging.info(f"{func.__name__} executed in {end-start:.4f} seconds")
        return result

    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0):

    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            last_error = None

            for attempt in range(max_attempts):

                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_error = e
                    logging.warning(f"Retry {attempt+1}/{max_attempts}")

                    time.sleep(delay)

            raise RetryError("Maximum retry attempts exceeded") from last_error

        return wrapper

    return decorator


class Cache:
    """Simple caching decorator"""

    def __init__(self):
        self.storage: Dict[Hashable, Any] = {}

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(*args):

            if args in self.storage:
                logging.info("Cache Hit")
                return self.storage[args]

            result = func(*args)
            self.storage[args] = result

            return result

        return wrapper


# ============================
# Generators
# ============================

def fibonacci() -> Iterator[int]:
    """Infinite Fibonacci generator"""

    a, b = 0, 1

    while True:
        yield a
        a, b = b, a + b


def batch_generator(data: Iterator[Any], size: int = 5) -> Iterator[list]:
    """Yield batches of data"""

    batch = []

    for item in data:

        batch.append(item)

        if len(batch) == size:
            yield batch
            batch = []

    if batch:
        yield batch


# ============================
# Context Manager
# ============================

class SafeFile(ContextDecorator):
    """Safe file handler"""

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):

        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.file:
            self.file.close()

        if exc_type:
            logging.error("File error occurred")

        return False


# ============================
# Metaclass
# ============================

class RegistryMeta(type):
    """Registers classes automatically"""

    registry = {}

    def __new__(cls, name, bases, attrs):

        new_class = super().__new__(cls, name, bases, attrs)

        if name != "BaseModel":
            cls.registry[name] = new_class

        return new_class


class BaseModel(metaclass=RegistryMeta):
    """Base class for models"""

    def to_dict(self):

        return self.__dict__


class User(BaseModel):

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


# ============================
# Example Functions
# ============================

cache = Cache()


@retry(3, 1)
@timer
@cache
def expensive_operation(x: int) -> int:
    """Simulated expensive task"""

    time.sleep(1)

    return x * x


# ============================
# CLI Application
# ============================

def main():

    parser = argparse.ArgumentParser(description="Advanced Python Demo")

    parser.add_argument("--fib", type=int, help="Generate Fibonacci numbers")

    args = parser.parse_args()

    if args.fib:

        gen = fibonacci()

        for _ in range(args.fib):
            print(next(gen))

    else:

        print("Running demo...")

        print(expensive_operation(5))
        print(expensive_operation(5))  # Cached result

        print("\nFibonacci Example")

        gen = fibonacci()

        for _ in range(5):
            print(next(gen))

        print("\nBatch Example")

        data = range(10)

        for batch in batch_generator(iter(data), 3):
            print(batch)

        print("\nContext Manager Example")

        with SafeFile("demo.txt", "w") as f:
            f.write("Hello Advanced Python")

        print("\nMetaclass Registry")
        print(RegistryMeta.registry)


# ============================
# Unit Tests (pytest)
# ============================

def test_cache():

    result1 = expensive_operation(2)
    result2 = expensive_operation(2)

    assert result1 == result2


def test_fibonacci():

    gen = fibonacci()

    assert next(gen) == 0
    assert next(gen) == 1
    assert next(gen) == 1


def test_batch():

    data = range(6)

    batches = list(batch_generator(iter(data), 3))

    assert len(batches) == 2


def test_user_model():

    u = User("John", 25)

    assert u.to_dict()["name"] == "John"


# ============================
# Run Script
# ============================

if __name__ == "__main__":
    main()