from os import listdir
from os.path import isfile, join
from subprocess import call

SOUND_PATH = './dataset'
files = [f for f in listdir(SOUND_PATH) if isfile(join(SOUND_PATH, f))]
for f in files:
    if f.endswith('.m4a') is False:
        continue

    # $ python arrangement_test.py ./dataset/serpent.m4a ./dataset/result/serpent_
    call(['python', 'arrangement_test.py', './dataset/%s' % f, './dataset/result/%s' % f.replace('.m4a', '')])
