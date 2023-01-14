from pygame import mixer  # Load the popular external library

mixer.init()
mixer.music.load('ryszard.mp3')
mixer.music.play(-1)