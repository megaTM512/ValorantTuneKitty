import numpy
import numpy as np
from PIL import Image
from pygame import mixer
import dxcam
import time

WIDTH, HEIGHT = 312, 146
POSX, POSY = 805, 135
REGION = (POSX, POSY, POSX + WIDTH, POSY + HEIGHT)
MAX_ERROR = 0.0005
DEFAULT_DURATION = 6
DEFAULT_PAUSETIME = 30
FADEOUT_TIME = 500
TIME_BETWEEN_SNAPSHOTS = 0.1


class matchStateObject:
    lastCalled = 0
    playing = False

    def __init__(self, trigger_image, musicpath, duration=DEFAULT_DURATION, pause_time=DEFAULT_PAUSETIME):
        self.trigger_image = trigger_image
        self.music_file = musicpath
        self.pause_time = pause_time
        self.duration = duration


def main():
    camera = dxcam.create(output_color="GRAY")

    won_image = Image.open('img/won2.png').convert('L')
    won_data = np.asarray(won_image)
    won_image.close()

    lost_image = Image.open('img/lost2.png').convert('L')
    lost_data = np.asarray(lost_image)
    lost_image.close()

    buy_image = Image.open('img/buy2.png').convert('L')
    buy_data = np.asarray(buy_image)
    buy_image.close()

    mixer.init()

    events = []
    events.append(matchStateObject(won_data, "music/won.mp3", duration=4))
    events.append(matchStateObject(lost_data, "music/lost.mp3",duration=4))
    events.append(matchStateObject(buy_data, "music/buy.mp3", duration=30,pause_time=35))
    while True:
        frame = camera.grab(region=REGION)

        # None Exception Handling
        if frame is None:
            print("Is Nothing")
        else:
            newFrame = frame
            newFrame = numpy.reshape(newFrame, (HEIGHT, WIDTH))
            #Image.fromarray(newFrame).show()
            print(calculate_error(newFrame, events[0].trigger_image))
            print(calculate_error(newFrame, events[1].trigger_image))
            print(calculate_error(newFrame, events[2].trigger_image))
            print("---")
            checkForEvents(events, newFrame)

        checkForFadeOut(events)
        time.sleep(TIME_BETWEEN_SNAPSHOTS)


def checkForEvents(events, newFrame):
    for event in events:
        if calculate_error(newFrame, event.trigger_image) > 1 - MAX_ERROR:
            if time.time() - event.lastCalled > event.pause_time:
                print("Playing Music!")
                for e in events:
                    e.playing = False
                event.playing = True
                event.lastCalled = time.time()
                mixer.music.stop()
                mixer.music.load(event.music_file)
                mixer.music.play()
                break


def checkForFadeOut(events):
    for event in events:
        if event.playing and time.time() - event.lastCalled > event.duration:
            mixer.music.fadeout(FADEOUT_TIME)
            event.playing = False


def calculate_error(current_frame, compare_image):
    result = 0
    for x in range(0, WIDTH):
        for y in range(0, HEIGHT):
            if compare_image[y][x] != 0:
                result += abs((current_frame[y][x] / 255) - (compare_image[y][x] / 255))**2
    max_error = WIDTH * HEIGHT
    return 1 - (result / max_error)


if __name__ == "__main__":
    main()
