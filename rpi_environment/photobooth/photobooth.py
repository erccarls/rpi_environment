import os
import time
from dropbox import Dropbox
from datetime import datetime
import pygame
import pygame.camera
from pygame.locals import *

pygame.init()
pygame.camera.init()


class Capture:

    def __init__(self):
        self.size = (1280, 720)
        # create a display surface. standard pygame stuff
        self.display = pygame.display.set_mode(self.size, 0)


        # this is the same as what we saw before
        self.clist = pygame.camera.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        self.cam = pygame.camera.Camera(self.clist[0], self.size)
        self.cam.start()

        # create a surface to capture to.  for performance purposes
        # bit depth is the same as that of the display surface.
        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)
        
        self.text = 'Drop yer fone to take a sick insta!'
        self.state = "waiting"
        self.start_time = None

        self.dropbox = Dropbox(os.environ['DROPBOX_TOKEN'])


    def draw(self):
        # if you don't want to tie the framerate to the camera, you can check
        # if the camera has an image ready.  note that while this works
        # on most cameras, some will never return true.
        if self.cam.query_image() and self.state != "show_photo":
            self.snapshot = self.cam.get_image(self.snapshot)

        # blit it to the display surface.  simple!
        self.display.blit(self.snapshot, (0,0))
        
        # Render Text
        white = (255, 255, 255) 
        green = (0, 255, 0) 
        blue = (0, 0, 128)
        font = pygame.font.Font('freesansbold.ttf', 32)

        if self.state == "countdown" or self.state == "show_photo":
            timer = 3.99 - (time.time() - self.start_time)
            text = str(int(timer))
            if -1 < timer < 1:
                text = "Say cheese!"
            if timer < -1:
                self.state = "show_photo"
                text = "Photo uploading..."
            if timer < -4:
                self.state = "waiting"
                text = self.text
                filename = f"{datetime.utcnow().strftime('%y_%m_%d_%H_%M_%S')}.jpg"
                full_path = f"/home/pi/Dropbox/photobooth/{filename}"
                pygame.image.save(self.snapshot, full_path)
                with open(full_path, 'rb') as f:
                    self.dropbox.files_upload(f.read(), path=f'/photobooth_cmci_studio/{filename}')
        else: 
            text = self.text
        

        text_obj = font.render(text, True, green, blue) 
        textRect = text_obj.get_rect()
        textRect.center = (1280 // 2, int(720 * .90)) 
        self.display.blit(text_obj, textRect)
        
        pygame.display.flip()
        

    def main(self):
        going = True
        
        while going:
            events = pygame.event.get()        
            self.draw()

            for e in events:
                print(e)
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    # close the camera safely
                    self.cam.stop()
                    going = False
            
                if (e.type == KEYDOWN and e.key == K_SPACE):
                    self.trigger()


    def trigger(self, charger_on_list=None):
        print('Detected Charger On:', charger_on_list)
        self.state = "countdown"
        self.start_time = time.time()



if __name__ == "__main__":            
    cap = Capture()
    cap.main()
