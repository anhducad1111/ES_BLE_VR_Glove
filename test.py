import customtkinter as ctk
import subprocess


class TestOpenToolDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self._countdown_running = False
        self._current_count = 2  # test cho nhanh
        self.open_tool_button = None

        self.title("Test Open Tool Dialog")
        self.geometry("400x200")
        self.configure(fg_color="#1F1F1F")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._start_countdown()

    def _build_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True)

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Starting...",
            font=("Inter Bold", 24),
            text_color="white"
        )
        self.status_label.pack(pady=20)

    def _start_countdown(self):
        self._countdown_running = True
        self._update_countdown()

    def _update_countdown(self):
        if not self._countdown_running:
            return

        if self._current_count >= 0:
            self.status_label.configure(text=str(self._current_count))
            self._current_count -= 1
            self.after(1000, self._update_countdown)
        else:
            self.status_label.pack_forget()
            self.open_tool_button = ctk.CTkButton(
                self.main_frame,
                text="OPEN TOOL",
                command=self._launch_tool,
                fg_color="transparent",
                hover_color="#333333",
                text_color="#00FF00",
                font=("Inter Bold", 18)
            )
            self.open_tool_button.pack()
            self._countdown_running = False

    def _launch_tool(self):
        try:
            subprocess.Popen(["MotionCal.exe"], shell=True)
        except Exception as e:
            print(f"[ERROR] Failed to launch MotionCal.exe: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.withdraw()  # Ẩn cửa sổ chính

    dialog = TestOpenToolDialog(root)
    dialog.mainloop()
