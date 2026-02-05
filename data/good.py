def fibonacci(n):
    """
    Generate a list containing the first n Fibonacci numbers.
    """
    if n <= 0:
        return []
    
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    
    return sequence[:n]


def main():
    n = 10
    fib_sequence = fibonacci(n)
    print(f"First {n} Fibonacci numbers: {fib_sequence}")


if __name__ == "__main__":
    main()
