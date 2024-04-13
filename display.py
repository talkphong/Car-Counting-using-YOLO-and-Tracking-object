import subprocess
import tkinter as tk
from tkinter import filedialog
import sys


class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")

        # Biến lưu đường dẫn của file video
        self.video_path = tk.StringVar()
        
        # Tạo các thành phần giao diện
        self.create_widgets()

    def create_widgets(self):
        # Label để hiển thị đường dẫn file video
        label_path = tk.Label(self.root, text="Video Path:")
        label_path.pack(pady=10)

        # Entry để hiển thị và chỉnh sửa đường dẫn file video
        entry_path = tk.Entry(self.root, textvariable=self.video_path, width=40)
        entry_path.pack(pady=5)

        # Button để chọn file
        button_browse = tk.Button(self.root, text="Browse", command=self.browse_file)
        button_browse.pack(pady=5)

        # Button để hiển thị video
        button_play = tk.Button(self.root, text="Play Video", command=self.play_video)
        button_play.pack(pady=10)

    def browse_file(self):
        # Hiển thị hộp thoại chọn file và cập nhật giá trị đường dẫn
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
        self.video_path.set(file_path)

    def play_video(self):
        # Đọc và hiển thị video
        video_path = self.video_path.get()
       
        python_executable = sys.executable
        # Gọi playvideo.py bằng subprocess và truyền đường dẫn đã chọn làm tham số dòng lệnh
        subprocess.run([python_executable, "Car_counting.py", video_path])

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()
