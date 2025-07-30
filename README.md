# Grocery Route Optimizer (Proof of Concept)

This is a Python proof-of-concept that calculates an optimized in-store route for a grocery list (starting with Kroger stores).

## 1. Quick Start

```bash
# 1. Clone repository (already done if you are reading this)

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Environment Variables
Create a `.env` file in the project root (or export in your shell) with the following keys:

```
KROGER_API_KEY=your_kroger_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here  # optional, for geocoding
```

The application will automatically load these via `python-dotenv`.

## 3. Next Steps
* Run `python main.py --help` (to be implemented) to explore commands.
* Follow the project TODO board for upcoming features.

---

© 2025 Grocery Route Optimizer