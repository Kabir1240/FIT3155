import sys
from bitarray import bitarray


"""Main Function"""
def zip_file(filename: str, window: int, buffer: int) -> None:
    """
    File encoder using assignment 3 specifications
    Args:
        filename: name of the file from which ASCII text is extracted
        window: window for LZ encoding
        buffer: Buffer for LZ encoding

    Returns:
    Writes a bit stream to <filename>.bin
    """

    string = read_input(filename)
    # init data needed for header
    filename_len = len(filename)
    string_len = len(string)
    header = bitarray()

    # Information in header part
    #   - MetaData
    #       - Length of input filename using Elias
    header.extend(elias_encoding(filename_len + 1))
    #       - Encode characters in filename using 8-bit ASCII code
    header.extend(string_to_ascii_8bit(filename))
    #       - Size of input inside the input file using Elias
    header.extend(elias_encoding(string_len + 1))

    # - Number of distinct ASCII characters inside the file using Elias
    freq = calc_freq(string)
    header.extend(elias_encoding(len(freq) + 1))

    # huffman code words for distinct characters
    nodes = create_bst(freq)
    huffman_code = huffman_code_tree(nodes[0][0])

    # sort it in a list for easy use
    huffman_sorted = [bitarray()] * 128
    for i in huffman_code:
        # Ensure it's a printable ASCII character
        if 0 <= ord(i[0]) < 128:
            huffman_sorted[ord(i[0])] = i[1]

    #   - For each distinct character
    for i in range(128):
        if huffman_sorted[i] != bitarray():
            #       - Encode each distinct character with 8-bit ASCII code
            header.extend(string_to_ascii_8bit(chr(i)))
            #       - Encode length of huffman code assigned to the character using Elias
            header.extend(elias_encoding(len(huffman_sorted[i]) + 1))
            #       - Encode the variable-length Huffman codeword assigned to that distinct character
            # print("Huffman encoding for " + chr(i) + ": ", huffman_sorted[i])
            header.extend(huffman_sorted[i])

    data = bitarray()
    # Information in data part
    #   - Encode each computed LZ77 3-tuples of the form ⟨offset, length, next char⟩, while processing the input text,
    #   using the search window size of W and lookahead buffer size of L
    lz = lz77_encoding(string, window, buffer)

    for i in lz:
        #           - encoding offset and length – both integers – using their respective variable length Elias
        #           codewords (over the non-negative range)
        data.extend(elias_encoding(i[0] + 1))
        data.extend(elias_encoding(i[1] + 1))
        #           - encoding next char using its assigned variable-length Huffman codeword.
        # print("Huffman encoding for " + i[2] + ": ", huffman_sorted[ord(i[2])])
        data.extend(huffman_sorted[ord(i[2])])

    # combine everything as a bit stream and
    final_result = bitarray()
    final_result.extend(header)
    final_result.extend(data)
    # output it to a bin file in packed bytes
    output_filename = file_name + ".bin"
    write_packed_bytes(final_result, output_filename)


"""Elias Encoding Below"""
def elias_encoding(n: int) -> bitarray:
    """
    Encodes non-negative integers using Elias encoding
    Args:
        n: integer to encode

    Returns:
    bitarray() of encoded integer
    """

    l_prev = n.bit_length()
    code_seq = bitarray()
    code_seq.extend(bin(n)[2:])

    while l_prev != 1:
        l_i = l_prev - 1
        # get the minimal binary code/representation
        mbc = bitarray(bin(l_i)[2:])
        # reset the first bit to 0
        mbc[0] = False
        # append length_component to code_component
        code_seq = mbc + code_seq
        # reset L
        l_prev = len(mbc)

    # print("Elias encoding for " + str(n-1) + ": ", code_seq)
    return code_seq


"""ASCII Encoding Below"""
def string_to_ascii_8bit(text: str) -> bitarray:
    """
    Encodes ASCII characters
    Args:
        text: text to encode

    Returns:
    bitarray() of encoded text
    """

    ascii_8bit = bitarray()
    for char in text:
        ascii_code = ord(char)
        # Ensure it's 8 bits long
        binary_code = bin(ascii_code)[2:].zfill(8)
        # print("ASCII encoding for " + char + ": ", binary_code)
        ascii_8bit.extend(bitarray(binary_code))
    return ascii_8bit


