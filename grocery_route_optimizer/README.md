# Grocery Route Optimizer

A Python proof-of-concept application that optimizes shopping routes inside grocery stores. The app helps users find the most efficient path through a store to collect all items on their grocery list.

## Features

- **Store Locator**: Find nearby Kroger stores using zip code
- **Grocery List Management**: Input and manage your shopping list
- **Item Location Finding**: Automatically finds or estimates item locations within the store
- **Route Optimization**: Calculates the most efficient path through the store using TSP algorithms
- **Interactive Shopping Mode**: Check off items as you find them
- **Store Map Support**: Option to upload store layout maps

## Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd grocery_route_optimizer
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Run the application from the project directory:

```bash
python main.py
```

## How to Use

### 1. Store Selection
- Enter your zip code in the first tab
- Click "Find Stores" to search for nearby Kroger locations
- Select a store from the list
- Optionally upload a store map image if you have one

### 2. Create Your Grocery List
- Navigate to the "Grocery List" tab
- Enter items one per line
- Click "Process List & Find Locations" to find where items are located in the store

### 3. Optimize Your Route
- Go to the "Shopping Route" tab
- Click "Optimize Route" to calculate the most efficient path
- The app will show you the optimized order to collect your items

### 4. Shop with the Route
- Click "Start Shopping" to begin
- The app will show you each item and its location
- Click "✓ Found Item" when you find each item
- Continue until all items are collected

## Current Limitations

This is a proof of concept with the following limitations:

1. **Store Data**: Currently uses mock data for store locations and item placements when real data is unavailable
2. **Item Locations**: Estimates item locations based on common grocery store layouts
3. **Maps**: Store maps must be uploaded manually as most stores don't provide public layout data
4. **Store Support**: Currently optimized for Kroger stores, with planned support for other chains

## Technical Details

The application uses:
- **tkinter**: GUI framework
- **requests/BeautifulSoup**: Web scraping for store and item data
- **networkx/python-tsp**: Route optimization algorithms
- **geopy**: Location services
- **Pillow**: Image handling for store maps

## Future Enhancements

- Mobile app versions (Android/iOS)
- Real-time store API integration
- Support for more grocery chains (Walmart, Safeway, etc.)
- Crowd-sourced item location data
- Integration with grocery store apps
- Voice navigation support
- Shopping time estimates

## Architecture

The application is modular with the following components:

- `app.py`: Main application GUI and logic
- `store_finder.py`: Locates nearby stores
- `store_scraper.py`: Finds item locations within stores
- `route_optimizer.py`: Calculates optimal shopping paths
- `gui_components.py`: Reusable GUI widgets

## Development Notes

This proof of concept demonstrates the core functionality needed for a grocery route optimization app. The modular design allows for easy extension and adaptation to mobile platforms using frameworks like Kivy or React Native.

For production use, consider:
- Implementing proper API authentication
- Adding offline mode support
- Enhancing error handling
- Adding user accounts and saved lists
- Implementing real-time store inventory checks