import random
import sys
import math


def ptimesq(n: int):
    """
    generates 2-n bit primes and uses karatsuba to multiply them
    Args:
        n: number of bits to generate the random numbers from

    Returns:
        write the 2 integers and the product to a file titled "output_ptimesq.txt"
    """

    # only accepts an n between 32 and 2046
    if 32 <= n <= 2046:
        # generate 2 n-bit integers p and q
        p = generate_n_bit_prime(n)
        q = generate_n_bit_prime(n)

        # multiply them using karatsuba
        p_q = karatsuba(p, q)

        # output them to the file
        filename = "output_ptimesq.txt"
        output_data(filename, p, q, p_q)


def miller_rabin(n: int, k: int) -> bool:
    """
    Uses miller rabin to determine if a certain integer is prime or not (probably)
    Args:
        n: integer to test
        k: number of times to run the test

    Returns:
        True or False depending on if n is prime or not.
    """

    # base cases for 1 - 3 and all even numbers
    if n <= 1:
        return False
    if n in {2, 3}:
        return True
    if n % 2 == 0:
        return False

    # Decompose n-1 into 2^s.t
    s = 0
    # t has d digits at most
    t = n - 1

    # O(log_2(n)) time
    while t % 2 == 0:
        s += 1
        t //= 2

    # k iterations
    for _ in range(k):
        a = random.randint(2, n - 2)
        # change the power function to calculate with modular arithmetic
        # if a^n mod -1 != 1, it is composite
        if mod_exp(a, n - 1, n) != 1:
            return False
        else:
            # Calculating the current value takes O(d * d^log_3(2)) time maximum
            # So it is d^log_3(6) time
            cur_value = mod_exp(a, t, n)
            # this takes O(d * d^log_3(2)) time for every squaring in the function
            for _ in range(1, s + 1):
                prev_value = cur_value
                cur_value = mod_exp(cur_value, 2, n)
                if cur_value == 1 or cur_value == n - 1:
                    break
                elif cur_value == 1 and prev_value != n - 1:
                    # it's confirmed to be composite
                    return False
                else:
                    continue
    # if all the iterations run through, its probably prime
    return True


def get_binary_representation(n: int) -> list:
    """
    Generates a binary representation of integer n
    Args:
        n: the integer to convert

    Returns:
        a list binary representation of n
    """

    k = []
    while n > 0:
        a = int(float(n % 2))
        k.append(a)
        n = (n - a) / 2

    return k[::-1]


def mod_exp(a: int, b: int, n: int) -> int:
    """
    returns the answer to a^b mod n
    Args:
        a: a
        b: b
        n: n

    Returns:
    the answer to a^b % n
    """

    # get the binary representation
    binary_rep = get_binary_representation(b)

    # Base case
    current = a % n
    lsb = binary_rep[-1]
    if lsb == 1:
        result = current
    else:
        result = 1

    # Iterate through the remaining bits in the binary representation in reverse
    for current_bit in binary_rep[::-1][1:]:
        # Compute the next term in the sequence
        current = (current * current) % n
        if current_bit == 1:
            # update the result
            result = (result * current) % n
    return result


def generate_n_bit_prime(n: int) -> int:
    """
    generates random n-bit numbers until one of them is approved by the miller-rabin function
    Args:
        n: how many bits to generate random numbers of

    Returns:
    a randomly generated n-bit prime number
    """

    while True:
        # generate a random odd n-bit integer and find the k
        candidate = random.getrandbits(n)
        candidate |= (1 << n - 1) | 1
        k = int(ln(candidate) + 1)
        # if the integer passes the miller-rabin test, return it
        if miller_rabin(candidate, k):
            return candidate


def karatsuba(x: int, y: int) -> int:
    """
    multiplies 2 integers, x and y, using karatsubas divide and conquer approach.
    Args:
        x: the first integer
        y: the second integer

    Returns:
    the product of x and y
    """

    n = max(x.bit_length(), y.bit_length())

    # trivial
    if n <= 1:
        # perform binary multiplications, including negative numbers
        return x * y

    # divide
    d = (n + 1) >> 1
    u1 = x >> d
    u0 = x - (u1 << d)
    v1 = y >> d
    v0 = y - (v1 << d)

    # recursions
    a = karatsuba(u1, v1)
    c = karatsuba(u0, v0)

    # remove the negative if existed
    if (u1 - u0) <= 0 and (v1 - v0) <= 0:
        p = karatsuba(abs(u1 - u0), abs(v1 - v0))
    else:
        p = karatsuba((u1 - u0), (v1 - v0))

    # conquer
    return (a << (2 * d)) + (a << d) + (-p << d) + ((c << d) + c * 1)


def output_data(output_filename: str, p: int, q: int, p_q: int):
    """
    outputs the two integers, p and q, along with their product to a file titled filename
    Args:
        output_filename: name of the file
        p: first integer
        q: second integer
        p_q: product of p and q

    Returns:
    the output is written to a file. p, q and their product.
    """

    with open(output_filename, "w") as file:
        file.write("# p (in base 10)\n")
        file.write(str(p) + "\n\n")
        file.write("# q (in base 10)\n")
        file.write(str(q) + "\n\n")
        file.write("# p*q (in base 10)\n")
        file.write(str(p_q) + "\n")

    # informs user when data has been written to the file
    print("Data written to: " + output_filename)


def ln(x):
    # Return the logarithm of 'x' to base 'e' (natural logarithm)
    return math.log(x, math.e)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <n>")
    else:
        num = sys.argv[1]
        ptimesq(int(num))