"""Huffman Encoding Below"""
def huffman_code_tree(node, bin_string=bitarray()):
    """
    Recursively gets data from a huffman bst tree
    Args:
        node: root node
        bin_string: memo for result. Initialized automatically when called for the first time

    Returns:
    Huffman encoding for the string inside the huffman bst
    """
    # If node is a leaf (a character)
    if type(node) is str:
        return [(node, bin_string)]

    (l, r) = node.children()
    left_tree = huffman_code_tree(l, bin_string + bitarray('0'))
    right_tree = huffman_code_tree(r, bin_string + bitarray('1'))

    return left_tree + right_tree


def calc_freq(string: str) -> list:
    """
    Calculates the frequency of each individual character inside a string
    Args:
        string: the string

    Returns:
    a list of unique characters and how many times they are repeated. Sorted by the frequency
    """

    # Initialize the frequency array with zeros for all printable ASCII characters
    # ASCII has 128 printable characters
    freq = [0] * 128

    # Calculate character frequencies
    for c in string:
        # Ensure it's a printable ASCII character
        if 0 <= ord(c) < 128:
            freq[ord(c)] += 1

    # Create a list of (character, frequency) pairs
    freq_list = [(chr(i), freq[i]) for i in range(128) if freq[i] > 0]

    # Sort the list based on frequency in ascending order
    freq_list.sort(key=lambda x: x[1])

    return freq_list


def create_bst(nodes):
    """
    Creates a Huffman Binary Search Tree (BST) from a list of nodes sorted by ascending order of frequency.

    Args:
        nodes: A list of individual characters and their frequency, sorted by ascending order of frequency.

    Returns:
        nodes: The nodes of the Huffman BST tree.
    """

    while len(nodes) > 1:
        # Get the key and frequency of the first and second nodes
        (key1, c1) = nodes[0]
        (key2, c2) = nodes[1]
        # Remove the first two nodes from the list
        nodes = nodes[2:]

        # Create a new node representing the combination of the first two nodes
        node = NodeTree(key1, key2)

        # Append the new node and its combined frequency to the list
        nodes.append((node, c1 + c2))

        # Sort the list of nodes by frequency in ascending order
        nodes = sorted(nodes, key=lambda x: x[1], reverse=False)

    # Return the nodes of the Huffman BST tree
    return nodes



class NodeTree(object):

    def __init__(self, left=None, right=None):
        self.left = left #Node(left)
        self.right = right #Node(right)


    def children(self):
        return self.left, self.right

    def nodes(self):
        return self.left, self.right

    def __str__(self):
        return '%s%s' % (self.left, self.right)


"""Lempel-Ziv LZ77 Encoding Below"""
def lz77_encoding(txt: str, window_size: int, lookahead_buffer: int):
    """
    Encodes a text with LZ77 encoding
    Args:
        txt: a string to encode
        window_size: window size (maximum distance to look back)
        lookahead_buffer: lookahead buffer (maximum number of characters to match)

    Returns:
    a list of tuples, each one with the LZ77 encoding of a character in the text
    """

    # Initialize the current position in the text
    curr_pos = 0
    # Initialize a list to store the LZ77 encoding
    code_list = []

    while curr_pos < len(txt):
        # Extract the lookahead buffer (substring) from the current position
        buffer = txt[curr_pos:curr_pos + min(lookahead_buffer, len(txt) - curr_pos)]

        # Extract the search window (substring to look back)
        search_window = txt[max(curr_pos - window_size, 0):curr_pos]

        # Find the offset and length of the best match between buffer and search_window
        offset, length = find_occurrences(buffer, search_window)

        if offset == 0:
            # If no match is found, move one character forward
            curr_pos = curr_pos + 1
        else:
            # If a match is found, move forward by the length of the match plus 1
            curr_pos = curr_pos + length + 1

        if curr_pos - 1 >= len(txt):
            # Determine the next character. End of text is marked with '$'
            next_char = '$'
        else:
            # Extract the next character from the text
            next_char = txt[curr_pos - 1]

        # Append the tuple (offset, length, next_char) to the code list
        code_list.append((offset, length, next_char))

    # Return the list of LZ77 encoding tuples
    return code_list


