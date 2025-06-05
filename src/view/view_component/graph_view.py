import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class GraphView(ctk.CTkFrame):
    def __init__(self, parent, figsize=(7, 5), dpi=70, bg_color='#3A3A3A'):
        super().__init__(parent)

        # Create and embed matplotlib plot
        self.fig = Figure(figsize=figsize, dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor(bg_color)  # Set figure background
        self.ax.set_facecolor(bg_color)  # Set plot background
        
        # Configure axis limits and appearance
        self.ax.set_xlim(0, 16000)
        self.ax.set_ylim(0, 16000)
        self.ax.tick_params(colors='white')  # Make ticks white
        self.ax.grid(True, color='gray', alpha=0.3)  # Add subtle grid
        
        # Create scatter plot for single point (initialized at 0,0)
        self.point = self.ax.scatter([0], [0], color='red', s=100)
        
        # Create canvas and embed in frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_xy(self, x: float, y: float):
        """Update the point position with new x,y coordinates"""
        self.point.set_offsets([[x, y]])
        self.canvas.draw()
