import re


def q2b(ustring: str):
    """
        convert GB character to utf-8 standard
    """
    res = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif 65281 <= inside_code <= 65374:
            inside_code -= 65248
        res += chr(inside_code)
    return res


def sanitize_str(s: str):
    s.strip()
    pattern = re.compile('[^a-zA-Z\s]+', re.UNICODE)
    return pattern.sub('', s)


def sanitize(s: str):
    """
        sanitize function will parse the input string,
        split into array of string on every occurrence of:
            - \n
            - !
            - .
            - 。
            - ,
            - ?
        remove none alphabet item if there's one single character in item
    """
    # GB to utf8
    s = q2b(s)
    print("====> q2b result: " + s)
    # Splitting
    str_group_list = re.split('\n|!|\.|。|,|\?|', s)
    f = filter(None, str_group_list)
    str_group_list = list(f)
    # Trim empty spaces twice
    str_group_list = [sanitize_str(item).lower() for item in str_group_list]

    # Trim empty group again group
    result_list = list(filter(None, str_group_list))
    return result_list


alphabet_to_note_name = {
    'a': 'C',
    'b': 'D',
    'c': 'E',
    'd': 'F',
    'e': 'G',
    'f': 'A',
    'g': 'B',
    'h': 'C',
    'i': 'D',
    'j': 'E',
    'k': 'F',
    'l': 'G',
    'm': 'A',
    'n': 'B',
    'o': 'C',
    'p': 'D',
    'q': 'E',
    'r': 'F',
    's': 'G',
    't': 'A',
    'u': 'B',
    'v': 'C',
    'w': 'D',
    'x': 'E',
    'y': 'F',
    'z': 'G',
    '0': 'A',
    '1': 'B',
    '2': 'C',
    '3': 'D',
    '4': 'E',
    '5': 'F',
    '6': 'G',
    '7': 'A',
    '8': 'B',
    '9': 'C',
}


def extract_chord(s: str):
    """
        Something funny happens here.
        We try to identify main chord of a sentence.
        But the choices are different
    """
    pass


def extract_note(v: str):
    """
        Another funny thing here.
        A character is a note, but what about its octave position ?
    """
    if v not in alphabet_to_note_name:
        return None
    return alphabet_to_note_name[v]


def extract_note_names(s: str):
    note_names = []
    for v in s:
        if v == '':
            continue
        c = extract_note(v)
        if c is None:
            continue
        note_names.append(c)
    return note_names


def build_melody_from_phrase(phrase, bar_count: int= 4, std_octave: int = 4, std_volume: int = 80):
    # split and do some sanitizing for safety
    words = phrase.split(' ')
    words = [sanitize_str(word) for word in words]
    words = list(filter(None, words))

    # each word corresponds a melody (without octave definition yet)
    word_note_names_dict = {}
    for word in words:
        note_names = extract_note_names(word)
        if len(note_names) == 0:
            continue
        word_note_names_dict[word] = note_names

    print("====> phrase %s build note names %s" % (phrase, word_note_names_dict))
    # whole beats of one bar
    whole_duration = 4 * bar_count
    word_portion = whole_duration / len(words)
    # now each word share certain portion of one bar, which depends on its length
    # @TODO: this algorithm should be improved as the sound seems too random
    word_note_portion_dict = {}
    for word, note_names in word_note_names_dict.items():
        portion = word_portion / len(note_names)
        word_note_portion_dict[word] = portion
        print("====> word %s, each note shared %.2f portion" % (word, portion))

    # @TODO: series of notes with pitch shifting remains TBD
    # @TODO: series of notes with volume shifting remains TBD
    result = []
    for word in words:
        note_names = word_note_names_dict[word]
        duration = word_note_portion_dict[word]
        for note_name in note_names:
            result.append(dict(note_name=note_name, duration=duration, octave=std_octave, volume=std_volume))

    return result






