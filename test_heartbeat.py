from pydub import AudioSegment

heart_beat_track = AudioSegment.from_file('/Users/hys/Downloads/heartbeat-01a.mp3', format='mp3')
part = heart_beat_track[80:150]
AudioSegment.export(part, 'single_heartbeat.mp3')

