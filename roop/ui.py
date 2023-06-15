import os
import customtkinter as ctk
from typing import Callable, Tuple

import cv2
from PIL import Image, ImageTk, ImageOps

import roop.globals
from roop.face_analyser import get_one_face
from roop.capturer import get_video_frame, get_video_frame_total
from roop.processors.frame.core import get_frame_processors_modules
from roop.utilities import is_image, is_video, resolve_relative_path, open_with_default_app


WINDOW_HEIGHT = 480
WINDOW_WIDTH = 640
PREVIEW_MAX_HEIGHT = 700
PREVIEW_MAX_WIDTH = 1200
RECENT_DIRECTORY_SOURCE = None
RECENT_DIRECTORY_TARGET = None
RECENT_DIRECTORY_OUTPUT = None

def init(start: Callable, destroy: Callable) -> ctk.CTk:
    global ROOT, PREVIEW

    ROOT = create_root(start, destroy)
    PREVIEW = create_preview(ROOT)

    return ROOT



def create_root(start: Callable, destroy: Callable) -> ctk.CTk:
    global source_button, target_button, status_label

    ctk.deactivate_automatic_dpi_awareness()
    ctk.set_appearance_mode('system')
    ctk.set_default_color_theme(resolve_relative_path('ui.json'))
    root = ctk.CTk()
    root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
    root.title('roop')
    root.configure()
    root.protocol('WM_DELETE_WINDOW', lambda: destroy())

    base_x1 = 0.075
    base_x2 = 0.575
    base_y = 0.6

    source_button = ctk.CTkButton(root, text='Select a face', width=200, height=200, compound='top', anchor='center', command=lambda: select_source_path())
    source_button.place(relx=base_x1, rely=0.05)

    target_button = ctk.CTkButton(root, text='Select a target', width=200, height=200, compound='top', anchor='center', command=lambda: select_target_path())
    target_button.place(relx=base_x2, rely=0.05)

    
    keep_fps_value = ctk.BooleanVar(value=roop.globals.keep_fps)
    keep_fps_checkbox = ctk.CTkSwitch(root, text='Keep fps', variable=keep_fps_value, command=lambda: setattr(roop.globals, 'keep_fps', not roop.globals.keep_fps))
    keep_fps_checkbox.place(relx=base_x1, rely=base_y)

    keep_frames_value = ctk.BooleanVar(value=roop.globals.keep_frames)
    keep_frames_switch = ctk.CTkSwitch(root, text='Keep frames', variable=keep_frames_value, command=lambda: setattr(roop.globals, 'keep_frames', keep_frames_value.get()))
    keep_frames_switch.place(relx=base_x1, rely=0.65)

    keep_audio_value = ctk.BooleanVar(value=roop.globals.keep_audio)
    keep_audio_switch = ctk.CTkSwitch(root, text='Keep audio', variable=keep_audio_value, command=lambda: setattr(roop.globals, 'keep_audio', keep_audio_value.get()))
    keep_audio_switch.place(relx=base_x2, rely=base_y)

    many_faces_value = ctk.BooleanVar(value=roop.globals.many_faces)
    many_faces_switch = ctk.CTkSwitch(root, text='Many faces', variable=many_faces_value, command=lambda: setattr(roop.globals, 'many_faces', many_faces_value.get()))
    many_faces_switch.place(relx=base_x2, rely=0.65)

    enhance_value = ctk.BooleanVar(value=roop.globals.post_enhance)
    enhance_switch = ctk.CTkSwitch(root, text='Post enhance images', variable=enhance_value, command=lambda: setattr(roop.globals, 'post_enhance', enhance_value.get()))
    enhance_switch.place(relx=base_x1, rely=0.7)

    base_y = 0.8
  
    start_button = ctk.CTkButton(root, text='Start', command=lambda: select_output_path(start))
    start_button.place(relx=base_x1, rely=base_y, relwidth=0.15, relheight=0.05)

    stop_button = ctk.CTkButton(root, text='Destroy', command=lambda: destroy())
    stop_button.place(relx=0.35, rely=base_y, relwidth=0.15, relheight=0.05)

    preview_button = ctk.CTkButton(root, text='Preview', command=lambda: toggle_preview())
    preview_button.place(relx=0.55, rely=base_y, relwidth=0.15, relheight=0.05)

    result_button = ctk.CTkButton(root, text='Show Result', command=lambda: show_result())
    result_button.place(relx=0.75, rely=base_y, relwidth=0.15, relheight=0.05)

    status_label = ctk.CTkLabel(root, text=None, justify='center')
    status_label.place(relx=base_x1, rely=0.9, relwidth=0.8)

    return root

def create_preview(parent) -> ctk.CTkToplevel:
    global preview_label, preview_slider

