import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from subprocess import call
import subprocess
import os
import urllib.request
import json
import re

ver_list_url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
ver_list_request = urllib.request.urlopen(ver_list_url)

raw_data = ver_list_request.read()
json_string = raw_data.decode('utf-8')
#to make it a dictionary
data = json.loads(json_string)

#creating a version list
versions_list = data["versions"]


def download_progress(block_num, block_size, total_size):
    if total_size > 0:
        # Calcola i byte scaricati finora
        downloaded = block_num * block_size
        
        # Calcola la percentuale (da 0 a 100)
        percent = (downloaded / total_size) * 100
        
        # Imposta il valore massimo e il valore attuale della progress bar
        progress["maximum"] = 100
        progress["value"] = percent
        
        # IMPORTANTE: Forza Tkinter ad aggiornare la grafica durante il download
        root.update_idletasks()


# Function used when the button is clicked
def click():
  root.update_idletasks()
  progress["value"] = 0
  # Get all the values we got from the inputs
  version = combo_version.get()
  path = entry_path.get()
  name = entry_name.get()

  os.chdir(path)
  call(["mkdir",name])
  os.chdir(name)


  matched_version = None

  #for each elemnt of the verios_list check if there's a coincidence

  for ver in versions_list:
    if version == ver["id"]:
        matched_version = ver
        server_name = "server.jar"
        
        ver_checked_request = urllib.request.urlopen(ver["url"])
        package_data = json.loads(ver_checked_request.read().decode('utf-8'))
        server_download_url = package_data["downloads"]["server"]["url"]

        if server_download_url:
          
          urllib.request.urlretrieve(server_download_url,server_name,reporthook=download_progress)
          
          
          #messagebox.showinfo("Done", "Server file has been downloaded!")

          process = subprocess.Popen(
            ["java","-jar", "server.jar"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
          )

          process.stdin.write('/stop')
          process.stdin.flush()

          process.wait()
          process.stdin.close()
          process.stdout.close()

          with open("eula.txt", "r") as f:
            f = f.read()

          newline = f.replace("eula=false", "eula=true")

          with open("eula.txt","w") as f:
            f.write(newline)

          if flag_crack.get() == 1:
            with open("server.properties", "r") as file_in:
              content = file_in.read()

            new_content_online_mode = re.sub(r"online-mode\s*=\s*(true|True)", "online-mode=false", content)
            new_content_white_list = re.sub(r"white-lists*=\s*(true|True)", "white-list=false", new_content_online_mode)

            with open("server.properties", "w") as file_out:
              file_out.write(new_content_white_list)
        

          ram = f"-Xmx{int(slider.get())}g"
          print(ram)

          process = subprocess.Popen(
            ["java",ram,"-jar","server.jar"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True 
          )
        break

  if not matched_version:
    print(f"Version '{version}' not found.")





# Function to manage the drag/drop
def gestisci_rilascio(event):
  # Clean the path form eventual curly braces
  file_path = event.data.strip("{}")

  # Write the path in the input field
  entry_path.delete(0, tk.END)
  entry_path.insert(0, file_path)


avainable_versions = [ver["id"] for ver in versions_list]

# Creation of the window
root = TkinterDnD.Tk()
root.title("Server Generator")
root.geometry("400x550")

# --- SELECTIONG VERSION ---
label_version = tk.Label(root, text="Version:", font=("Arial", 14), anchor="w")
label_version.pack(anchor="w", pady=10 , padx=5)

combo_version = ttk.Combobox(root, values=avainable_versions, state="readonly")
combo_version.pack(anchor="w", fill="x" ,padx=40, pady=5)

# --- SELECTIONG NAME ---
label_name = tk.Label(root, text="Name:", font=("Arial", 14), anchor="w")
label_name.pack(anchor="w", pady=10 , padx=5)

entry_name = tk.Entry(root, width=40)
entry_name.pack(pady=5)

# --- SELECTION PATH ---
label_path = tk.Label(root, text="Path: (drag the directory)", font=("Arial", 14))
label_path.pack(anchor="w", pady=10 , padx=5)

entry_path = tk.Entry(root, width=40)
entry_path.pack(pady=10)

# --- SELECTIONING RAM ---

ram_path = tk.Label(root, text="Ram assigned:", font=("Arial", 14))
ram_path.pack(anchor="w", pady=10 , padx=5)

slider = tk.Scale(root, from_=1, to=8, length=370, orient=tk.HORIZONTAL)
slider.pack()



# REGISTERING THE INPUT AS AN AVAILABLE PATH DROP
entry_path.drop_target_register(DND_FILES)
entry_path.dnd_bind("<<Drop>>", gestisci_rilascio)

# --- SLECTIONING CRACK LAUNCHER ---
flag_crack = tk.IntVar()
checkbox = tk.Checkbutton(root, text='3rd Party Launcher',variable=flag_crack, onvalue=1, offvalue=0)
checkbox.pack(pady=10)


progress = ttk.Progressbar(root, orient="horizontal", length=300 , mode="determinate")
progress.pack(pady=10)

# --- BUTTON CREATE ---
button = tk.Button(
    root, text="Create", command=click, bg="#4CAF50", fg="black", padx=10, pady=5
)
button.pack(pady=20)

# Start app
root.mainloop()