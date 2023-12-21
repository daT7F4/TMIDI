# TMIDI
MIDI renderer written in Python

### Setup

First, you need the main.py file, the videos.txt file, a .sf2(soundfont) file and a MIDI file to render

Second, you need to install some dependencies using pip
* mido
* numpy
* subprocess
* cv2
* alive_progress
* midi2audio

You can also run `pip install -r requirements.txt`

You will also need to install FluidSynth and ffmpeg but you can't install them just using pip
## Linux:
```
sudo apt upgrade fluidsynth ffmpeg -y
```

## Mac:
(If you are using homebrew)
```
brew install fluidsynth ffmpeg
```
## Windows: 
[FFMPEG](https://www.ffmpeg.org/download.html#build-windows)
[FluidSynth](https://github.com/FluidSynth/fluidsynth/releases)

### Running

Run it by using ``` python3 main.py ```

You will be prompted to input the name ***and*** the extension of the MIDI file, for example ```example.mid```. After that you will be prompted to input the name ***and*** the extension of the SoundFont file, for example ```example.sf2```. Then it will render the MIDI file. The time depends on the size of the MIDI file and the processing power of your CPU

The 2 output files are named ```output.mp4```(Only video) ```movie.mp4```(Video and Audio)

If you have some problems or opinions, feel free to open an issue
