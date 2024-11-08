import os
import shutil
import time
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import pygame
from threading import Thread
from pydub import AudioSegment

# Initialize pygame mixer
pygame.mixer.init()

# Set up GUI
root = Tk()
root.title("Audio Categorizer")

# Global variables
audio_file = None
categories = ["child crying", "dog barking", "rain sounds", "traffic noise"]
audio_folder_path = r"C:\Users\user\Downloads\drive-download-20241031T212756Z-001"
base_save_path = r"C:\Users\user\Documents\Categorized_Audio"  # Base folder for categorized audio

# Create category folder within the specified path
def create_folder(category):
    path = os.path.join(base_save_path, category)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# Function to convert audio to .wav if needed
def convert_to_wav(file_path):
    audio = AudioSegment.from_file(file_path)
    wav_file = file_path.replace(os.path.splitext(file_path)[1], ".wav")
    audio.export(wav_file, format="wav")
    return wav_file

# Function to play the audio file using pygame
def play_audio():
    global audio_file
    if audio_file:
        # Convert to .wav if not in supported format
        if not audio_file.endswith(".wav"):
            audio_file = convert_to_wav(audio_file)
        
        def play_thread():
            try:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                update_progress_bar()
            except pygame.error as e:
                messagebox.showerror("Error", f"Could not play the audio: {e}")
        Thread(target=play_thread).start()
    else:
        messagebox.showwarning("No File", "Please load an audio file first.")

# Function to stop the audio playback and unload the file
def stop_audio():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    messagebox.showinfo("Audio Stopped", "The audio playback has been stopped and file unloaded.")

# Function to load audio file
def load_audio():
    global audio_file
    file_path = filedialog.askopenfilename(
        initialdir=audio_folder_path,  # Set default directory
        filetypes=[("Audio Files", "*.mp3 *.wav *.mp4 *.m4a")]
    )
    if file_path:
        audio_file = file_path
        label_file.config(text=f"Loaded: {os.path.basename(file_path)}")
        reset_progress_bar()

# Function to reset the progress bar
def reset_progress_bar():
    progress_bar['value'] = 0
    progress_bar.update()

# Function to update the progress bar
def update_progress_bar():
    if pygame.mixer.music.get_busy():
        # Get the position of the audio in milliseconds
        pos = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
        audio_length = pygame.mixer.Sound(audio_file).get_length()

        # Calculate the progress as a percentage
        progress = (pos / audio_length) * 100

        # Update the progress bar
        progress_bar['value'] = progress
        progress_bar.update()

        # Call this function again after a short delay to continue updating
        root.after(100, update_progress_bar)
    else:
        progress_bar['value'] = 0

# Function to categorize and save the file
def save_categorized_audio():
    global audio_file
    if audio_file:
        # Stop the audio and unload it if it's playing
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
        # Add a slight delay to ensure file release
        time.sleep(0.5)  # 0.5 seconds delay

        selected_category = category_var.get()
        if selected_category:
            category_path = create_folder(selected_category)  # Create or get the category folder path
            file_name = os.path.basename(audio_file)
            dest_path = os.path.join(category_path, file_name)
            
            try:
                # Use shutil.move to move the file
                shutil.move(audio_file, dest_path)
                messagebox.showinfo("Success", f"Audio saved to '{category_path}' folder.")
                label_file.config(text="No file loaded.")
                audio_file = None  # Reset the audio file
            except PermissionError:
                messagebox.showerror("Error", "The audio file is currently in use. Please stop the audio before saving.")
        else:
            messagebox.showwarning("Select Category", "Please select a category.")
    else:
        messagebox.showwarning("No File", "Please load an audio file first.")

# GUI elements
frame = Frame(root)
frame.pack(pady=20)

label_file = Label(frame, text="No file loaded")
label_file.pack()

btn_load = Button(frame, text="Load Audio", command=load_audio)
btn_load.pack(pady=5)

btn_play = Button(frame, text="Play Audio", command=play_audio)
btn_play.pack(pady=5)

# Add Stop button
btn_stop = Button(frame, text="Stop Audio", command=stop_audio)
btn_stop.pack(pady=5)

category_var = StringVar(root)
category_var.set("Select Category")  # default value

dropdown = OptionMenu(frame, category_var, *categories)
dropdown.pack(pady=5)

btn_save = Button(frame, text="Save to Category", command=save_categorized_audio)
btn_save.pack(pady=5)

# Progress bar for audio playback
progress_bar = Progressbar(frame, length=300, maximum=100, mode='determinate')
progress_bar.pack(pady=10)

# Run the GUI main loop
root.mainloop()
