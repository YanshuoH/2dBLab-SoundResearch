import sys
from subprocess import call

if len(sys.argv) < 2:
    print('Usage: %s <number>' % sys.argv[0])
    sys.exit(1)

exp_no = int(sys.argv[1])
if exp_no == 1:
    call(['python', 'phrase_test.py', 'demo/exp_1.mid'])
elif exp_no == 2:
    call(['python', 'arrangement_test.py', 'ensemble.m4a', 'demo/exp_2'])
elif exp_no == 3:
    call(['python', 'midi_heartbeat_test.py', 'pachelbel_canon.mid', '80', 'demo/exp_3.mp3'])
elif exp_no == 4:
    call(['python', 'arrangement_test.py', 'dataset/third_bank_of_the_river_b.m4a', 'demo/exp_4'])
else:
    print('Unknown experiment number')

