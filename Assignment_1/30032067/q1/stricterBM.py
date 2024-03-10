import sys


def stricter_bm(txt_filename: str, pat_filename: str):
    """
    boyer moore implementation. Uses bad character rule, matched prefix and a stricter vcersion of good suffix
    to pattern match and return a list of indices of where the pattern occurs in the text.
    Args:
        txt_filename: name of the file containing the text
        pat_filename: name of the file containing the pattern

    Returns:
        a list of indices of where the pattern occurs in the text
    """

    # read data from the files and store it as 2 strings, txt and pat
    input_data = read_input(txt_filename, pat_filename)
    txt = input_data[0]
    pat = input_data[1]

    # defines length of txt and pat
    m = len(txt)
    n = len(pat)
    
    # Preprocessing algorithms
    z_array = get_z_array(pat)
    bc_array = get_ebc_array(pat)
    gs_array = get_gs_array(z_array)
    mp_array = get_mp_array(z_array)

    # value that will be output later
    ret_val = []

    # initialize the process
    pos = 0
    start = None
    stop = None
    # loops through the text. If the pattern exceeds the txt, it ends
    while pos + (n-1) < m:
        # comparison is carried out here, returns the value of mismatch index
        mm_idx = compare(txt, pat, pos, start, stop)

        # reset start and stop every time the comparison is complete
        start = None
        stop = None

        # full match, take value of mp_array[1] or 1, if mp_array[1] == 0
        if mm_idx == pos - 1:
            ret_val.append(pos)
            shift = max(mp_array[1], 1)

        # mismatch
        else:
            # calculate gs_shift and extended bad character shift
            gs_shift = get_gs_shift(pos, mm_idx, n, gs_array, mp_array)
            ebc_shift = get_ebc_shift(pos, mm_idx, bc_array, txt[mm_idx])

            # if gs shift is selected, stop and start are updated as well as shift
            if gs_shift[0] > ebc_shift:
                shift = gs_shift[0]
                start = gs_shift[1]
                stop = gs_shift[2]
            # if ebc is selected, stop and start remain as None while shift is updated
            else:
                shift = ebc_shift

        # update the starting position of the pattern
        pos += shift

    # output the indices to a file titled "output_stricterBM.txt"
    output_data(ret_val, "output_stricterBM.txt")


def compare(txt: str, pat: str, pos: int, start=None, stop=None):
    """
    Given the text, pattern, the current position of the pattern over the text and range of the pattern that is
    currently known to match the text(so these regions can be skipped in explicit character comparisons),
    performs character comparisons and returns position of first mismatched character
    Args:
        txt: text
        pat: pattern
        pos: position of pattern
        start: start
        stop: stop

    Returns:
        index of mismatch
    """

    n = len(pat)
    # if there are no comparisons to skip
    if start is None and stop is None:
        k = pos + n - 1
        while k >= pos and txt[k] == pat[k - pos]:
            k -= 1
        return k
    
    # galil's optimization to skip comparisons
    else:
        k = pos + n - 1
        while k >= stop and txt[k] == pat[k - pos]:
            k -= 1
            
        if k >= stop:
            return k
        
        k = start
        while k >= pos and txt[k] == pat[k - pos]:
            k -= 1
        return k


def get_ebc_array(pat: str):
    """
    given pattern, calculates the extended bad character rule array

    Args:
        pat: the pattern

    Returns: a list of lists that can be used to find bad characters

    """

    m = len(pat)
    bc_array = [[0]*93 for _ in range(m)]                # 93 printable characters in ASCII, 33-126
    for i in range(m):
        for j in range(0, i):
            current = ord(pat[j]) - 33                   # first position starts at 33
            bc_array[i][current] = j + 1
            
    return bc_array
    

