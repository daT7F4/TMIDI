# TMIDI
MIDI renderer written in Python

First, you need the main.py file, a .sf2(soundfont) file and a MIDI file to render

Second, you need to install some dependencies using pip
 : mido
 : numpy
 : subprocess
 : cv2
 : alive_progress
 : midi2audio

You will also need to install FluidSynth and ffmpeg
Linux: "sudo apt install fluidsynth" and "sudo apt install ffmpeg"
Mac: "brew install fluidsynth" and "brew install ffmpeg" (if you're using homebrew)
Windows: (There is no command, there are installers)

Lastly, run it with "python3 main.py"
You will now be prompted to type in the MIDI name with the extension: "example.mid"
Hit enter
Same with the soundfont file, type also the extension: "example.sf2" or "example.sf3"
Hit enter

Then you just wait until it finishes
The video without the sound is called "output.mp4"
The video with the sound is called "movie.mp4"

Hope you enjoy :)



If you encounter some error that you don't know how to fix, open an issue and i will try to help


