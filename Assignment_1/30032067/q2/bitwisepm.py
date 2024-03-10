from bitarray import bitarray
import sys


def bitwise_pm(txt_filename: str, pat_filename: str):
    """
    Performs bitwise pattern matching using a sliding window approach.

    Args:
        txt_filename (str): the name of the file containing the text
        pat_filename (str): the name of the file containing the pattern

    Returns:
        list: A list containing the starting positions of occurrences of the pattern in the text.
    """

    # initialize txt, pat and their lengths
    data = read_input(txt_filename, pat_filename)
    txt = data[0]
    pat = data[1]
    n = len(txt)
    m = len(pat)

    # if the pattern is longer than the text, return empty list
    if m > n:
        return []

    # initialize occurrences return value
    occurrences = []

    # compute the initial bitvector naively
    initial_bitvector = compute_initial_bitvector(txt[:m], pat)
    prev_bitvector = initial_bitvector
    # if the initial bitvector is a match, append 0, the starting index
    if not initial_bitvector[0]:
        occurrences.append(0)

    # loop through the remaining text
    for j in range(m, n):
        # find the delta
        deltaj = compute_deltaj(txt[j], pat)
        # find the new bitvector using the delta
        curr_bitvector = compute_bitvector_from_deltaj(prev_bitvector, deltaj)

        # if the pattern is a match, append the occurrence
        if not curr_bitvector[0]:
            occurrences.append(j - m + 1)

        # update prev_bitvector
        prev_bitvector = curr_bitvector

    # output to the file
    output_filename = "output_bitwisepm.txt"
    output_data(occurrences, output_filename)


def compute_delta(txt_char, pat_char):
    """
    compares 2 characters, returns 1 if its not a match, 0 otherwise
    Args:
        txt_char: character from text
        pat_char: character from pattern

    Returns:
        1 if its not a match, 0 otherwise
    """

    return 1 if txt_char != pat_char else 0


def compute_initial_bitvector(txt, pat):
    """
    computes the initial bitvector naively
    Args:
        txt: text
        pat: pattern

    Returns:
        bitvector with the inital values
    """

    # initialize values. New bitvector
    m = len(pat)
    initial_bitvector = bitarray([0] * m)
    # the length of the bitvector is always m, that is the number of iterations we need
    for iteration in range(m):
        # carry out comparisons
        for i in range(m-iteration):
            compare = compute_delta(txt[i+iteration], pat[i])
            if compare == 1:
                initial_bitvector[iteration] = 1

    # return the bitvector
    return initial_bitvector


def compute_deltaj(txt_char, pat):
    """
    calculates delta by comparing every character in pattern with the next character in text
    Args:
        txt_char: character in text
        pat: the pattern

    Returns:
        a bitvector with the delta j
    """

    m = len(pat)
    deltaj = bitarray()
    for i in range(m, 0, -1):
        deltaj.append(compute_delta(txt_char, pat[i-1]))
    return deltaj


def compute_bitvector_from_deltaj(prev_bitvector, deltaj):
    """
    calculates the next bitvector using the previous bitvector and delta j and performing calculations
    Args:
        prev_bitvector: the previous bitvector
        deltaj: delta j

    Returns:
        next bitvector
    """

    # shifts the bitvector to the left by one
    shifted_bitvector = prev_bitvector[1:]
    shifted_bitvector.append(False)

    # carries out OR function between the shifted bitvector and delta j
    new_bitvector = shifted_bitvector | deltaj

    # returns the new bitvector
    return new_bitvector


def read_input(txt_filename: str, pat_filename: str):
    """
    when given 2 filenames, stores the contents as strings and returns them
    Args:
        txt_filename: name of the file where the text is stored
        pat_filename: name of the file where the pattern is stored

    Returns:
        2 strings, one containing the text and the other containing the pattern
    """

    txt_file = open(txt_filename, 'r')

    txt = txt_file.read()
    txt_file.close()

    pat_file = open(pat_filename, 'r')
    pat = pat_file.read()
    pat_file.close()
    return txt, pat


def output_data(data: list, output_filename: str):
    """
    when given a list and a filename, outputs each element on a new line in the specified file
    Args:
        data: a list containing the data
        output_filename: the name of the file where the data has to be output

    Returns:
        None
    """

    with open(output_filename, "w") as file:
        for element in data:
            file.write(str(element) + "\n")

    # informs user when data has been written to the file
    print("Data written to: " + output_filename)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python your_script.py txt_file pat_file")
    else:
        txt_file = sys.argv[1]
        pat_file = sys.argv[2]
        bitwise_pm(txt_file, pat_file)
