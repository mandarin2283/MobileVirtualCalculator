# main.py

import cv2
import numpy as np
import mediapipe as mp
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
import HandTrackingClass as htm


class Button:
    def init(self, position, width, height, value):
        self.position = position
        self.width = width
        self.height = height
        self.value = value

    def draw(self, image):
        cv2.rectangle(image, self.position,
                      (self.position[0]+self.width, self.position[1]+self.height),
                      (255, 255, 255), -1)
        cv2.rectangle(image, self.position,
                      (self.position[0]+self.width, self.position[1]+self.height),
                      (50, 50, 50), 3)
        cv2.putText(image, self.value, (self.position[0] + 30, self.position[1] + 70),
                    cv2.FONT_HERSHEY_PLAIN, 4, (50, 50, 50), 4)

    def click(self, x, y):
        return (self.position[0] < x < self.position[0] + self.width and
                self.position[1] < y < self.position[1] + self.height)


class HandCalcApp(App):
    def build(self):
        self.img_widget = Image()
        layout = BoxLayout()
        layout.add_widget(self.img_widget)

        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 1280)
        self.capture.set(4, 720)

        self.detector = htm.HandDetector()

        self.button_values = [['7','8','9','*'],
                              ['4','5','6','-'],
                              ['1','2','3','+'],
                              ['0','/','.','=']]
        self.button_list = []
        for x in range(4):
            for y in range(4):
                xpos = x * 100 + 600
                ypos = y * 100 + 100
                self.button_list.append(Button((xpos, ypos), 100, 100,
                                               self.button_values[y][x]))

        self.my_equation = ''
        self.counter = 0

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        return layout

    def update(self, dt):
        ret, img = self.capture.read()
        if not ret:
            return

        img = cv2.flip(img, 1)
        img = self.detector.find_hands(img)

        cv2.rectangle(img, (600, 50), (1000, 170), (255, 255, 255), -1)
        cv2.rectangle(img, (600, 50), (1000, 170), (50, 50, 50), 3)
        for button in self.button_list:
            button.draw(img)

        lm_list = self.detector.find_pos(img)
        if lm_list:
            length = self.detector.find_distance(lm_list[8][1:], lm_list[12][1:])
            x, y = lm_list[8][1:]

            if length < 50:
                for button in self.button_list:
                    if button.click(x, y) and self.counter == 0:
                        my_value = button.value
                        if my_value == '=':
                            try:
                                self.my_equation = str(eval(self.my_equation))
                            except:
                                self.my_equation = "Error"
                        else:
                            self.my_equation += my_value
                        self.counter = 1

        if self.counter != 0:
            self.counter += 1
            if self.counter > 10:
                self.counter = 0

        cv2.putText(img, self.my_equation, (610, 90),
                    cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)

        # Show image on Kivy widget
        buf = cv2.flip(img, 0).tobytes()
        img_texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img_widget.texture = img_texture

    def on_stop(self):
        self.capture.release()