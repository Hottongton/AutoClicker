import tkinter as tk
import pynput
import threading
import os


class AutoClicker(tk.Frame):
    def __init__(self, master=None):
        try:
            self.indicator_off = tk.PhotoImage(file='data\\Paused.png')
            self.indicator_on = tk.PhotoImage(file='data\\Running.png')
        except tk.TclError:
            self.indicator_off = None
            self.indicator_on = None

        self.apply = None
        self.close = None
        self.enabler = None
        self.speeder = None
        self.speeder_description = None
        self.speeder_unit = None
        self.toggle = None
        self.toggle_description = None
        self.toggle_state = None
        self.indicator = None
        self.listener_thread = None
        self.click_thread = None

        super().__init__()
        self.master = master
        self.pack()
        self.create_widgets()

        self.click_state = False
        self.start_keyboard_listener()

    def create_apply(self):
        def internal():
            global default_speed
            self.click_state = False
            try:
                default_speed = int(self.speeder.get())
                self.write_data()
            except (TypeError, ValueError):
                self.speeder.delete(0, len(self.speeder.get()))
                self.speeder.insert(0, str(default_speed))

        self.apply = tk.Button(self.master)
        self.apply['text'] = 'Apply'
        self.apply['command'] = internal
        self.apply.place(relheight=0.40, relwidth=0.35, rely=0.55, relx=0.6)

    def create_close(self):
        def internal():
            self.master.destroy()
            self.click_state = False

        self.close = tk.Button(self.master)
        self.close['text'] = 'Close'
        self.close['command'] = internal
        self.close.place(relheight=0.40, relwidth=0.35, rely=0.55, relx=0.05)

    def create_enabler(self):
        def on_press(key):
            global default_button
            self.click_state = False
            default_button = key
            self.write_data()
            return False

        def internal():
            def thread_function():
                self.enabler['text'] = 'Press key'
                listener = pynput.keyboard.Listener(on_press=on_press)
                listener.start()
                listener.join()
                self.enabler['text'] = 'Auto click on:\n' + str(default_button).replace('Key.', '').replace('\'', '').capitalize()
            thread = threading.Thread(target=thread_function)
            thread.start()

        global default_button
        self.enabler = tk.Button(self.master)
        self.enabler['text'] = 'Auto click on:\n' + str(default_button).replace('Key.', '').replace('\'', '').capitalize()
        self.enabler['command'] = internal
        self.enabler.place(relheight=0.40, relwidth=0.35, rely=0.05, relx=0.05)

    def create_speeder(self):
        self.speeder = tk.Entry(self.master)
        self.speeder.insert(0, str(default_speed))
        self.speeder.place(relheight=0.15, relwidth=0.20, rely=0.05, relx=0.71)

        self.speeder_description = tk.Label(self.master)
        self.speeder_description['text'] = 'ms per click'
        self.speeder_description.place(relheight=0.15, relwidth=0.20, rely=0.05, relx=0.50)

        self.speeder_unit = tk.Label(self.master)
        self.speeder_unit['text'] = 'ms'
        self.speeder_unit.place(relheight=0.15, relwidth=0.08, rely=0.05, relx=0.90)

    def create_toggle(self):
        global toggle_state
        self.toggle = tk.Button(self.master)
        try:
            on_image, off_image = tk.PhotoImage(file='data\\On.png'), tk.PhotoImage(file='data\\Off.png')
            self.toggle['bd'] = 0
            if toggle_state:
                self.toggle.config(image=on_image)
            else:
                self.toggle.config(image=off_image)
        except tk.TclError:
            self.toggle['text'] = 'Toggle'

        def internal():
            global toggle_state
            if toggle_state:
                try:
                    self.toggle.config(image=off_image)
                except NameError:
                    pass
                self.toggle_state['text'] = 'off'
                toggle_state = False
            else:
                try:
                    self.toggle.config(image=on_image)
                except NameError:
                    pass
                self.toggle_state['text'] = 'on'
                toggle_state = True

        self.toggle['command'] = internal
        self.toggle.place(relheight=0.20, relwidth=0.15, rely=0.25, relx=0.75)

        self.toggle_description = tk.Label(self.master)
        self.toggle_description['text'] = 'Toggle on key press'
        self.toggle_description.place(relheight=0.20, relwidth=0.25, rely=0.25, relx=0.50)

        self.toggle_state = tk.Label(self.master)
        if toggle_state:
            self.toggle_state['text'] = 'on'
        else:
            self.toggle_state['text'] = 'off'
        self.toggle_state.place(relheight=0.20, relwidth=0.05, rely=0.25, relx=0.90)

    def create_indicator(self):
        self.indicator = tk.Label(self.master, image=self.indicator_off)
        self.indicator.image = self.indicator_off
        self.indicator.place(relheight=0.15, relwidth=0.15, rely=0.43, relx=0.43)

    def create_widgets(self):
        self.create_apply()
        self.create_close()
        self.create_enabler()
        self.create_speeder()
        self.create_toggle()
        self.create_indicator()

    def start_keyboard_listener(self):
        def on_press(key):
            if key == default_button:
                if toggle_state:
                    if self.click_state:
                        self.click_state = False
                    else:
                        self.click_state = True
                else:
                    self.click_state = True

        def on_release(key):
            if not toggle_state:
                if key == default_button:
                    self.click_state = False

        def thread_function():
            listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
            listener.start()

        self.listener_thread = threading.Thread(target=thread_function)
        self.listener_thread.start()

        self.clicker()

    def clicker(self):
        if self.click_state:
            cursor.click(pynput.mouse.Button.left)
            self.indicator.config(image=self.indicator_on)
        else:
            self.indicator.config(image=self.indicator_off)
        self.master.after(default_speed, self.clicker)

    @staticmethod
    def write_data():
        with open('data\\defaults.txt', 'w+') as file:
            file.write(str(default_button) + '\n' + str(default_speed))
            file.close()


if not os.path.exists('data'):
    os.makedirs('data')

root = tk.Tk()
Title = 'MrKingHatters Auto clicker'
root.title(Title)
try:
    icon = 'data\\autoclicker.ico'
    root.iconbitmap(icon)
except tk.TclError:
    pass

cursor = pynput.mouse.Controller()
keyboard = pynput.keyboard.Listener()
root.geometry('470x200')

try:
    f = open('data\\defaults.txt', 'r')
    default_button, default_speed = f.read().split('\n')
    f.close()
    try:
        default_button = eval('pynput.keyboard.' + default_button)
    except SyntaxError:
        default_button = pynput.keyboard.Key.shift
except FileNotFoundError:
    default_button, default_speed = pynput.keyboard.Key.shift, 100
    with open('data\\defaults.txt', 'w+') as f:
        f.write(str(default_button) + '\n' + str(default_speed))
        f.close()

default_speed = int(default_speed)
toggle_state = False

Application = AutoClicker(master=root)
Application.mainloop()
