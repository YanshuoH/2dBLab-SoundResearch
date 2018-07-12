import sys

from algo.text import extract_note_names
from model.phrase import Phrase
from model.track import Track
from utils.utils import create_midi_file, save_midi_file

if len(sys.argv) < 2:
    print('Usage: %s <destination>' % sys.argv[0])
    sys.exit(1)

destination = sys.argv[1]

# input_str = 'You can hear the whistle blow a hundred miles'
# input_str = 'Oh my love for the first time in my life, My mind is wide wide open'
# input_str = 'there is a lady who sure all that glitter is gold and shes buying a stairway to heaven?'
input_str = 'Music gives a soul to the universe, wings to the mind, flight to the imagination and life to everything'
note_names = extract_note_names(input_str)
phrase = Phrase(note_names=note_names, start_time=0, bar_count=16, std_octave=5)
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
