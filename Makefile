run:
	uv run main.py

debug:
	uv run python3 -i main.py

sputtering_dummy.raw:
	uv run main.py -w

sputtering_dummy.wav: sputtering_dummy.raw
	sox  -r 48k -e signed -b 16 -L -c 1 sputtering_dummy.raw sputtering_dummy.wav

wav: sputtering_dummy.wav

clean:
	rm -f sputtering_dummy.wav sputtering_dummy.raw