def get_z_array(pat: str):
    """
    Implements Gusfield's Z-Algorithm in reverse to compute the reverse z-values of a given string

    Args:
        pat (str): The string to compute reverse z-values for

    Returns:
        a list of reverse Z algorithm values

    """

    pat = pat[::-1]
    z_vals = [None] * len(pat)
    l = 0
    r = 0
    for pos in range(1, len(pat)):
        k = pos
        if pat[k] == pat[0]:
            # case 2
            if k <= r:
                # case 2a
                if z_vals[k-l] < r-k+1:
                    z_vals[k] = z_vals[k-l]
                # case 2b
                elif z_vals[k-l] > r-k+1:
                    z_vals[pos] = r-k+1
                # case 2c
                elif z_vals[k-l] == r-k+1:
                    k = r + 1
                    l = pos
                    while k < len(pat) and pat[k] == pat[k - pos]:
                        k += 1
                    r = k - 1
            else:
                # normal comparison
                k += 1
                l = pos
                while k < len(pat) and pat[k] == pat[k - pos]:
                    k += 1
                r = k - 1
            
        # update zi values
        if z_vals[pos] is None:
            z_vals[pos] = k - pos
    z_vals[0] = len(z_vals)
    return z_vals[::-1]


def get_gs_array(z_array: list):
    """
    Given the z_array, calculate the good suffix array
    Args:
        z_array: reverse Z algorithm values

    Returns: good suffix array

    """
    m = len(z_array)
    gs = [0] * (m + 1)
    j = []
    for p in range(m):
        j = m - (z_array[p]) + 1
        gs[j-1] = p + 1
    return gs
    
    
def get_mp_array(z_array: list):
    """
    given the z_array, calculate the matched prefix array
    Args:
        z_array: the reverse z algorithm values

    Returns:
        a list containing the matched prefix indices
    """

    # O(2N) complexity -> O(N)
    m = len(z_array)
    max_mp = 0
    mp_array = [0] * (m)
    
    for i in range(m):
        if z_array[i] > max_mp and z_array[i] - i == 1:
            mp_array[i] = z_array[i]
            max_mp = z_array[i]
        else:
            mp_array[i] = max_mp
    
    mp_array = mp_array[::-1]
    mp_array.append(0)
    return mp_array


def get_gs_shift(pos: int, mm_idx: int, n: int, gs_array: list, mp_array: list):
    """
        given the mismatch position, the good suffix array and the matched prefix array, computes the good suffix
        shift and the range within the pattern that can be skipped from explicit character comparisons in the
        next iteration
    Args:
        pos: current position of pattern
        mm_idx: index of the mismatch
        n: length of pattern
        gs_array: good suffix array
        mp_array: matched prefix array

    Returns:

    """

    # calculates gs value
    gs_shift = gs_array[mm_idx-pos + 1]
    next_pos = pos + (n - gs_shift)
    p = next_pos + gs_shift
    # if gs shift exists, return that, along with the start and stop values
    if gs_shift > 0:
        return [n-gs_shift, p-((pos+n-1) - mm_idx), p]
    # if gs shift doesnt exist but mp shift does, return that along with the start and stop values
    elif mp_array[mm_idx-pos + 1] > 0:
        return [n - mp_array[mm_idx-pos + 1], next_pos, next_pos + mp_array[mm_idx-pos + 1]]
    # if neither exists, shift by 1 and set start and stop to None
    else:
        return [1, None, None]


def get_ebc_shift(pos: int, mm_idx: int, bc_array: list, mm_char: str):
    """
        given the mismatch position, the bad character and the bad character array, computes the shift resulting
        from the bad character rule and the range within the pattern that can be skipped from explicit character
        comparisons in the next iteration

    Args:
        pos: position of pattern
        mm_idx: mismatch index
        bc_array: extended bad character array
        mm_char: mismatch character

    Returns:

    """

    # returns ebc if the shift > 0 and 1 otherwise
    ebc = mm_idx - pos - bc_array[mm_idx-pos][ord(mm_char) - 33]
    return ebc if ebc > 0 else 1
    

def read_input(txt_filename:str, pat_filename: str):
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
        stricter_bm(txt_file, pat_file)
