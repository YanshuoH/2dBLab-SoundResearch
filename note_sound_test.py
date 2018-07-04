import sys

from model.melody import Melody
from model.phrase_2 import Phrase2
from model.track import Track
from utils.utils import read_note_from_sound_file, create_midi_file, save_midi_file

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
note_result = read_note_from_sound_file(filename)
melody = Melody(note_result).build()
phrase = Phrase2(melody.bar_note_result_list)
bars_of_notes = phrase.standardize(std_octave=4).bars_of_notes
chords = phrase.build_chords(std_octave=2)
appregios = phrase.build_appregios(std_octave=3)
midi_instance = create_midi_file(num_tracks=3, file_format=1)
tempo = 90
volume = 80
track1 = Track.create_track(midi_instance=midi_instance, track=0, channel=0, tempo=tempo)
track2 = Track.create_track(midi_instance=midi_instance, track=1, channel=0, tempo=tempo)
track3 = Track.create_track(midi_instance=midi_instance, track=2, channel=0, tempo=tempo)

for one_bar in bars_of_notes:
    for note in one_bar:
        track1.add_note(note=note)
for chord in chords:
    track2.add_chord(chord=chord)
for appregio in appregios:
    track3.add_appregio(appregio=appregio)

save_midi_file('test.mid', midi_instance)
