import sys

from algo.sound import note_result_to_notes
from model.note import Note
from model.track import Track
from utils.utils import read_note_from_sound_file, create_midi_file, save_midi_file

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
note_result = read_note_from_sound_file(filename)
print(note_result)

midi_instance = create_midi_file(num_tracks=1, file_format=1)
tempo = 90
volume = 80
track1 = Track.create_track(midi_instance=midi_instance, track=0, channel=0, tempo=tempo)
note_result_to_notes(note_result, tempo=tempo)
# for note_dict in note_result:
#     if note_dict['duration'] <= 0:
#         continue
#     note = Note(pitch=note_dict['pitch'], time=note_dict['time'], duration=note_dict['duration'],
#                 volume=note_dict['volume'])
#     track1.add_note(note)

# save_midi_file('test.mid', midi_instance)
