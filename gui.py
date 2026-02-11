# gui.py
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.constants import *
import os
import csv
import json
from corrin import json_to_character
import leveling as leveling
import fe14unit as fe14unit

# Constants
MIN_CHAPTER = 7
MAX_CHAPTER = 28
ACCENT_CYAN = "#00ACC1"
ACCENT_GREEN = "#2E7D32"
ACCENT_BROWN = "#795548"

class CharacterConverterGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Corn Factory")
        self.geometry("600x400")
        self.configure(bg='white')

        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.chapter = tk.StringVar()
        self.most_recent = tk.IntVar()
        self.most_recent.set(1)
        self.chapter.set(str(MIN_CHAPTER))
        
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        # Input frame
        self.input_frame = ttk.LabelFrame(self, text="Input", padding="10")
        
        self.single_file_btn = ttk.Button(
            self.input_frame, 
            text="Select JSON File",
            command=self._select_file
        )
        
        self.folder_btn = ttk.Button(
            self.input_frame,
            text="Select Folder",
            command=self._select_input_folder
        )
        
        self.input_label = ttk.Label(
            self.input_frame,
            textvariable=self.input_path,
            wraplength=400
        )

        # Output frame
        self.output_frame = ttk.LabelFrame(self, text="Output", padding="10")
        
        self.output_btn = ttk.Button(
            self.output_frame,
            text="Select Output Folder",
            command=self._select_output_folder
        )
        
        self.output_label = ttk.Label(
            self.output_frame,
            textvariable=self.output_path,
            wraplength=400
        )

        # Chapter frame
        self.chapter_frame = ttk.LabelFrame(self, text="Chapter", padding="10")
        self.chapter_dropdown = ttk.Combobox(
            self.chapter_frame,
            textvariable=self.chapter,
            values=[str(i) for i in range(MIN_CHAPTER, MAX_CHAPTER + 1)],
            state='readonly'
        )

        # Buttons frame
        self.buttons_frame = ttk.Frame(self, padding="10")
        
        self.export_spreadsheet_btn = ttk.Button(
            self.buttons_frame,
            text="Export Spreadsheet",
            command=self._export_spreadsheet,
            style='Accent.TButton'
        )
        
        self.export_units_btn = ttk.Button(
            self.buttons_frame,
            text="Export Units",
            command=self._export_units,
            style='Accent.TButton'
        )

        self.most_recent_checkbox = ttk.Checkbutton(
            self.buttons_frame,
            text="Only include each chatter's most recent submission",
            variable=self.most_recent
        )

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Accent.TButton', background=ACCENT_CYAN)

    def _setup_layout(self):
        # Input frame layout
        self.input_frame.pack(fill=X, padx=10, pady=5)
        self.single_file_btn.pack(side=LEFT, padx=5)
        self.folder_btn.pack(side=LEFT, padx=5)
        self.input_label.pack(side=LEFT, padx=5, fill=X, expand=True)

        # Output frame layout
        self.output_frame.pack(fill=X, padx=10, pady=5)
        self.output_btn.pack(side=LEFT, padx=5)
        self.output_label.pack(side=LEFT, padx=5, fill=X, expand=True)

        # Chapter frame layout
        self.chapter_frame.pack(fill=X, padx=10, pady=5)
        self.chapter_dropdown.pack(fill=X, padx=5)

        # Buttons frame layout
        self.buttons_frame.pack(fill=X, padx=10, pady=5)
        self.export_spreadsheet_btn.pack(side=LEFT, padx=5)
        self.export_units_btn.pack(side=LEFT, padx=5)
        self.most_recent_checkbox.pack(side=LEFT, padx=5)

    def _select_file(self):
        filename = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            self.input_path.set(filename)

    def _select_input_folder(self):
        folder = filedialog.askdirectory(
            title="Select Input Folder"
        )
        if folder:
            self.input_path.set(folder)

    def _select_output_folder(self):
        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )
        if folder:
            self.output_path.set(folder)

    def _export_spreadsheet(self):
        if not self.output_path.get():
            tk.messagebox.showerror("Error", "Please select an output folder first.")
            return
            
        input_path = self.input_path.get()
        if not input_path:
            tk.messagebox.showerror("Error", "Please select an input file or folder first.")
            return
            
        characters = []
        
        if os.path.isfile(input_path):
            # Single file
            with open(input_path, 'r') as f:
                json_data = json.load(f)
                characters.append(json_to_character(json_data))
        else:
            # Directory
            for filename in os.listdir(input_path):
                if filename.endswith('.json'):
                    with open(os.path.join(input_path, filename), 'r') as f:
                        json_data = json.load(f)
                        characters.append(json_to_character(json_data))
        
        if not characters:
            tk.messagebox.showerror("Error", "No valid JSON files found.")
            return

        if self.most_recent.get():
            characters = self.filter_obsolete_characters(characters)
            
        # Export to CSV
        output_file = os.path.join(self.output_path.get(), 'Submitted Corrins.csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Corrin Name', 'Twitch Name', 'Build', 'Hair', 'Hair Clip', 
                'Hair Color', 'Color Hex Code', 'Face', 'Facial Feature', 'Voice',
                'Hair Accessory', 'Face Accessory', 'Arm Accessory', 'Body Accessory',
                'Boon', 'Bane', 'Base Class', 'Promoted Class',
                'Personal Skill 1', 'Personal Skill 2', 'Timestamp'
            ])
            
            writer.writeheader()
            for char in characters:
                writer.writerow(char.to_csv_row())
                
        tk.messagebox.showinfo("Success", f"Spreadsheet exported to {output_file}")

    def _export_units(self):
        if not self.output_path.get():
            tk.messagebox.showerror("Error", "Please select an output folder first.")
            return
            
        input_path = self.input_path.get()
        if not input_path:
            tk.messagebox.showerror("Error", "Please select an input file or folder first.")
            return

        characters = []
        
        if os.path.isfile(input_path):
            # Single file
            with open(input_path, 'r') as f:
                json_data = json.load(f)
                characters.append(json_to_character(json_data))
        else:
            # Directory
            for filename in os.listdir(input_path):
                if filename.endswith('.json'):
                    with open(os.path.join(input_path, filename), 'r') as f:
                        json_data = json.load(f)
                        characters.append(json_to_character(json_data))
        
        if not characters:
            tk.messagebox.showerror("Error", "No valid JSON files found.")
            return

        if self.most_recent.get():
            characters = self.filter_obsolete_characters(characters)

        corrin_names = []
        duplicate_names = []
        for char in characters:
            if char.corrin_name in corrin_names:
                if char.corrin_name not in duplicate_names:
                    duplicate_names.append(char.corrin_name)
            else:
                corrin_names.append(char.corrin_name)
        
        for char in characters:
            leveling.level_corrin(int(self.chapter_dropdown.get()), char)
            bytearr = fe14unit.create_fe14unit_bytearray(char)
            filename = char.corrin_name
            if char.corrin_name in duplicate_names:
                filename = char.corrin_name + "(" + char.twitch_name + ")"
            output_file = os.path.join(self.output_path.get(), filename + ".fe14unit")
            with open(output_file, 'wb') as file:
                file.write(bytearr)

        tk.messagebox.showinfo("Success", f"Units exported to {self.output_path.get()}")

    def filter_obsolete_characters(self, characters):
        to_delete = []
        twitch_dict = {}
        for char in characters:
            if char.twitch_name in twitch_dict.keys():
                dict_char = twitch_dict[char.twitch_name]
                if self.compare_timestamps(char.timestamp, dict_char.timestamp) > 0:
                    twitch_dict[char.twitch_name] = char
                    to_delete.append(dict_char)
                else:
                    to_delete.append(char)
            else:
                twitch_dict[char.twitch_name] = char
        return [c for c in characters if c not in to_delete]

    #Returns 1 if the first timestamp is later than the second, -1 if it is earlier, and 0 if they are at the same time
    def compare_timestamps(self, stampstring1, stampstring2):
         stamp1 = stampstring1.split('_')
         stamp2 = stampstring2.split('_')
         for i in range(len(stamp1)):
             if int(stamp1[i]) > int(stamp2[i]):
                 return 1
             elif int(stamp1[i]) < int(stamp2[i]):
                 return -1
         return 0