def find_occurrences(buffer, window):
    """
    Finds occurrences of the buffer within the window and returns the offset and length of the match.

    Args:
        buffer: The current lookahead buffer.
        window: The search window to look back in.

    Returns:
        offset: The offset from the current position to the start of the match.
        length: The length of the matched substring.
    """

    if len(window) < 1:
        offset = 0
        length = 0
    else:
        # Call the find_match function to determine the offset and length of the match
        offset, length = find_match(buffer, window)

    return offset, length


def find_match(buffer, window):
    """
    Finds the best match of the buffer within the search window and returns the offset and length of the match.

    Args:
        buffer: The current lookahead buffer.
        window: The search window to look back in.

    Returns:
        offset: The offset from the current position to the start of the best match.
        length: The length of the best matched substring.
    """

    # Create a new string that combines buffer, window, and a part of buffer for circularity
    new_string = buffer + window + buffer[:max(1, len(buffer) - len(window))]

    # Initialize variables to track the best match's length and offset
    length, offset = 0, 0

    # Initialize a counter variable
    i = 0

    # Calculate the Z-array for the new string
    Z = calculate_z(new_string)

    # Iterate through the characters in the search window
    for i in range(len(window)):
        # Check if the Z-value at the current position indicates a longer match
        if Z[i + len(buffer)] > length:
            # Update the offset to the current position
            offset = len(window) - i

            # Update the length to the new maximum match length
            length = Z[i + len(buffer)]

    # Return the offset and length of the best match
    return offset, length



def calculate_z(string):
    """
    Calculate the Z-array for the given string.

    Args:
        string: The input string for which to compute the Z-array.

    Returns:
        z: The computed Z-array.
    """

    # Initialize Z-array with Zeroes as well as the left and right boundaries of the z-box
    z = [0] * len(string)
    left = 0
    right = 0

    # Start from index 1 (since Z[0] is set to 0)
    for k in range(1, len(string)):
        if k > right:
            # Initialize left and right boundaries for a new Z-box
            left = right = k

            # While characters match, and we are within the string bounds, expand the Z-box
            while right < len(string) and string[right] == string[right - left]:
                right += 1

            # Store the Z-value for this position
            # Adjust right boundary
            z[k] = right - left
            right -= 1

        else:
            # We are operating inside an existing Z-box
            # Calculate the corresponding position in the Z-box
            k1 = k - left

            # If the Z-value at k1 does not extend beyond the right boundary, just copy it
            if z[k1] < right - k + 1:
                z[k] = z[k1]
            else:
                # Start a new Z-box from this position
                left = k

                # While characters match, and we are within the string bounds, expand the Z-box
                while right < len(string) and string[right] == string[right - left]:
                    right += 1

                z[k] = right - left
                right -= 1

    # Return the final Z-array
    return z



"""Input and Output Functions Below"""
def read_input(filename: str):
    """
    Reads the contents of afile and returns it as a string.

    Args:
        filename: Name of the .asc file to read.

    Returns:
        A string containing the contents of the file.
    """

    try:
        with open(filename, 'rb') as asc_file:
            asc_content = asc_file.read().decode('utf-8')
        return asc_content
    except FileNotFoundError:
        return None


def write_packed_bytes(bitstream, output_filename):
    """
    Python function that takes a bitstream and converts it to a binary file with padding,
    ensuring the length of the bitstream is a perfect multiple of 8 bits (1 byte).
    Args:
        bitstream: a bitarray()
        output_filename: bin file to write to

    Returns:

    """
    # Calculate the number of padding bits needed to make the length a multiple of 8
    padding_bits = (8 - (len(bitstream) % 8)) % 8

    # Pad the bitstream with the required number of zeros
    padded_bitstream = bitstream + bitarray('0' * padding_bits)

    # Convert the padded bitstream to bytes
    packed_bytes = bytes(int(padded_bitstream[i:i+8].to01(), 2) for i in range(0, len(padded_bitstream), 8))

    # Write the packed bytes to the output file
    with open(output_filename, 'wb') as output_file:
        output_file.write(packed_bytes)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python your_script.py <filename> <W> <L>")
    else:
        file_name = sys.argv[1]
        w = int(sys.argv[2])
        l = int(sys.argv[3])
        zip_file(file_name, w, l)
