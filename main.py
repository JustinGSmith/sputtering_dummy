import sys
import pyaudio
import random

runtime = 300
chunk = 1024
data_width=2
sample_rate = 48000

out_buff = bytearray(chunk)
proc_buff_size = sample_rate * 10
proc_buff = bytearray(proc_buff_size)


class Cursor():
    def __init__(self, max_pos):
        self.max = max_pos
        self.reset()


    def reset(self):
        self.pos = 0
        self.dur = 0


    def step(self):
        self.pos = (self.pos + 1) % self.max
        self.dur = self.dur - 1


# NOTE: val is one byte, but the size of a sample is declared in
# the format argument of p.open below. eg. for CD audio it would be two
# bytes. at some point if this project becomes more complex, we should deal
# with bytes not mapping 1:1 with output values
#
# for now, this means that every random output is a composite mixing 1 to N
# bytes into N bytes of a frame value
def insert_noise(position, duration, rate, store):
    val = 0
    val_update = 0

    for _ in range(0, duration):

        if (val_update <= 0):
            val_update = rate
            val = random.randint(0, 255)

        val_update = val_update - 1
        position = (position + 1) % len(store)
        store[position] = val


def duplicate_noise(in_pos, out_pos, dur, store):
    i = in_pos
    j = out_pos

    for _ in range(0, dur):

        store[j] = store[i]
        j = (j + 1) % len(store)
        i = (i + 1) % len(store)


def mangle(cursor, store, output):
    store_max = len(store)-1
    max_adulteration = int(store_max / 10)

    def rand_pos():
        return random.randint(0, store_max)

    for i in range(0, len(output)):

        if (cursor.dur == 0):
            cursor.pos = rand_pos()
            cursor.dur = rand_pos()
            adulterate_point = rand_pos()
            adulterate_len = random.randint(0, max_adulteration)
            if random.randint(0,100) > 75:

                rate = random.randint(0, 1000)
                insert_noise(adulterate_point, adulterate_len, rate, store)

            else:

                read_point = rand_pos()
                duplicate_noise(read_point, adulterate_point, adulterate_len,
                                store)

        output[i] = store[cursor.pos]
        cursor.step()


def main(to_disk=False):
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(data_width),
                    channels=1,
                    rate=sample_rate,
                    input=False,
                    output=True,
                    frames_per_buffer=chunk)

    sinks = [stream]

    if to_disk:
        sinks.append(open('sputtering_dummy.raw', 'wb'))


    cursor = Cursor(len(proc_buff))

    for _ in range (0, int(sample_rate / chunk * runtime)):

        mangle(cursor, proc_buff, out_buff)
        b = bytes(out_buff)
        for sink in sinks:
            sink.write(b)

    for sink in sinks:
        sink.close()


if __name__ == "__main__":
    if "-w" in sys.argv:
        main(to_disk=True)
    else:
        main(to_disk=False)
