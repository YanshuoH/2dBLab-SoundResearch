import sys

from model.melody import Melody
from model.phrase_2 import Phrase2
from model.track import Track
from utils.utils import read_note_from_sound_file, create_midi_file, save_midi_file, read_pitch_from_sound_file

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
tempo = 90
midi_instance = create_midi_file(num_tracks=3, file_format=1)
track1 = Track.create_track(midi_instance=midi_instance, track=0, channel=0, tempo=tempo)
track2 = Track.create_track(midi_instance=midi_instance, track=1, channel=0, tempo=tempo)
track3 = Track.create_track(midi_instance=midi_instance, track=2, channel=0, tempo=tempo)

note_result = read_note_from_sound_file(filename)
# this decides which phrase should have more tracks (instrument)
pitch_result = read_pitch_from_sound_file(filename)
emphasis_proportion_list = pitch_result['emphasis_proportion_list']
density_level_list = pitch_result['density_level_list']

melody = Melody(note_result).build()
# divide melody bars with a group of 4, building phrases
bar_of_each_phrase = 4
chunks = [melody.bar_note_result_list[x:x + bar_of_each_phrase] for x in
          range(0, len(melody.bar_note_result_list), bar_of_each_phrase)]

sum_beats = len(melody.bar_note_result_list) * 4  # 4 beat each bar
begin_beat = 0
for chunk in chunks:
    phrase = Phrase2(bars_of_notes=chunk, start_time=begin_beat)
    bars_of_notes = phrase.standardize(std_octave=4).bars_of_notes
    chords = phrase.build_chords(std_octave=2)
    # add to track
    for one_bar in bars_of_notes:
        for note in one_bar:
            track1.add_note(note=note)
    for chord in chords:
        track2.add_chord(chord=chord)

    # decide if we want appregio or more ?
    begin_proportion_range = [(begin_beat + x) / sum_beats for x in range(0, 4)]
    addon = False
    # one beat proportion contains in emphasis_proportion could be considered as addon enabled
    for beat_proportion in begin_proportion_range:
        for emphasis_proportion in emphasis_proportion_list:
            if emphasis_proportion['start'] <= beat_proportion <= emphasis_proportion['end']:
                addon = True
                break
            if emphasis_proportion['start'] <= beat_proportion <= emphasis_proportion['end']:
                addon = True
                break
        if addon:
            break
    if addon:
        appregios = phrase.build_appregios(std_octave=3)
        for appregio in appregios:
            track3.add_appregio(appregio=appregio)

    begin_beat += 4 * bar_of_each_phrase

# phrase = Phrase2(melody.bar_note_result_list)
# bars_of_notes = phrase.standardize(std_octave=4).bars_of_notes
# chords = phrase.build_chords(std_octave=2)
# appregios = phrase.build_appregios(std_octave=3)
# midi_instance = create_midi_file(num_tracks=3, file_format=1)
# volume = 80

#
# for one_bar in bars_of_notes:
#     for note in one_bar:
#         track1.add_note(note=note)
# for chord in chords:
#     track2.add_chord(chord=chord)
# for appregio in appregios:
#     track3.add_appregio(appregio=appregio)
#
save_midi_file('test1.mid', midi_instance)
