import sys
from subprocess import call

if len(sys.argv) < 2:
    print('Usage: %s <number> <argument>' % sys.argv[0])
    sys.exit(1)

exp_no = int(sys.argv[1])
if exp_no == 1:
    if len(sys.argv) < 3:
        print('test suite argument is required')
        sys.exit(1)
    arg = sys.argv[2]
    call(['python', 'phrase_test.py', 'demo/exp_1.mid', arg])
elif exp_no == 2:
    if len(sys.argv) < 3:
        print('test suite argument is required')
        sys.exit(1)
    arg = sys.argv[2]
    voice_track = None
    if arg == '1':
        voice_track = 'dataset/lanqiaoyi_a.m4a'
    else:
        voice_track = 'dataset/lanqiaoyi_wangdongqiang.m4a'
    call(['python', 'arrangement_test.py', voice_track, 'demo/exp_2'])
elif exp_no == 3:
    if len(sys.argv) < 3:
        print('bpm argument is required')
        sys.exit(1)
    bpm = sys.argv[2]
    call(['python', 'midi_heartbeat_test.py', 'pachelbel_canon.mid', bpm, 'demo/exp_3.mp3'])
elif exp_no == 4:
    call(['python', 'arrangement_test.py', 'dataset/third_bank_of_the_river_b.m4a', 'demo/exp_4'])
else:
    print('Unknown experiment number')

