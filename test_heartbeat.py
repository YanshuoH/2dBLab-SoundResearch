from pydub import AudioSegment

heart_beat_track = AudioSegment.from_file('/Users/hys/Downloads/heartbeat-01a.mp3', format='mp3')
heart_beat_1 = heart_beat_track[70:180]
heart_beat_2 = heart_beat_track[380:490]
# AudioSegment.export(part, 'single_heartbeat1.mp3')

bpm = 86
tick_per_sec = 60 * 1000 / bpm
# heart_beat_1 = AudioSegment.from_file('single_heartbeat1.mp3', format='mp3')
# heart_beat_2 = AudioSegment.from_file('single_heartbeat2.mp3', format='mp3')

# make a sequential beats by a quarter notes which means a tick contains 2 heat beats
# and this is only applied for a half bar.
# in conclusion, one bar has two sets of heart beats
result_track = AudioSegment.empty()

# first set
result_track += heart_beat_1
gap = tick_per_sec / 2 - len(result_track)
result_track += AudioSegment.silent(gap)
result_track += heart_beat_2
# fill the gap
gap = tick_per_sec * 2 - len(result_track)
result_track += AudioSegment.silent(gap)

# # second set
result_track += heart_beat_1
gap = tick_per_sec * 2.5 - len(result_track)
result_track += AudioSegment.silent(gap)
result_track += heart_beat_2
# # fill the end gap
gap = tick_per_sec * 4 - len(result_track)
result_track += AudioSegment.silent(gap)

AudioSegment.export(result_track, 'bar_heartbeat.mp3')