def create_preview(parent) -> ctk.CTkToplevel:
    global preview_label, preview_slider

    preview = ctk.CTkToplevel(parent)
    preview.withdraw()
    preview.title('Preview')
    preview.configure()
    preview.protocol('WM_DELETE_WINDOW', lambda: toggle_preview())
    preview.resizable(width=False, height=False)

    preview_label = ctk.CTkLabel(preview, text=None)
    preview_label.pack(fill='both', expand=True)

    preview_slider = ctk.CTkSlider(preview, from_=0, to=0, command=lambda frame_value: update_preview(frame_value))

    return preview

def update_status(text: str) -> None:
    status_label.configure(text=text)
    ROOT.update()

def update_status(text: str) -> None:
    status_label.configure(text=text)
    ROOT.update()

def select_source_path() -> None:
    global RECENT_DIRECTORY_SOURCE

def select_source_path() -> None:
    global RECENT_DIRECTORY_SOURCE

    PREVIEW.withdraw()
    source_path = ctk.filedialog.askopenfilename(title='select an source image', initialdir=RECENT_DIRECTORY_SOURCE)
    if is_image(source_path):
        roop.globals.source_path = source_path
        RECENT_DIRECTORY_SOURCE = os.path.dirname(roop.globals.source_path)
        image = render_image_preview(roop.globals.source_path, (200, 200))
        source_button.configure(image=image)
    else:
        roop.globals.source_path = None
        source_button.configure(image=None)
    source_button._draw()


def select_target_path() -> None:
    global RECENT_DIRECTORY_TARGET

    PREVIEW.withdraw()
    target_path = ctk.filedialog.askopenfilename(title='select an target image or video', initialdir=RECENT_DIRECTORY_TARGET)
    if is_image(target_path):
        roop.globals.target_path = target_path
        RECENT_DIRECTORY_TARGET = os.path.dirname(roop.globals.target_path)
        image = render_image_preview(roop.globals.target_path, (200, 200))
        target_button.configure(image=image)
    elif is_video(target_path):
        roop.globals.target_path = target_path
        RECENT_DIRECTORY_TARGET = os.path.dirname(roop.globals.target_path)
        video_frame = render_video_preview(target_path, (200, 200))
        target_button.configure(image=video_frame)
    else:
        roop.globals.target_path = None
        target_button.configure(image=None)
    target_button._draw()

def select_output_path(start):
    global RECENT_DIRECTORY_OUTPUT


def select_output_path(start):
    global RECENT_DIRECTORY_OUTPUT

    if is_image(roop.globals.target_path):
        output_path = ctk.filedialog.asksaveasfilename(title='save image output file', initialfile='output.png', initialdir=RECENT_DIRECTORY_OUTPUT)
    elif is_video(roop.globals.target_path):
        output_path = ctk.filedialog.asksaveasfilename(title='save video output file', initialfile='output.mp4', initialdir=RECENT_DIRECTORY_OUTPUT)
    else:
        output_path = None
    if output_path:
        roop.globals.output_path = output_path
        RECENT_DIRECTORY_OUTPUT = os.path.dirname(roop.globals.output_path)
        start()

def show_result():
    open_with_default_app(roop.globals.output_path)
    


def render_image_preview(image_path: str, size: Tuple[int, int] = None) -> ctk.CTkImage:
    image = Image.open(image_path)
    if size:
        image = ImageOps.fit(image, size, Image.LANCZOS)
    return ctk.CTkImage(image, size=image.size)


def render_video_preview(video_path: str, size: Tuple[int, int] = None, frame_number: int = 0) -> ctk.CTkImage:
    capture = cv2.VideoCapture(video_path)
    if frame_number:
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    has_frame, frame = capture.read()
    if has_frame:
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if size:
            image = ImageOps.fit(image, size, Image.LANCZOS)
        return ctk.CTkImage(image, size=image.size)
    capture.release()
    cv2.destroyAllWindows()


def toggle_preview() -> None:
    if PREVIEW.state() == 'normal':
        PREVIEW.withdraw()
    elif roop.globals.source_path and roop.globals.target_path:
        init_preview()
        update_preview()
        PREVIEW.deiconify()


def init_preview() -> None:
    if is_image(roop.globals.target_path):
        preview_slider.pack_forget()
    if is_video(roop.globals.target_path):
        video_frame_total = get_video_frame_total(roop.globals.target_path)
        preview_slider.configure(to=video_frame_total)
        preview_slider.pack(fill='x')
        preview_slider.set(0)


def update_preview(frame_number: int = 0) -> None:
    if roop.globals.source_path and roop.globals.target_path:
        video_frame = None
        for frame_processor in get_frame_processors_modules(roop.globals.frame_processors):
            video_frame = frame_processor.process_frame(
                get_one_face(cv2.imread(roop.globals.source_path)),
                get_video_frame(roop.globals.target_path, frame_number)
            )
        image = Image.fromarray(cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB))
        image = ImageOps.contain(image, (PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        preview_label.configure(image=image)
        preview_label.image = image
