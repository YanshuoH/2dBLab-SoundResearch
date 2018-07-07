from copy import copy

from model.note import volume_map, Note, drum_map


class DrumBar:
    def __init__(self, start_time: int, std_volume: int = volume_map['mf'], bar_count: int = 4):
        self.start_time = start_time
        self.std_volume = std_volume
        self.bar_count = bar_count

    def __build_single_bar_style1(self, start_time: int):
        time = copy(start_time)
        note1_bass_drum = Note(pitch=drum_map['BassDrum'], volume=self.std_volume, duration=1, time=time)
        note1_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        time += 1
        note2_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        time += 1
        note3_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        note3_snare_drum = Note(pitch=drum_map['SnareDrum'], volume=self.std_volume, duration=1, time=time)
        time += 1
        note4_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        return [note1_bass_drum, note1_hat_closed, note2_hat_closed, note3_hat_closed, note3_snare_drum,
                note4_hat_closed]

    def __build_double_bar_style1(self, start_time: int):
        time = copy(start_time)
        bar1 = self.__build_single_bar_style1(start_time=time)
        time += 4
        note1_bass_drum = Note(pitch=drum_map['BassDrum'], volume=self.std_volume, duration=1, time=time)
        note1_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        time += 1
        note2_bass_drum = Note(pitch=drum_map['BassDrum'], volume=self.std_volume, duration=1, time=time)
        note2_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        time += 1
        note3_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        note3_snare_drum = Note(pitch=drum_map['SnareDrum'], volume=self.std_volume, duration=1, time=time)
        time += 1
        note4_hat_closed = Note(pitch=drum_map['HiHatClosed'], volume=self.std_volume, duration=1, time=time)
        bar2 = [note1_bass_drum, note1_hat_closed, note2_bass_drum, note2_hat_closed, note3_hat_closed,
                note3_snare_drum, note4_hat_closed]
        return [bar1, bar2]

    def build_style1(self):
        bar_notes = []
        start_time = copy(self.start_time)
        if self.bar_count == 1:
            bar_notes.append(self.__build_single_bar_style1(start_time))
        elif self.bar_count % 2 == 0:
            # has something in the end
            for i in range(0, self.bar_count, 2):
                bar_notes.extend(self.__build_double_bar_style1(start_time))
                start_time += 2 * 4
        else:
            # remove the last one and add it in the end
            for i in range(0, self.bar_count - 1, 2):
                bar_notes.extend(self.__build_double_bar_style1(start_time))
                start_time += 2 * 4
            bar_notes.append(self.__build_single_bar_style1(start_time))

        return bar_notes
