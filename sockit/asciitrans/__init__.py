"""
Translation table for transliteration of non-ASCII characters.
"""
asciitrans = str.maketrans({
    u"\xc0": "A",
    u"\xc1": "A", # Remove accent mark over A
    u"\xc2": "A", # Remove hat mark over A
    u"\xc3": "A", # Remove ~ over A
    u"\xc4": "A",
    u"\xc5": "A", # Remove ring over A
    u"\xc6": "AE",
    u"\xc7": "C",
    u"\xc8": "E",
    u"\xc9": "E", # Remove acute over E
    u"\xca": "E",
    u"\xcb": "E",
    u"\xcc": "I",
    u"\xcd": "I",
    u"\xce": "I",
    u"\xcf": "I", # Remove diaeresis over I
    u"\xd0": "D",
    u"\xd1": "N", # Remove ~ on top of N
    u"\xd2": "O", # Remove grave over O
    u"\xd3": "O",
    u"\xd4": "O", # Remove hat over O
    u"\xd5": "O", # Remove ~ over O
    u"\xd6": "O", # Remove diaeresis over O
    u"\xd7": "x", # Replace multiplication sign
    u"\xd8": "O",
    u"\xd9": "U", # Remove grave over U
    u"\xda": "U", # Remove acute over U
    u"\xdb": "U", # Remove hat over U
    u"\xdc": "U", # Remove diaeresis over U
    u"\xdd": "Y", # Remove acute over Y
    u"\xde": "Th", # Replace capital letter thorn
    u"\xdf": "s", # Replace eszett with single s (assuming lower case) 
    u"\xe0": "a", # Remove grave above a 
    u"\xe1": "a", # Remove acute above a 
    u"\xe2": "a", # Remove circumflex above a 
    u"\xe3": "a", # Remove ~ above a
    u"\xe4": "a", # Remove diaeresis above a   
    u"\xe5": "a", # Remove ring above a 
    u"\xe6": "ae", # Replace ae single letter with ae 
    u"\xe7": "c", # Remove tail on c
    u"\xe8": "e", # Remove grave on e
    u"\xe9": "e", # Remove acute on e
    u"\xea": "e",
    u"\xeb": "e",
    u"\xec": "i",
    u"\xed": "i",
    u"\xee": "i",
    u"\xef": "i", # Remove diaeresis on i
    u"\xf0": "d",
    u"\xf1": "n", # Remove ~ on top of n
    u"\xf2": "o",
    u"\xf3": "o",
    u"\xf4": "o", # Remove hat over o
    u"\xf5": "o",
    u"\xf6": "o", # Remove diaeresis over o 
    u"\xf7": None, # Remove math symbol
    u"\xf8": "o",
    u"\xf9": "u", # Remove grave over u 
    u"\xfa": "u", # Remove acute over u 
    u"\xfb": "u", # Remove hat over u
    u"\xfc": "u", # Remove diaeresis over u 
    u"\xfd": "y", # Replace accent over y
    u"\xfe": "th", # Replace lower case thorn
    u"\xff": "y", # Remove diaeresis over y
})
