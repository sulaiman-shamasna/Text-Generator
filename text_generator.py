import openai
import os
import threading
import logging
from tkinter import Tk, Label, Button, Entry, Text, filedialog, END, StringVar, OptionMenu
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf
import queue

from helper import get_openai_api_key

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

OPENAI_API_KEY = get_openai_api_key()
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    raise ValueError("Please set your OpenAI API key in the 'OPENAI_API_KEY' environment variable.")

LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']

# Supported models -> Can be updated/ improved
MODELS = ['whisper-1']

# Queue for audio recording ...
q = queue.Queue()

class SpeechToTextApp:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Speech-to-Text Converter")

        # Input File
        self.label_input = Label(master, text="Audio File:")
        self.label_input.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.entry_input = Entry(master, width=50)
        self.entry_input.grid(row=0, column=1, padx=5, pady=5)
        
        self.button_browse = Button(master, text="Browse", command=self.browse_file)
        self.button_browse.grid(row=0, column=2, padx=5, pady=5)
        
        # Language Selection
        self.label_language = Label(master, text="Language:")
        self.label_language.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        
        self.language_var = StringVar(master)
        self.language_var.set('en')  # default value
        
        self.dropdown_language = OptionMenu(master, self.language_var, *LANGUAGES)
        self.dropdown_language.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Model Selection
        self.label_model = Label(master, text="Model:")
        self.label_model.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        
        self.model_var = StringVar(master)
        self.model_var.set('whisper-1')  # default value
        
        self.dropdown_model = OptionMenu(master, self.model_var, *MODELS)
        self.dropdown_model.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Record Button
        self.button_record = Button(master, text="Record Audio", command=self.record_audio)
        self.button_record.grid(row=3, column=0, padx=5, pady=5)
        
        # Transcribe Button
        self.button_transcribe = Button(master, text="Transcribe", command=self.transcribe)
        self.button_transcribe.grid(row=3, column=1, padx=5, pady=5)
        
        # Output Text
        self.text_output = Text(master, wrap='word', height=15, width=60)
        self.text_output.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        # Save Button
        self.button_save = Button(master, text="Save Transcription", command=self.save_transcription)
        self.button_save.grid(row=5, column=1, padx=5, pady=5)
        
        # Initialize variables
        self.audio_file_path = None
        self.recording = False

    def browse_file(self):
        filetypes = (
            ('Audio files', '*.wav *.mp3 *.m4a *.ogg *.flac'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(title='Open an audio file', initialdir='/', filetypes=filetypes)
        if filename:
            self.entry_input.delete(0, END)
            self.entry_input.insert(0, filename)
            self.audio_file_path = filename

    def record_audio(self):
        if not self.recording:
            self.recording = True
            self.button_record.config(text="Stop Recording")
            threading.Thread(target=self._record_audio_thread).start()
        else:
            self.recording = False
            self.button_record.config(text="Record Audio")

    def _record_audio_thread(self):
        fs = 44100  # Sample rate
        self.audio_file_path = 'recorded_audio.wav'
        try:
            with sf.SoundFile(self.audio_file_path, mode='w', samplerate=fs, channels=1) as file:
                with sd.InputStream(samplerate=fs, channels=1, callback=lambda indata, frames, time, status: q.put(indata.copy())):
                    print("Recording...")
                    while self.recording:
                        file.write(q.get())
            print("Recording complete.")
            self.entry_input.delete(0, END)
            self.entry_input.insert(0, self.audio_file_path)
        except Exception as e:
            logging.error(f"Error during recording: {e}")
            self.recording = False
            self.button_record.config(text="Record Audio")
            self.text_output.insert(END, "An error occurred during recording.\n")

    def transcribe(self):
        self.text_output.delete(1.0, END)
        if not self.audio_file_path:
            self.text_output.insert(END, "Please select an audio file or record audio first.\n")
            return

        language = self.language_var.get()
        model = self.model_var.get()
        threading.Thread(target=self._transcribe_thread, args=(self.audio_file_path, language, model)).start()

    def _transcribe_thread(self, file_path, language, model):
        self.button_transcribe.config(state='disabled')
        try:
            transcription = transcribe_audio(file_path, language, model)
            if transcription:
                self.text_output.insert(END, transcription)
            else:
                self.text_output.insert(END, "Transcription failed.\n")
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            self.text_output.insert(END, "An error occurred during transcription.\n")
        finally:
            self.button_transcribe.config(state='normal')

    def save_transcription(self):
        transcription = self.text_output.get(1.0, END)
        if not transcription.strip():
            self.text_output.insert(END, "No transcription to save.\n")
            return

        filetypes = (
            ('Text files', '*.txt'),
            ('PDF files', '*.pdf'),
            ('All files', '*.*')
        )
        filename = filedialog.asksaveasfilename(title='Save transcription', defaultextension='.txt', filetypes=filetypes)
        if filename:
            try:
                if filename.endswith('.txt'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(transcription)
                elif filename.endswith('.pdf'):
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.set_font("Arial", size=12)
                    for line in transcription.split('\n'):
                        pdf.multi_cell(0, 10, line)
                    pdf.output(filename)
                else:
                    self.text_output.insert(END, "Unsupported file format.\n")
                self.text_output.insert(END, f"Transcription saved to {filename}\n")
            except Exception as e:
                logging.error(f"Error saving transcription: {e}")
                self.text_output.insert(END, "An error occurred while saving the transcription.\n")

def transcribe_audio(file_path, language='en', model='whisper-1'):
    try:
        audio = AudioSegment.from_file(file_path)

        # Export audio to a temporary WAV file
        temp_file = 'temp.wav'
        audio.export(temp_file, format='wav')

        with open(temp_file, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                model,
                audio_file,
                language=language
            )

        # Clean up the temporary file
        os.remove(temp_file)

        return transcript['text']

    except Exception as e:
        logging.error(f"Error transcribing {file_path}: {e}")
        return None

def main():
    root = Tk()
    app = SpeechToTextApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
