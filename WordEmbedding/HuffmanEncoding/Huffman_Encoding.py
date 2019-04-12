# -*- coding: utf-8 -*-
"""
Preparation for study of Word2Vec word embedding techniques
Practice Usage of Huffman Ecoding
Author : Shixuan (Wayne) Li
Last Modified : Oct 8, 2018
"""

""" Word Count Function
Count the frequency each word appears
Generate projection table
"""
def count_freq(text):
    chars = []
    chars_freqs = []
    for i in range(0, len(text)):
        if text[i] in chars:
            pass
        else:
            chars.append(text[i])
            char_freq = (text[i], text.count(text[i]))
            chars_freqs.append(char_freq)
    return chars_freqs


""" Node 
Class Definition
"""
class Node:
    def __init__(self, freq):
        self.left = None
        self.right = None
        self.father = None
        self.freq = freq

    def isLeft(self):
        return self.father.left == self


""" Create Node Function
@ Param freqs : A list of freqs
@ Return : A list of Nodes created in correspondance to the input
"""
def createNodes(freqs):
    return [Node(freq) for freq in freqs]


""" Create Huffman Tree
@ Param nodes : List of nodes
@ Return : The root of the created Huffman Tree
"""
def createHuffmanTree(nodes):
    # Deep copy of the nodes into queue
    queue = nodes[:]
    # Start iteration until queue has only one item left
    while len(queue) > 1:
        # Sort the queue by each node's freq
        queue.sort(key=lambda item: item.freq)
        # Get left & right children of the new node by extracting the two lowest-freq nodes
        node_left = queue.pop(0)
        node_right = queue.pop(0)
        # Create the new node combining the two children defined above
        # The new node has freq as the sum of its two children
        node_father = Node(node_left.freq + node_right.freq)
        node_father.left = node_left
        node_father.right = node_right
        # Link the children to the father (new node)
        node_left.father = node_father
        node_right.father = node_father
        # Append the new node (father) to the end of the queue
        queue.append(node_father)
    # The only node left in the queue is the root of the Huffman Tree
    # Thus set its father link as None
    queue[0].father = None
    # Return the root of the Huffman Tree
    return queue[0]


""" Huffman Encoding Function
@ Param nodes : A list of nodes
@ Param root : The root of the Huffman Tree
@ Return : The list of codes in correspondance of the input nodes
"""
def huffmanEncoding(nodes, root):
    codes = [''] * len(nodes)
    for i in range(len(nodes)):
        node_tmp = nodes[i]
        while node_tmp != root:
            if node_tmp.isLeft():
                codes[i] = '0' + codes[i]
            else:
                codes[i] = '1' + codes[i]
            node_tmp = node_tmp.father
    return codes


""" Encode the text
@ Param text : Text to be encoded
@ Param chars_freqs : A mapping from each char to its freq
@ Param codes : The code for chars with sequence correspondance to the chars_freq
@ Return : Huffman encoded string
"""
def encodeStr(text, chars_freqs, codes):
    huffmanStr = ''
    for char in text:
        i = 0
        for item in chars_freqs:
            if char == item[0]:
                huffmanStr += codes[i]
            i += 1
    return huffmanStr


""" Decode the text
@ Param huffmanStr : The Huffman encoded string to be decoded
@ Param chars_freqs : A mapping from each char to its freq
@ Param codes : The code for chars with sequence correspondance to the chars_freq
@ Return : The decoded original text
"""
def decodeStr(huffmanStr, chars_freqs, codes):
    originStr = ''
    while huffmanStr != '':
        i = 0
        for item in codes:
            if item in huffmanStr:
                if huffmanStr.index(item) == 0:
                    originStr += chars_freqs[i][0]
                    huffmanStr = huffmanStr[len(item):]
            i += 1
    return originStr


if __name__ == '__main__':
    text = input('The text to encode: ')
    chars_freqs = count_freq(text)
    # Notice that the seqence of items in the following definitions matters for our implementation
    # The variables should have index corresponding storage of items
    nodes = createNodes([item[1] for item in chars_freqs])
    root = createHuffmanTree(nodes)
    codes = huffmanEncoding(nodes, root)
    huffmanStr = encodeStr(text, chars_freqs, codes)
    orignStr = decodeStr(huffmanStr, chars_freqs, codes)
    print ('Encode result: ' + huffmanStr)
    print ('Decode result: ' + orignStr)
