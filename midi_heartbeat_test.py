import sys

from mido import MidiFile

from utils.utils import get_heart_beat_track_and_save

if len(sys.argv) < 4:
    print('Usage: %s <filename> <bpm> <destination>' % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
bpm = int(sys.argv[2])
destination = sys.argv[3]
mid = MidiFile(filename)

bar_count = int((mid.length / 60) * bpm / 4) + 1

FILLING_BARS = 2
print('====> mid length in seconds = %d, bar_count = %d, bpm = %d' % (mid.length, bar_count, bpm))
get_heart_beat_track_and_save(filename='heartbeat-01a.mp3', dest_filename=destination,
                              bar_count=bar_count + FILLING_BARS * 2, bpm=bpm)
print('====> saved file %s' % destination)

