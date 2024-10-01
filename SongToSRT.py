import os
import requests
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    messagebox.showerror("Error", "API key not found. Please set the OPENAI_API_KEY environment variable.")
    exit(1)

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Transcription Tool")

        # Variables to hold file paths
        self.audio_file_path = tk.StringVar()
        self.output_folder_path = tk.StringVar(value=os.getcwd())

        # Audio File Selection
        self.audio_label = tk.Label(root, text="Audio File:")
        self.audio_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.audio_entry = tk.Entry(root, textvariable=self.audio_file_path, width=50)
        self.audio_entry.grid(row=0, column=1, padx=5, pady=5)

        self.audio_button = tk.Button(root, text="Browse", command=self.browse_audio_file)
        self.audio_button.grid(row=0, column=2, padx=5, pady=5)

        # Output Folder Selection
        self.output_label = tk.Label(root, text="Output Folder:")
        self.output_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        self.output_entry = tk.Entry(root, textvariable=self.output_folder_path, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)

        self.output_button = tk.Button(root, text="Browse", command=self.browse_output_folder)
        self.output_button.grid(row=1, column=2, padx=5, pady=5)

        # Transcribe Button
        self.transcribe_button = tk.Button(root, text="Transcribe", command=self.start_transcription)
        self.transcribe_button.grid(row=2, column=0, columnspan=3, padx=5, pady=10)

        # Messages Text Area
        self.messages_text = tk.Text(root, height=10, width=70)
        self.messages_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

    def browse_audio_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.ogg *.webm")]
        )
        if file_path:
            self.audio_file_path.set(file_path)

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_folder_path.set(folder_path)

    def start_transcription(self):
        audio_file = self.audio_file_path.get()
        output_folder = self.output_folder_path.get()
        if not audio_file:
            messagebox.showerror("Error", "Please select an audio file.")
            return

        if not os.path.exists(audio_file):
            messagebox.showerror("Error", f"Audio file not found: {audio_file}")
            return

        output_srt_path = os.path.join(
            output_folder,
            os.path.splitext(os.path.basename(audio_file))[0] + ".srt"
        )

        # Disable the transcribe button during processing
        self.transcribe_button.config(state=tk.DISABLED)
        self.messages_text.delete('1.0', tk.END)
        self.messages_text.insert(tk.END, "Starting transcription...\n")

        # Start the transcription in a separate thread to avoid blocking the GUI
        threading.Thread(
            target=self.transcribe_audio_thread,
            args=(audio_file, output_srt_path)
        ).start()

    def transcribe_audio_thread(self, audio_file_path, output_srt_path):
        try:
            # Check the file size
            file_size = os.path.getsize(audio_file_path)
            max_size = 25 * 1024 * 1024  # 25 MB
            temp_audio_path = audio_file_path  # Default to original file

            if file_size > max_size:
                self.update_messages("Audio file exceeds 25 MB. Compressing audio...")
                temp_audio_path = self.compress_audio(audio_file_path)
                self.update_messages("Audio compressed successfully.")

            # Transcribe the (possibly compressed) audio file
            self.update_messages("Transcribing audio...")
            with open(temp_audio_path, 'rb') as audio_file:
                # Determine MIME type
                mime_type = self.get_mime_type(temp_audio_path)
                # Set up the request
                headers = {
                    'Authorization': f'Bearer {OPENAI_API_KEY}',
                }
                files = {
                    'file': (os.path.basename(temp_audio_path), audio_file, mime_type),
                    'model': (None, 'whisper-1'),
                    'response_format': (None, 'srt'),
                }
                response = requests.post(
                    'https://api.openai.com/v1/audio/transcriptions',
                    headers=headers,
                    files=files
                )

                if response.status_code == 200:
                    srt_content = response.text
                    with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
                        srt_file.write(srt_content)
                    self.update_messages(f"Transcription saved to {output_srt_path}")
                else:
                    error_message = f"Error {response.status_code}: {response.text}"
                    self.update_messages(error_message)
                    messagebox.showerror("Error", error_message)
        except Exception as e:
            self.update_messages(f"An error occurred: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            # Remove temporary compressed file if created
            if temp_audio_path != audio_file_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            # Re-enable the transcribe button
            self.transcribe_button.config(state=tk.NORMAL)

    def compress_audio(self, input_file_path):
        from pydub import AudioSegment

        # Load the audio file
        audio = AudioSegment.from_file(input_file_path)

        # Apply compression settings
        target_bitrate = "64k"
        target_sample_rate = 16000  # Hz
        target_channels = 1  # Mono

        # Set parameters
        audio = audio.set_frame_rate(target_sample_rate)
        audio = audio.set_channels(target_channels)

        # Generate a temporary file path
        temp_file_path = os.path.splitext(input_file_path)[0] + "_compressed.mp3"

        # Export the compressed audio
        audio.export(temp_file_path, format="mp3", bitrate=target_bitrate)

        # Check if the compressed file is under the size limit
        compressed_size = os.path.getsize(temp_file_path)
        max_size = 25 * 1024 * 1024  # 25 MB

        if compressed_size > max_size:
            # If still too large, attempt further compression
            self.update_messages("Further compressing audio to meet size requirements...")
            # Reduce bitrate further
            target_bitrate = "48k"
            audio.export(temp_file_path, format="mp3", bitrate=target_bitrate)
            compressed_size = os.path.getsize(temp_file_path)

            if compressed_size > max_size:
                raise Exception("Unable to compress audio below 25 MB limit.")

        return temp_file_path

    def update_messages(self, message):
        self.messages_text.insert(tk.END, message + '\n')
        self.messages_text.see(tk.END)

    def get_mime_type(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.wav':
            return 'audio/wav'
        elif ext == '.mp3':
            return 'audio/mpeg'
        elif ext == '.m4a':
            return 'audio/mp4'
        elif ext == '.ogg':
            return 'audio/ogg'
        elif ext == '.webm':
            return 'audio/webm'
        else:
            return 'application/octet-stream'  # Fallback

if __name__ == '__main__':
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()
