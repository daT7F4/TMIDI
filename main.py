print("Importing...")

print("Midi")
from mido import MidiFile
print("Numpy")
import numpy as np
print("OS, Time, random, Subprocess, OpenCV")
import os, time, random, subprocess, cv2
print("Alive progress")
from alive_progress import alive_bar
print("Fluidsynth")
from midi2audio import FluidSynth

try:
  os.remove("output.mp4")
except FileNotFoundError:
  print(" ")

try:
  os.remove("movie.mp4")
except FileNotFoundError:
  print(" ")

W = 1080
H = 1080

image = 0

st = time.time()
image_sequence = []

# 0 = Notes
# 1 = Time
# 2 = Duration
# 3 = Channel
# 4 = Velocity
channels = []
keys = [0, 3, 1, 3, 2, 0, 3, 1, 3, 1, 3, 2]

colors = [
  [255, 0, 0],
  [255, 153, 255],
  [255, 255, 0],
  [153, 255, 51],
  [102, 255, 153],
  [102, 255, 255],
  [51, 204, 255],
  [51, 153, 255],
  [0, 102, 255],
  [0, 0, 255],
  [102, 102, 255],
  [153, 102, 255],
  [107, 66, 234],
  [204, 51, 255],
  [255, 0, 255],
  [255, 204, 204]
]

tt = 0

# <----------> MAIN PARAMETERS <---------->
MIDI = input("Enter the MIDI file name with the extension: ")
SOUNDFONT = input("Enter the Soundfont file name with the extension: ")
framerate = 60
steps = 1/framerate  # the amount of time the notes move every frame
offset = 0  # start offset(in seconds
zoom = 3840  # how fast the notes will move(px/s)
# <----------> MAIN PARAMETERS <---------->

# 0 = Index
# 1 = Time
tNotes = [[[0] * 2 for _ in range(128)] for _ in range(16)]

def rectangle(tl, br, c):
  cv2.rectangle(image, tl, br, c, cv2.FILLED)

# 0 = Straight Right
# 1 = Straight Center
# 2 = Straight Left
# 3 Black

def renderKey(x, y, k, r, g, b):
  if k == 0:
    rectangle((x, y), (x + 8, y + 44), (b, r, g))
    rectangle((x + 8, y + 28), (x + 12, y + 44), (b, r, g))
    if [r, g, b] == [255, 255, 255]:
      rectangle((x, y + 36), (x + 12, y + 44), (b - 80, r - 80, g - 80))

  if k == 1:
    rectangle((x, y), (x + 8, y + 44), (b, r, g))
    rectangle((x - 4, y + 28), (x, y + 44), (b, r, g))
    rectangle((x + 8, y + 28), (x + 12, y + 44), (b, r, g))
    if [r, g, b] == [255, 255, 255]:
      rectangle((x - 4, y + 36), (x + 12, y + 44), (b - 80, r - 80, g - 80))

  if k == 2:
    rectangle((x, y), (x + 8, y + 44), (b, r, g))
    rectangle((x - 4, y + 28), (x, y + 44), (b, r, g))
    if [r, g, b] == [255, 255, 255]:
      rectangle((x - 4, y + 36), (x + 8, y + 44), (b - 80, r - 80, g - 80))

  if k == 3:
    rectangle((x, y), (x + 8, y + 28), (b, r, g))


def renderPart(x, y, p):
  if p == 0:
    renderKey(x, y, 0, 255, 255, 255)
    renderKey(x + 16, y, 1, 255, 255, 255)
    renderKey(x + 32, y, 2, 255, 255, 255)

  if p == 1:
    renderKey(x, y, 0, 255, 255, 255)
    renderKey(x + 16, y, 1, 255, 255, 255)
    renderKey(x + 32, y, 1, 255, 255, 255)
    renderKey(x + 48, y, 2, 255, 255, 255)


