from model.drum import DrumBar
from model.track import Track
from utils.utils import create_midi_file, save_midi_file

midi_instance = create_midi_file(num_tracks=1, file_format=1)
tempo = 90
track1 = Track.create_track(midi_instance=midi_instance, track=0, channel=9, tempo=tempo)

time = 0
bar_count = 2
volume = 80

drum_bars = DrumBar(start_time=0, bar_count=1).build_style1()
for one_bar in drum_bars:
    for note in one_bar:
        track1.add_note(note)

save_midi_file('test.mid', midi_instance)
