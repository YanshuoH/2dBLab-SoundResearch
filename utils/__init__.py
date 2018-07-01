from midiutil import MIDIFile


def create_midi_file(num_tracks: int, file_format: int):
    return MIDIFile(numTracks=num_tracks, file_format=file_format)


def save_midi_file(filename: str, midi_file: MIDIFile):
    with open(filename, "wb") as output_file:
        midi_file.writeFile(output_file)
    print("====> file %s saved." % filename)