def renderKeyboard(x, y):
  i = 0
  for i in range(10):
    renderPart(x + i * 96, y, 0)
    renderPart(x + ((i * 96) + 40), y, 1)
  i += 1
  renderPart(x + i * 96, y, 0)
  renderKey((x + 40) + (i * 96), y, 0, 255, 255, 255)
  renderKey((x + 40) + (i * 96), y, 2, 255, 255, 255)

print("Parsing MIDI")
i = 0
last_ts = time.time()
mid = MidiFile(MIDI)
mi = 0
for msg in mid:
  tt += msg.time
  if msg.type == 'note_on' or msg.type == 'note_off':
    c = msg.channel
    if msg.type == 'note_on':
      if msg.velocity == 0:
        channels[tNotes[c][msg.note][0]][2] = tt - tNotes[c][msg.note][1]
      else:
        tNotes[c][msg.note][0] = i
        tNotes[c][msg.note][1] = tt
        channels.append([msg.note, tt, 0, c, msg.velocity])
        i += 1
    if msg.type == 'note_off':
      channels[tNotes[c][msg.note][0]][2] = tt - tNotes[c][msg.note][1]
mi = i


def drawPixel(y, x, r, g, b):
  if y > H - 4:
    return
  if y < 0:
    return
  for i in range(16):
    image[x + i%4, y + int(i/4)] = [b, r, g]

def drawParticle(x, y, r, g, b):
  for i in range(9):
    r = random.randint(0, 1)
    drawPixel(x + (i % 3) + random.randint(0, 8), y + int(i / 3) - random.randint(4, 80), (r + 20) * r, (g + 20) * r, (b + 20) * r)


def drawLine(x1, y1, y2, r, g, b):
  tl = (int(x1+4), int(y1-y2))
  br = (int(x1+4), int(y1))
  rc = [b, r, g]
  cv2.line(image, tl, br, rc, 8)

print("Took " + str(time.time() - last_ts) + " seconds!")
print("Generating Frames")

fr = 0
ti = 0
last_t = time.time()
frame_files = []
s = True
video_writer = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*'mp4v'), framerate, (W, H))
with alive_bar(int((channels[mi - 1][1] + channels[mi - 1][2]) / steps) + 2) as bar:
  while s:
    try:
      while H - ((channels[ti][1] + channels[ti][2] - offset) * zoom) > H:
        if ti == mi:
          break
        ti += 1
    except IndexError:
      ti = mi
      s = False
    i = ti
    image = np.zeros((H, W, 3), dtype=np.uint8)
    render = [-1] * 128
    while True:
      try:
        x = channels[i][0]
      except IndexError:
        break
      y = channels[i][1]
      d = channels[i][2]
      c = channels[i][3]
      v = channels[i][4]
      if ((channels[mi - 1][1] + channels[mi - 1][2] - offset) * zoom) < 0 and i == mi - 1:
        s = False
        break
      if H - ((y - offset) * zoom) < 0:
        break
      drawLine(x * 8, H - ((y - offset) * zoom), d * zoom, colors[c][0], colors[c][1], colors[c][2])
      if H - ((y - offset) * zoom) > H - 44 and H -((y + d - offset) * zoom) < H:
        render[x] = c

      i += 1
    offset += steps
    renderKeyboard(0, H - 44)
    for j in range(128):
      if render[j] > -1:
        renderKey(j * 8, H - 44, keys[j % 12], colors[render[j]][0], colors[render[j]][1], colors[render[j]][2])
        #drawParticle(j * 8, H - 44, colors[render[j]][0], colors[render[j]][1], colors[render[j]][2])
    video_writer.write(image)
    fr += 1
    bar()


print("Frames rendered! Took " + str(time.time() - last_t) + " seconds!")

FluidSynth(SOUNDFONT).midi_to_audio(MIDI, 'output.wav')

print("Merging video")

video_writer.release()

subprocess.run(
    "ffmpeg -y -i output.mp4 -i output.wav -c:v copy -c:a aac -strict experimental movie.mp4",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=False)

print("")
print("Everything took " + str(time.time() - st) + " seconds")