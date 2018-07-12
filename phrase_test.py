import sys

from algo.text import extract_note_names
from model.phrase import Phrase
from model.track import Track
from utils.utils import create_midi_file, save_midi_file

if len(sys.argv) < 3:
    print('Usage: %s <destination> <suite>' % sys.argv[0])
    sys.exit(1)

destination = sys.argv[1]
suite_no = int(sys.argv[2])

input_str = None
phrase = None
if suite_no == 1:
    input_str = 'music'
elif suite_no == 2:
    input_str = 'music gives a soul'
elif suite_no == 3:
    input_str = 'Music gives a soul to the universe, wings to the mind, flight to the imagination and life to everything'
elif suite_no == 4:
    input_str = 'meican'
else:
    print('unknown test suite %d' % suite_no)

note_names = extract_note_names(input_str)
if suite_no == 1:
    phrase = Phrase(note_names=note_names, start_time=0, bar_count=1, std_octave=5)
elif suite_no == 2:
    phrase = Phrase(note_names=note_names, start_time=0, bar_count=4, std_octave=5)
elif suite_no == 3:
    phrase = Phrase(note_names=note_names, start_time=0, bar_count=16, std_octave=5)
elif suite_no == 4:
    phrase = Phrase(note_names=note_names, start_time=0, bar_count=1, std_octave=5)
else:
    print('unknown test suite %d' % suite_no)

notes = phrase.build_notes()
chords = phrase.build_chords()
appregios = phrase.build_appregios()
midi_instance = create_midi_file(num_tracks=3, file_format=1)
tempo = 90
track1 = Track(midi_instance=midi_instance, track=0, channel=0, tempo=tempo)
track2 = Track(midi_instance=midi_instance, track=1, channel=0, tempo=tempo)
track3 = Track(midi_instance=midi_instance, track=2, channel=0, tempo=tempo)

for note in notes:
    track1.add_note(note)
for chord in chords:
    track2.add_chord(chord)
for appregio in appregios:
    track3.add_appregio(appregio)

save_midi_file(destination, midi_instance)
