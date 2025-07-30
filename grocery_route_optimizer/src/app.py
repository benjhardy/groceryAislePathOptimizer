"""
Main application class for the Grocery Route Optimizer
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import scrolledtext
import threading
from pathlib import Path

from .store_finder import StoreFinder
from .store_scraper import KrogerScraper
from .route_optimizer import RouteOptimizer
from .gui_components import MapDisplay, GroceryListInput, RouteDisplay


class GroceryRouteApp:
    """Main application class for the Grocery Route Optimizer"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grocery Route Optimizer")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.store_finder = StoreFinder()
        self.scraper = KrogerScraper()
        self.route_optimizer = RouteOptimizer()
        
        # Store data
        self.selected_store = None
        self.store_map = None
        self.grocery_list = []
        self.item_locations = {}
        self.optimized_route = []
        self.current_item_index = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_store_selection_tab()
        self.setup_grocery_list_tab()
        self.setup_route_tab()
        
    def setup_store_selection_tab(self):
        """Set up the store selection tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Store Selection")
        
        # Zip code input
        zip_frame = ttk.Frame(tab)
        zip_frame.pack(pady=20)
        
        ttk.Label(zip_frame, text="Enter Zip Code:").pack(side='left', padx=5)
        self.zip_entry = ttk.Entry(zip_frame, width=10)
        self.zip_entry.pack(side='left', padx=5)
        
        search_btn = ttk.Button(zip_frame, text="Find Stores", command=self.find_stores)
        search_btn.pack(side='left', padx=5)
        
        # Store list
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Label(list_frame, text="Available Stores:").pack(anchor='w')
        
        # Create scrollable frame for stores
        self.store_listbox = tk.Listbox(list_frame, height=10)
        self.store_listbox.pack(fill='both', expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.store_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.store_listbox.config(yscrollcommand=scrollbar.set)
        
        # Store selection button
        select_btn = ttk.Button(list_frame, text="Select Store", command=self.select_store)
        select_btn.pack(pady=10)
        
        # Map upload option
        map_frame = ttk.LabelFrame(tab, text="Store Map")
        map_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(map_frame, text="Upload store map (optional):").pack(anchor='w', padx=10, pady=5)
        
        upload_btn = ttk.Button(map_frame, text="Upload Map Image", command=self.upload_map)
        upload_btn.pack(padx=10, pady=5)
        
        self.map_status_label = ttk.Label(map_frame, text="No map uploaded")
        self.map_status_label.pack(padx=10, pady=5)
        
    def setup_grocery_list_tab(self):
        """Set up the grocery list input tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Grocery List")
        
        # Instructions
        ttk.Label(tab, text="Enter your grocery items (one per line):").pack(anchor='w', padx=20, pady=10)
        
        # Text area for grocery list
        self.grocery_text = scrolledtext.ScrolledText(tab, height=15, width=50)
        self.grocery_text.pack(padx=20, pady=10)
        
        # Sample items
        sample_items = "Milk\nBread\nEggs\nBananas\nPeanut Butter\nChicken Breast\nTomatoes\nCheese\nYogurt"
        self.grocery_text.insert('1.0', sample_items)
        
        # Process button
        process_btn = ttk.Button(tab, text="Process List & Find Locations", command=self.process_grocery_list)
        process_btn.pack(pady=10)
        
        # Status label
        self.list_status_label = ttk.Label(tab, text="")
        self.list_status_label.pack(pady=5)
        
    def setup_route_tab(self):
        """Set up the route optimization and navigation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Shopping Route")
        
        # Control buttons
        control_frame = ttk.Frame(tab)
        control_frame.pack(pady=20)
        
        self.optimize_btn = ttk.Button(control_frame, text="Optimize Route", command=self.optimize_route)
        self.optimize_btn.pack(side='left', padx=5)
        
        self.start_btn = ttk.Button(control_frame, text="Start Shopping", command=self.start_shopping, state='disabled')
        self.start_btn.pack(side='left', padx=5)
        
        # Current item display
        self.current_item_frame = ttk.LabelFrame(tab, text="Current Item")
        self.current_item_frame.pack(fill='x', padx=20, pady=10)
        
        self.current_item_label = ttk.Label(self.current_item_frame, text="Not started", font=('Arial', 16, 'bold'))
        self.current_item_label.pack(pady=10)
        
        self.location_label = ttk.Label(self.current_item_frame, text="", font=('Arial', 12))
        self.location_label.pack(pady=5)
        
        # Found button
        self.found_btn = ttk.Button(self.current_item_frame, text="✓ Found Item", 
                                   command=self.mark_item_found, state='disabled',
                                   style='Success.TButton')
        self.found_btn.pack(pady=20)
        
        # Route display
        route_frame = ttk.LabelFrame(tab, text="Optimized Route")
        route_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.route_text = scrolledtext.ScrolledText(route_frame, height=10, width=60)
        self.route_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def find_stores(self):
        """Find stores near the entered zip code"""
        zip_code = self.zip_entry.get().strip()
        if not zip_code:
            messagebox.showwarning("Input Error", "Please enter a zip code")
            return
            
        # Show loading
        self.store_listbox.delete(0, tk.END)
        self.store_listbox.insert(0, "Searching for stores...")
        
        # Run in thread to prevent UI freeze
        thread = threading.Thread(target=self._find_stores_thread, args=(zip_code,))
        thread.start()
        
    def _find_stores_thread(self, zip_code):
        """Thread function to find stores"""
        try:
            stores = self.store_finder.find_kroger_stores(zip_code)
            
            # Update UI in main thread
            self.root.after(0, self._update_store_list, stores)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to find stores: {str(e)}"))
            
    def _update_store_list(self, stores):
        """Update the store listbox with found stores"""
        self.store_listbox.delete(0, tk.END)
        
        if not stores:
            self.store_listbox.insert(0, "No stores found")
            return
            
        self.stores = stores
        for i, store in enumerate(stores):
            store_text = f"{store['name']} - {store['address']} ({store['distance']} miles)"
            self.store_listbox.insert(i, store_text)
            
    def select_store(self):
        """Select a store from the list"""
        selection = self.store_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a store")
            return
            
        index = selection[0]
        self.selected_store = self.stores[index]
        messagebox.showinfo("Store Selected", f"Selected: {self.selected_store['name']}")
        
        # Enable next tab
        self.notebook.tab(1, state='normal')
        
    def upload_map(self):
        """Upload a store map image"""
        filename = filedialog.askopenfilename(
            title="Select Store Map",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        
        if filename:
            self.store_map = filename
            self.map_status_label.config(text=f"Map uploaded: {Path(filename).name}")
            
    def process_grocery_list(self):
        """Process the grocery list and find item locations"""
        if not self.selected_store:
            messagebox.showwarning("Store Error", "Please select a store first")
            return
            
        # Get grocery items
        text = self.grocery_text.get('1.0', 'end-1c')
        self.grocery_list = [item.strip() for item in text.split('\n') if item.strip()]
        
        if not self.grocery_list:
            messagebox.showwarning("List Error", "Please enter at least one item")
            return
            
        self.list_status_label.config(text="Finding item locations...")
        
        # Run in thread
        thread = threading.Thread(target=self._find_item_locations_thread)
        thread.start()
        
    def _find_item_locations_thread(self):
        """Thread function to find item locations"""
        try:
            # Use scraper to find item locations
            self.item_locations = self.scraper.find_item_locations(
                self.grocery_list, 
                self.selected_store['id']
            )
            
            # Update UI
            found_count = len([loc for loc in self.item_locations.values() if loc])
            status_text = f"Found locations for {found_count}/{len(self.grocery_list)} items"
            
            self.root.after(0, lambda: self.list_status_label.config(text=status_text))
            self.root.after(0, lambda: self.notebook.tab(2, state='normal'))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to find item locations: {str(e)}"))
            
    def optimize_route(self):
        """Optimize the shopping route"""
        if not self.item_locations:
            messagebox.showwarning("Data Error", "Please process grocery list first")
            return
            
        try:
            # Filter items with known locations
            items_with_locations = [(item, loc) for item, loc in self.item_locations.items() if loc]
            
            if not items_with_locations:
                messagebox.showwarning("Location Error", "No item locations found")
                return
                
            # Optimize route
            self.optimized_route = self.route_optimizer.optimize_route(items_with_locations)
            
            # Display route
            self.route_text.delete('1.0', tk.END)
            route_text = "Optimized Shopping Route:\n\n"
            
            for i, (item, location) in enumerate(self.optimized_route, 1):
                route_text += f"{i}. {item} - {location}\n"
                
            self.route_text.insert('1.0', route_text)
            
            # Enable start button
            self.start_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize route: {str(e)}")
            
    def start_shopping(self):
        """Start the shopping journey"""
        if not self.optimized_route:
            messagebox.showwarning("Route Error", "Please optimize route first")
            return
            
        self.current_item_index = 0
        self.found_btn.config(state='normal')
        self.start_btn.config(state='disabled')
        
        self.show_current_item()
        
    def show_current_item(self):
        """Display the current item to find"""
        if self.current_item_index >= len(self.optimized_route):
            # Shopping complete
            self.current_item_label.config(text="Shopping Complete!")
            self.location_label.config(text="All items found")
            self.found_btn.config(state='disabled')
            messagebox.showinfo("Complete", "Shopping trip complete!")
            return
            
        item, location = self.optimized_route[self.current_item_index]
        self.current_item_label.config(text=item)
        self.location_label.config(text=f"Location: {location}")
        
    def mark_item_found(self):
        """Mark current item as found and move to next"""
        self.current_item_index += 1
        self.show_current_item()
        
    def run(self):
        """Run the application"""
        # Style configuration
        style = ttk.Style()
        style.configure('Success.TButton', foreground='green')
        
        # Start the GUI
        self.root.mainloop()