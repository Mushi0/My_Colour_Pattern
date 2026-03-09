import tkinter as tk
import math
import colorsys

SIZE = 420
CENTER = SIZE // 2
RADIUS = 180
STEPS = 360

ONE_HOLE_SIZE = 20
ONE_LAYER_SIZE = 20
HALF_LAYER_SIZE = ONE_LAYER_SIZE // 2
LINE_SIZE = 3
CONT_COLOUR_LEN = 7

RADIUS_LAYER_3 = RADIUS - ONE_LAYER_SIZE * 2
RADIUS_LAYER_2 = RADIUS_LAYER_3 - ONE_LAYER_SIZE * 2
RADIUS_LAYER_1 = RADIUS_LAYER_2 - ONE_LAYER_SIZE * 2

TRIADIC_COLOUR_ANGLE = 120
COMPLEMENTARY_COLOUR_ANGLE = 180

COLOUR_WHEEL_COORDS = (CENTER - RADIUS - ONE_LAYER_SIZE, 
                       CENTER + RADIUS + ONE_LAYER_SIZE)

class MyColourPattern:
    def __init__(self, root):
        self.root = root
        self.root.title("Colour Pattern")
        self.canvas = tk.Canvas(self.root, width = SIZE, height = SIZE, bg = "white")
        self.canvas.pack()

        # Bind mouse events for dragging
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

        # Add a button to toggle between RGB and RYB colour wheels
        self.toggle_button = tk.Button(self.root, 
                                       text = "RGB/RYB", 
                                       command = self.toggle_colour_mode)
        self.toggle_button.pack()

        # initial state
        self.current_angle = 0
        self.prev_x = None
        self.prev_y = None
        self.rgb_or_ryb = "ryb"

        self.update_start_angle()

        self.root.mainloop()
    
    # ------------- Draw colour wheel --------------
    
    def _cubic(self, t, a, b):
        weight = t * t * (3 - 2*t)
        return a + weight * (b - a)
    
    def ryb_to_rgb(self, r, y, b):
        # red
        x0, x1 = self._cubic(b, 1.0, 0.163), self._cubic(b, 1.0, 0.0)
        x2, x3 = self._cubic(b, 1.0, 0.5), self._cubic(b, 1.0, 0.2)
        y0, y1 = self._cubic(y, x0, x1), self._cubic(y, x2, x3)
        red = self._cubic(r, y0, y1)

        # green
        x0, x1 = self._cubic(b, 1.0, 0.373), self._cubic(b, 1.0, 0.66)
        x2, x3 = self._cubic(b, 0., 0.), self._cubic(b, 0.5, 0.094)
        y0, y1 = self._cubic(y, x0, x1), self._cubic(y, x2, x3)
        green = self._cubic(r, y0, y1)

        # blue
        x0, x1 = self._cubic(b, 1.0, 0.6), self._cubic(b, 0.0, 0.2)
        x2, x3 = self._cubic(b, 0.0, 0.5), self._cubic(b, 0.0, 0.0)
        y0, y1 = self._cubic(y, x0, x1), self._cubic(y, x2, x3)
        blue = self._cubic(r, y0, y1)

        return "#%02x%02x%02x" % (int(red*255), int(green*255), int(blue*255))

    def draw_colour_wheel_ryb(self):
        for i in range(STEPS):
            r, y, b = colorsys.hsv_to_rgb(i/360, 1, 1)
            colour = self.ryb_to_rgb(r, y, b)
            
            self.canvas.create_arc(COLOUR_WHEEL_COORDS[0], COLOUR_WHEEL_COORDS[0], 
                                   COLOUR_WHEEL_COORDS[1], COLOUR_WHEEL_COORDS[1], 
                                   start = i, extent = 1, 
                                   fill = colour, outline = colour)
    
    def draw_colour_wheel_rgb(self):
        for i in range(STEPS):
            r, g, b = colorsys.hsv_to_rgb(i/360, 1, 1)
            colour = "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))

            self.canvas.create_arc(COLOUR_WHEEL_COORDS[0], COLOUR_WHEEL_COORDS[0], 
                                   COLOUR_WHEEL_COORDS[1], COLOUR_WHEEL_COORDS[1], 
                                   start = i, extent = 1, 
                                   fill = colour, outline = colour)
    
    # ------------- Draw mask layers --------------

    def draw_mask_layer_0(self):
        '''
        central mask
        '''
        xy1 = CENTER - RADIUS_LAYER_1
        xy2 = CENTER + RADIUS_LAYER_1
        self.canvas.create_oval(xy1, xy1, xy2, xy2, 
                                fill = "black", outline = "black")

        self.canvas.create_oval(xy1, xy1, xy2, xy2, 
                                outline = "gray", width = LINE_SIZE)

    def draw_mask_layer_1(self, start_angle):
        '''
        continuous colours
        '''
        xy1 = CENTER - RADIUS_LAYER_1 - HALF_LAYER_SIZE
        xy2 = CENTER + RADIUS_LAYER_1 + HALF_LAYER_SIZE
        self.canvas.create_arc(xy1, xy1, xy2, xy2, 
                               start = (start_angle) % 360, 
                               extent = 360 - ONE_HOLE_SIZE * CONT_COLOUR_LEN, 
                               style=tk.ARC, 
                               outline = "black", 
                               width = ONE_LAYER_SIZE)

        xy1 = CENTER - RADIUS_LAYER_2 + HALF_LAYER_SIZE
        xy2 = CENTER + RADIUS_LAYER_2 - HALF_LAYER_SIZE
        self.canvas.create_oval(xy1, xy1, xy2, xy2,
                                outline = "black", width = ONE_LAYER_SIZE)
        
        xy1 = CENTER - RADIUS_LAYER_2
        xy2 = CENTER + RADIUS_LAYER_2
        self.canvas.create_oval(xy1, xy1, xy2, xy2, 
                                outline = "gray", width = LINE_SIZE)

    def draw_mask_layer_2(self, start_angle):
        '''
        complementary colours
        '''
        for i in range(2):
            angle = (start_angle + i * COMPLEMENTARY_COLOUR_ANGLE) % 360

            xy1 = CENTER - RADIUS_LAYER_2 - HALF_LAYER_SIZE
            xy2 = CENTER + RADIUS_LAYER_2 + HALF_LAYER_SIZE
            self.canvas.create_arc(xy1, xy1, xy2, xy2, 
                                   start = angle, 
                                   extent = COMPLEMENTARY_COLOUR_ANGLE - ONE_HOLE_SIZE, 
                                   style=tk.ARC, 
                                   outline = "black", 
                                   width = ONE_LAYER_SIZE)
        
        xy1 = CENTER - RADIUS_LAYER_3 + HALF_LAYER_SIZE
        xy2 = CENTER + RADIUS_LAYER_3 - HALF_LAYER_SIZE
        self.canvas.create_oval(xy1, xy1, xy2, xy2,
                                outline = "black", width = ONE_LAYER_SIZE)
        
        xy1 = CENTER - RADIUS_LAYER_3
        xy2 = CENTER + RADIUS_LAYER_3
        self.canvas.create_oval(xy1, xy1, xy2, xy2, 
                                outline = "gray", width = LINE_SIZE)
    
    def draw_mask_layer_3(self, start_angle):
        '''
        triadic colours
        '''
        for i in range(3):
            angle = (start_angle + i * TRIADIC_COLOUR_ANGLE) % 360 

            xy1 = CENTER - RADIUS_LAYER_3 - HALF_LAYER_SIZE
            xy2 = CENTER + RADIUS_LAYER_3 + HALF_LAYER_SIZE
            self.canvas.create_arc(xy1, xy1, xy2, xy2,
                                   start = angle, 
                                   extent = TRIADIC_COLOUR_ANGLE - ONE_HOLE_SIZE, 
                                   style=tk.ARC, 
                                   outline = "black", 
                                   width = ONE_LAYER_SIZE)
        
        xy1 = CENTER - RADIUS + HALF_LAYER_SIZE
        xy2 = CENTER + RADIUS - HALF_LAYER_SIZE
        self.canvas.create_oval(xy1, xy1, xy2, xy2,
                                outline = "black", width = ONE_LAYER_SIZE)
    
    # ------------- Event handlers --------------

    def on_drag(self, event):
        if self.prev_x is not None and self.prev_y is not None:
            prev_angle = math.atan2(self.prev_y - CENTER, self.prev_x - CENTER)
            curr_angle = math.atan2(event.y - CENTER, event.x - CENTER)
            angle_diff = math.degrees(prev_angle - curr_angle)
            self.current_angle = (self.current_angle + angle_diff) % 360
            
            self.update_start_angle()
            
        self.prev_x = event.x
        self.prev_y = event.y

    def on_release(self, event):
        self.prev_x = None
        self.prev_y = None
    
    def toggle_colour_mode(self):
        self.rgb_or_ryb = "rgb" if self.rgb_or_ryb == "ryb" else "ryb"
        self.update_start_angle()

    def update_start_angle(self):
        self.canvas.delete("all")
        if self.rgb_or_ryb == "ryb":
            self.draw_colour_wheel_ryb()
        else:
            self.draw_colour_wheel_rgb()
        self.draw_mask_layer_0()
        self.draw_mask_layer_1(self.current_angle)
        self.draw_mask_layer_2(self.current_angle)
        self.draw_mask_layer_3(self.current_angle)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyColourPattern(root)
    root.mainloop()