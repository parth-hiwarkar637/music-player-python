import os
os.environ["pygame_hide_support_prompt"] = "hide"
import pygame
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

# -------------------------------------------------------------
#                FIXED REAL IMAGE PATHS
# -------------------------------------------------------------
BASE = r"D:\python\music player\music_player_better gui\assets"

HEADER_IMG = os.path.join(BASE, "header.png")        # NEW HEADER
ICON_IMG = os.path.join(BASE, "paw_icon.jpg")
BACKGROUND_IMG = os.path.join(BASE, "background.jpeg")

MUSIC_FOLDER = "music"

WINDOW_W = 420
WINDOW_H = 750

BG_PINK = "#FDD9E5"
CARD_BG = "#FFFFFF"
PLAY_BTN_BG = "#FFE3EA"
TEXT_COLOR = "#5A3A45"

pygame.mixer.init()

# -------------------------------------------------------------
#                   CHECK MUSIC FOLDER
# -------------------------------------------------------------
if not os.path.isdir(MUSIC_FOLDER):
    messagebox.showerror("Error", f"Music folder '{MUSIC_FOLDER}' not found.")
    raise SystemExit

songs = [s for s in os.listdir(MUSIC_FOLDER) if s.lower().endswith(".mp3")]

if not songs:
    messagebox.showerror("Error", "No .mp3 files found in the music folder.")
    raise SystemExit

# -------------------------------------------------------------
#                   MAIN WINDOW
# -------------------------------------------------------------
root = tk.Tk()
root.title("Cute Cat Music Player 🎀")
root.geometry(f"{WINDOW_W}x{WINDOW_H}")
root.resizable(False, False)

main_canvas = tk.Canvas(root, width=WINDOW_W, height=WINDOW_H, highlightthickness=0)
main_canvas.pack(fill="both", expand=True)

img_refs = {}

# -------------------------------------------------------------
#                   TILE BACKGROUND
# -------------------------------------------------------------
def tile_background():
    bg_img = Image.open(BACKGROUND_IMG).convert("RGBA")
    w, h = bg_img.size
    scale = 120 / min(w, h)
    bg_img = bg_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    
    bg_photo = ImageTk.PhotoImage(bg_img)
    img_refs["bg"] = bg_photo
    
    tw = bg_photo.width()
    th = bg_photo.height()
    
    for x in range(0, WINDOW_W, tw):
        for y in range(0, WINDOW_H, th):
            main_canvas.create_image(x, y, image=bg_photo, anchor="nw")

tile_background()

# -------------------------------------------------------------
#                   NEW SMALLER HEADER
# -------------------------------------------------------------
def draw_header():
    img = Image.open(HEADER_IMG).convert("RGBA")
    w, h = img.size
    
    target_w = 240     # smaller header width
    scale = target_w / w
    new_h = int(h * scale)
    
    img = img.resize((target_w, new_h), Image.LANCZOS)

    header_photo = ImageTk.PhotoImage(img)
    img_refs["header"] = header_photo

    main_canvas.create_image(WINDOW_W // 2, 20, image=header_photo, anchor="n")
    return 20 + new_h

header_bottom = draw_header()

# -------------------------------------------------------------
#               SONG LIST TITLE (touches header)
# -------------------------------------------------------------
main_canvas.create_text(
    WINDOW_W // 2,
    header_bottom + 5,      # touching header
    text="Song List",
    font=("Comic Sans MS", 22, "bold"),
    fill=TEXT_COLOR,
    anchor="n"
)

title_bottom = header_bottom + 55   # moved up closer

# -------------------------------------------------------------
#            SCROLL AREA FOR SONG CARDS
# -------------------------------------------------------------
container = tk.Frame(main_canvas, width=WINDOW_W, height=WINDOW_H - title_bottom - 150, bg=BG_PINK)
main_canvas.create_window(WINDOW_W // 2, title_bottom, window=container, anchor="n")

inner_canvas = tk.Canvas(container, bg=BG_PINK, highlightthickness=0)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=inner_canvas.yview)
inner_canvas.configure(yscrollcommand=scrollbar.set)

inner_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

cards_frame = tk.Frame(inner_canvas, bg=BG_PINK)
inner_canvas.create_window((0, 0), window=cards_frame, anchor="nw")

def update_scroll(event):
    inner_canvas.configure(scrollregion=inner_canvas.bbox("all"))
cards_frame.bind("<Configure>", update_scroll)

inner_canvas.bind_all("<MouseWheel>", lambda e: inner_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

# -------------------------------------------------------------
#                   SONG ICON (PAW)
# -------------------------------------------------------------
icon_img = Image.open(ICON_IMG).convert("RGBA").resize((45, 45), Image.LANCZOS)
icon_photo = ImageTk.PhotoImage(icon_img)
img_refs["icon"] = icon_photo

# -------------------------------------------------------------
#                   MUSIC FUNCTIONS
# -------------------------------------------------------------
current_song = None

def play_music(name):
    global current_song
    pygame.mixer.music.load(os.path.join(MUSIC_FOLDER, name))
    pygame.mixer.music.play()
    current_song = name
    now_label.config(text=f"🎶 Now Playing: {os.path.splitext(name)[0]}")

def pause_music():
    pygame.mixer.music.pause()

def resume_music():
    pygame.mixer.music.unpause()

def stop_music():
    pygame.mixer.music.stop()
    now_label.config(text="No song playing")

# -------------------------------------------------------------
#                SONG CARD LAYOUT FIXED
# -------------------------------------------------------------
def make_card(song):
    card = tk.Frame(cards_frame, bg=CARD_BG)
    card.pack(fill="x", pady=10, padx=20)

    # Left icon
    tk.Label(card, image=icon_photo, bg=CARD_BG).pack(side="left", padx=10)

    # Song info
    mid = tk.Frame(card, bg=CARD_BG)
    mid.pack(side="left", fill="both", expand=True)

    title = os.path.splitext(song)[0]
    tk.Label(mid, text=title, bg=CARD_BG, fg=TEXT_COLOR, font=("Arial", 12, "bold")).pack(anchor="w")
    tk.Label(mid, text=song, bg=CARD_BG, fg="#7a7a7a", font=("Arial", 9)).pack(anchor="w")

    # FIXED PLAY BUTTON (no overflow)
    tk.Button(
        card,
        text="Play ▶",
        command=lambda: play_music(song),
        bg=PLAY_BTN_BG,
        fg="black",
        font=("Arial", 10, "bold"),
        width=7
    ).pack(side="right", padx=10)

for s in songs:
    make_card(s)

# -------------------------------------------------------------
#               CONTROLS BOTTOM
# -------------------------------------------------------------
controls = tk.Frame(root, bg=BG_PINK)
main_canvas.create_window(WINDOW_W // 2, WINDOW_H - 120, window=controls, anchor="n")

btn_style = dict(bg=PLAY_BTN_BG, fg="black", font=("Arial", 11, "bold"), width=9)

tk.Button(controls, text="Pause ⏸", command=pause_music, **btn_style).grid(row=0, column=0, padx=5)
tk.Button(controls, text="Resume ⏯", command=resume_music, **btn_style).grid(row=0, column=1, padx=5)
tk.Button(controls, text="Stop ⏹", command=stop_music, **btn_style).grid(row=0, column=2, padx=5)

now_label = tk.Label(root, text="No song playing", bg=BG_PINK, fg=TEXT_COLOR, font=("Arial", 12))
main_canvas.create_window(WINDOW_W // 2, WINDOW_H - 60, window=now_label, anchor="n")

root.mainloop()
