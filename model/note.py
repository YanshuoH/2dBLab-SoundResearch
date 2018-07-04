class Note:
    """
    A note is a note with all arguments required for MIDIUtil's addNote function
    :param note_name is C5 like str
    """

    def __init__(self, pitch: int, time: int, duration: int, volume: int, note_name: str = ''):
        self.pitch = int(round(pitch))
        self.time = float(time)
        self.duration = float(duration)
        self.volume = int(volume)
        if note_name != '':
            self.note_name = note_name
        elif self.pitch in reverse_note_map:
            # pitch to c major note name
            self.note_name = reverse_note_map[self.pitch]
        else:
            self.note_name = ''

    def __repr__(self):
        return 'Note note_name = %s, pitch = %d, time = %f, duration = %f, volume = %d' % (
            self.note_name, self.pitch, self.time, self.duration, self.volume)


def note_name_to_pitch(name: str):
    if name in note_map:
        return note_map[name]
    return None


def note_name_octave_to_pitch(name: str, octave: int):
    note_name = name + str(octave)
    return note_name_to_pitch(note_name)


duration_map = dict(
    sixteenth_note=1 / 4,
    eighth_note=1 / 2,
    quarter_note=1,
    half_note=2,
    whole_note=4,
)
reverse_duration_map = {v: k for k, v in duration_map.items()}
standard_duration_list = [v for k, v in duration_map.items()]

volume_map = dict(
    ppp=16,
    pp=32,
    p=48,
    mp=64,
    mf=80,
    f=96,
    ff=112,
    fff=127,
)
reverse_volume_map = {v: k for k, v in volume_map.items()}
standard_volume_list = [v for k, v in volume_map.items()]

note_map = dict(
    A0=21,
    B0=23,
    C1=24,
    D1=26,
    E1=28,
    F1=29,
    G1=31,
    A1=33,
    B1=35,
    C2=36,
    D2=38,
    E2=40,
    F2=41,
    G2=43,
    A2=45,
    B2=47,
    C3=48,
    D3=50,
    E3=52,
    F3=53,
    G3=55,
    A3=57,
    B3=59,
    C4=60,
    D4=62,
    E4=64,
    F4=65,
    G4=67,
    A4=69,
    B4=71,
    C5=72,
    D5=74,
    E5=76,
    F5=77,
    G5=79,
    A5=81,
    B5=83,
    C6=84,
    D6=86,
    E6=88,
    F6=89,
    G6=91,
    A6=93,
    B6=95,
    C7=96,
    D7=98,
    E7=100,
    F7=101,
    G7=103,
    A7=105,
    B7=107,
    C8=108,
    D8=110,
    E8=112,
    F8=113,
    G8=115,
    A8=117,
    B8=119,
    C9=120,
)

reverse_note_map = {v: k for k, v in note_map.items()}
c_major_pitch_list = [v for k, v in note_map.items()]
