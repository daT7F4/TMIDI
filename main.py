print("Importing...")

from mido import MidiFile
import os, time, random, subprocess, shutil, threading
import cv2
from midi2audio import FluidSynth
from alive_progress import alive_bar
import numpy as np

try:
  os.remove("output.mp4")
except FileNotFoundError:
  pass

try:
  os.remove("movie.mp4")
except FileNotFoundError:
  pass

try:
  shutil.rmtree("images")
except FileNotFoundError:
  pass

os.mkdir("images")

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
THREADS = 4
framerate = 60
steps = 1/framerate  # the amount of time the notes move every frame(don't change)
offset = 0  # start offset in seconds(don't change)
zoom = 3840  # how fast the notes will move(px/s)
# <----------> MAIN PARAMETERS <---------->

# 0 = Index
# 1 = Time
tNotes = [[[0, 0] for _ in range(128)] for _ in range(16)]

def rectangle(tl, br, c, image):
  cv2.rectangle(image, tl, br, c, cv2.FILLED)

# 0 = Straight Right
# 1 = Straight Center
# 2 = Straight Left
# 3 Black

def renderKey(x, y, k, r, g, b, image):
  if k == 0:
    rectangle((x, y), (x + 8, y + 44), (b, r, g), image)
    rectangle((x + 8, y + 28), (x + 12, y + 44), (b, r, g), image)
    if [r, g, b] == [255, 255, 255]:
      rectangle((x, y + 36), (x + 12, y + 44), (b - 80, r - 80, g - 80), image)

  if k == 1:
    rectangle((x, y), (x + 8, y + 44), (b, r, g), image)
    rectangle((x - 4, y + 28), (x, y + 44), (b, r, g), image)
    rectangle((x + 8, y + 28), (x + 12, y + 44), (b, r, g), image)
    if [r, g, b] == [255, 255, 255]:
      rectangle((x - 4, y + 36), (x + 12, y + 44), (b - 80, r - 80, g - 80), image)

  if k == 2:
    rectangle((x, y), (x + 8, y + 44), (b, r, g), image)
    rectangle((x - 4, y + 28), (x, y + 44), (b, r, g), image)
    if [r, g, b] == [255, 255, 255]:
      rectangle((x - 4, y + 36), (x + 8, y + 44), (b - 80, r - 80, g - 80), image)

  if k == 3:
    rectangle((x, y), (x + 8, y + 28), (b, r, g), image)


def renderPart(x, y, p, image):
  if p == 0:
    renderKey(x, y, 0, 255, 255, 255, image)
    renderKey(x + 16, y, 1, 255, 255, 255, image)
    renderKey(x + 32, y, 2, 255, 255, 255, image)

  if p == 1:
    renderKey(x, y, 0, 255, 255, 255, image)
    renderKey(x + 16, y, 1, 255, 255, 255, image)
    renderKey(x + 32, y, 1, 255, 255, 255, image)
    renderKey(x + 48, y, 2, 255, 255, 255, image)


def renderKeyboard(x, y, image):
  i = 0
  for i in range(10):
    renderPart(x + i * 96, y, 0, image)
    renderPart(x + ((i * 96) + 40), y, 1, image)
  i += 1
  renderPart(x + i * 96, y, 0, image)
  renderKey((x + 40) + (i * 96), y, 0, 255, 255, 255, image)
  renderKey((x + 40) + (i * 96), y, 2, 255, 255, 255, image)

print("Parsing MIDI")
i = 0
last_ts = time.time()
mid = MidiFile(MIDI, clip=True)
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
      try:
        channels[tNotes[c][msg.note][0]][2] = tt - tNotes[c][msg.note][1]
      except IndexError:
        raise Exception('MIDI started using a note_off event or a 0 velocity note')
mt = tt
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


def drawLine(x1, y1, y2, r, g, b, image):
  tl = (int(x1+4), int(y1-y2))
  br = (int(x1+4), int(y1))
  rc = [b, r, g]
  cv2.line(image, tl, br, rc, 8)

print("Took " + str(time.time() - last_ts) + " seconds!")
print("Rendering Frames")
last_t = time.time()
frame_files = []

def threadRender(start):
  s = True
  fr = start
  offset = steps * fr
  last_t = time.time()
  ti = 0
  while s:
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
      if H - ((channels[ti][1] + channels[ti][2] - offset) * zoom) > H:
        ti += 1
      if H - ((y - offset) * zoom) < 0:
        break
      if H - ((y + d - offset) * zoom) < H:
        drawLine(x * 8, H - ((y - offset) * zoom), d * zoom, colors[c][0], colors[c][1], colors[c][2], image)
      if H - ((y - offset) * zoom) > H - 44 and H -((y + d - offset) * zoom) < H:
        render[x] = c
      li = i
      while H - ((channels[i][1] + channels[i][2] - offset) * zoom) > H:
        i += 1
        try:
          channels[i][1]
        except IndexError:
          i -= 1
          break
      if li == i:
        i += 1

    offset += steps * THREADS
    renderKeyboard(0, H - 44, image)
    for j in range(128):
      if render[j] > -1:
        renderKey(j * 8, H - 44, keys[j % 12], colors[render[j]][0], colors[render[j]][1], colors[render[j]][2], image)
    if "./images/img" + str(fr).zfill(5) + ".png" not in frame_files:
      cv2.imwrite("./images/img" + str(fr).zfill(5) + ".png", image)
      frame_files.append("img" + str(fr).zfill(5) + ".png")
    fr += THREADS
    bar()

threads = []
with alive_bar(int(mt / steps) - 101) as bar:
  for i in range(THREADS):
    threads.append(threading.Thread(target=threadRender, args=(i,)))
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()

print("Frames rendered! Took " + str(time.time() - last_t) + " seconds!")

FluidSynth(SOUNDFONT).midi_to_audio(MIDI, 'output.wav')
channels = 0

print("Writing Video")

subprocess.run(
    'ffmpeg -r ' + str(framerate) + ' -i images/img%05d.png output.mp4',
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=False)

subprocess.run(
    "ffmpeg -y -i output.mp4 -i output.wav -c:v copy -c:a aac -strict experimental movie.mp4",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=False)

print("")
print("Everything took " + str(time.time() - st) + " seconds")
