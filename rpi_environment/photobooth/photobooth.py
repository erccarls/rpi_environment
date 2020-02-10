import pygame
import pygame.camera
from pygame.locals import *

pygame.init()
pygame.camera.init()


class Capture:

    def __init__(self):
        self.size = (640, 480)
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

    def draw(self):
        # if you don't want to tie the framerate to the camera, you can check
        # if the camera has an image ready.  note that while this works
        # on most cameras, some will never return true.
        if self.cam.query_image():
            self.snapshot = self.cam.get_image(self.snapshot)

        # blit it to the display surface.  simple!
        self.display.blit(self.snapshot, (0,0))
        
        # Render Text
        white = (255, 255, 255) 
        green = (0, 255, 0) 
        blue = (0, 0, 128)
        font = pygame.font.Font('freesansbold.ttf', 32) 
        text = font.render(self.text, True, green, blue) 
        textRect = text.get_rect()
        textRect.center = (640 // 2, int(480 * .90)) 
        self.display.blit(text, textRect)
        
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
                    self.text = 'spacebar pressed'
            
            
cap = Capture()
cap.main()
