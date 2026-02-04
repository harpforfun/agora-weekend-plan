# Toronto Weekend Activity Finder

A Python-based web application that helps users discover activities and events in the Greater Toronto Area (GTA).

## Features

- 🔍 Search for activities by keyword
- 📅 Optional date filtering
- 🏙️ Beautiful Toronto skyline background
- 📱 Responsive design for all devices
- 🔗 Direct links to activity sources

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter your search query (e.g., "museums", "outdoor activities", "restaurants")
2. Optionally select a date
3. Click "Search Activities"
4. Browse the results and click "View Details" to visit the source website

## Project Structure

```
Agora/
├── app.py              # Flask application
├── scraper.py          # Web scraping logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main HTML template
└── static/
    ├── css/
    │   └── style.css  # Styling
    └── images/        # Static images
```

## User Stories

- ✅ US1: Basic Activity Search - Users can search for activities and view results
- ⏳ US2: Date-Specific Search - Coming soon
- ⏳ US3: Browse Activity Details - Coming soon

## Development

The application uses:
- **Flask** - Web framework
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP client

## Notes

- Currently uses sample data when Toronto.com scraping encounters issues
- No database - all searches are performed in real-time
- Rate limiting and robots.txt compliance included

## Future Enhancements

- Add more activity sources (BlogTO, Narcity, etc.)
- Implement caching for improved performance
- Add user preferences and saved searches
- Enhanced filtering by price, category, and distance