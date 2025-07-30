"""
GUI components for the Grocery Route Optimizer
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os


class MapDisplay(tk.Frame):
    """Widget to display store maps with route overlay"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill='both', expand=True)
        self.map_image = None
        self.route_overlay = None
        
    def load_map(self, map_path):
        """Load and display a store map image"""
        try:
            # Load image
            image = Image.open(map_path)
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
            self.map_image = ImageTk.PhotoImage(image)
            
            # Display on canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor='nw', image=self.map_image)
            
        except Exception as e:
            print(f"Error loading map: {e}")
            
    def draw_route(self, route_points):
        """Draw route overlay on the map"""
        if not self.map_image:
            return
            
        # Create overlay for route
        # This would draw lines connecting the route points
        # For now, this is a placeholder
        pass
        

class GroceryListInput(tk.Frame):
    """Enhanced grocery list input widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create text widget with scrollbar
        self.text = tk.Text(self, wrap='word', width=40, height=20)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def get_items(self):
        """Get list of grocery items"""
        text = self.text.get('1.0', 'end-1c')
        return [item.strip() for item in text.split('\n') if item.strip()]
        
    def set_items(self, items):
        """Set the grocery list"""
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', '\n'.join(items))
        

class RouteDisplay(tk.Frame):
    """Widget to display the optimized route"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create treeview for route display
        self.tree = ttk.Treeview(self, columns=('Item', 'Location', 'Status'), show='tree headings')
        
        # Configure columns
        self.tree.heading('#0', text='Step')
        self.tree.heading('Item', text='Item')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Status', text='Status')
        
        # Column widths
        self.tree.column('#0', width=50)
        self.tree.column('Item', width=200)
        self.tree.column('Location', width=150)
        self.tree.column('Status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def display_route(self, route):
        """Display the shopping route"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add route items
        for i, (item, location) in enumerate(route, 1):
            self.tree.insert('', 'end', text=str(i), 
                           values=(item, location, 'Pending'))
                           
    def mark_item_complete(self, index):
        """Mark an item as complete"""
        items = self.tree.get_children()
        if 0 <= index < len(items):
            item_id = items[index]
            values = list(self.tree.item(item_id)['values'])
            values[2] = 'Complete'
            self.tree.item(item_id, values=values)
            
            # Update styling
            self.tree.tag_configure('complete', foreground='green')
            self.tree.item(item_id, tags=('complete',))