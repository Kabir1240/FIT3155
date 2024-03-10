import sys


def bwt_pattern_matching(bwt_filepath, pat_filepath, distance):
    """
    bwt pattern matching using BWT
    Args:
        bwt_filepath: path containing bwt processed string
        pat_filepath: path containing pattern to match with
        distance: hamming distance

    Returns:
        an array of number of matches
    """

    distance = int(distance)
    string = read_file_as_string(bwt_filepath)
    pattern = read_file_as_string(pat_filepath)
    # initialize values, final is the return value
    n = len(string)
    m = len(pattern)
    final = []
    n_occurrences, rank = compute_rank(string)

    def backward_search(pattern_index, sp, en, distance):
        """
        searches backwards for matches using recursion
        Args:
            pattern_index: index of current pattern character to match
            sp: starting position
            en: ending position
            distance: remaining hamming distance

        Returns:
            number of matches
        """
        ret_val = 0

        # base cases
        if distance < 0:
            return 0
        elif pattern_index < 0 and distance == 0:
            return en - sp + 1
        elif pattern_index < 0 and distance > 0:
            return 0

        # loop through for every individual character in rank
        for i in range(len(rank)):
            sp_copy = sp
            en_copy = en
            rank_index = rank[i]
            # if the character exists
            if rank[i] is not None:
                # find new sp and ep values for the character
                while n_occurrences[i][sp_copy] == 0 and sp_copy > 0:
                    sp_copy -= 1
                if string[sp] == chr(i+36):
                    next_sp = rank_index + n_occurrences[i][sp_copy] - 1
                else:
                    next_sp = rank_index + n_occurrences[i][sp_copy]

                while n_occurrences[i][en_copy] == 0 and en_copy > 0:
                    en_copy -= 1
                next_en = rank_index + n_occurrences[i][en_copy] - 1

                if next_sp > next_en and distance > 0:
                    ret_val += backward_search(pattern_index - 1, 0, n-1, distance-1)
                elif next_sp > next_en and distance == 0:
                    ret_val += 0
                else:
                    # for the area that matches successfully, do not decrease distance because it matched
                    if chr(i + 36) == pattern[pattern_index]:
                        ret_val += backward_search(pattern_index - 1, next_sp, next_en, distance)

                    # for the "mismatched area", decrease distance for the next round
                    else:
                        ret_val += backward_search(pattern_index - 1, next_sp, next_en, distance-1)
        # return number of matches
        return ret_val

    # loop through hamming distance
    for i in range(distance+1):
        final.append(backward_search(m-1, 0, n-1, i))

    write_list_to_file("output_hdbwtpm.txt", final)


def compute_rank(bwt_string: str):
    """
    Preprocesses rank and n_occurrence for bwt pattern matching
    Args:
        bwt_string: bwt processed string

    Returns:
        rank and n_occurrence
    """

    n = len(bwt_string)
    string_sorted = sorted(bwt_string)
    rank = [None] * 91
    counter = [0] * 91
    n_occurrence = [[0] * n for _ in range(91)]
    for i in range(n):
        index = ord(string_sorted[i]) - 36
        if rank[index] is None:
            rank[index] = i

        index = ord(bwt_string[i]) - 36
        counter[index] += 1
        n_occurrence[index][i] = counter[index]

    return n_occurrence, rank


def read_file_as_string(file_path):
    """
    reads file and converts to string
    Args:
        file_path: the filename and location
    Returns:
        a string with the file contents
    """

    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        return None


def write_list_to_file(filename: str, result: list):
    print(result)
    try:
        with open(filename, 'w') as file:
            for i in range(len(result)):
                file.write("d = " + str(i) + ", nMatches = " + str(result[i]) + '\n')
        print(f"Successfully wrote {len(result)} lines to '{filename}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python your_script.py bwt_filename pat_filename hamming_distance")
    else:
        bwt_file = sys.argv[1]
        pat_file = sys.argv[2]
        hamming_distance = sys.argv[3]
        bwt_pattern_matching(bwt_file, pat_file, hamming_distance)

