# Toronto Weekend Activity Finder - Project Specification

## Project Overview
A Python-based web application that helps users discover activities and events in the Greater Toronto Area (GTA) by searching multiple leisure websites and aggregating results in a user-friendly interface.

## Application Architecture

### 1. Frontend (Web Interface)
**Technology Stack:**
- Python web framework (Flask or Django)
- HTML5/CSS3
- JavaScript for interactive elements
- Responsive design for mobile and desktop

**UI Components:**
- **Background:** Toronto downtown skyline scenery image
- **Search Interface:**
  - Text input box for activity queries (e.g., "outdoor activities", "museums", "restaurants")
  - Date picker field for activity date selection
  - Search button
- **Results Display:**
  - Activity cards showing:
    - Activity title
    - Description
    - Date/time information
    - Related images/photos
    - Source URL reference (clickable link)
  - Organized in a grid or list layout
  - Responsive image gallery

### 2. Middle Tier (Search & Aggregation Service)
**Responsibilities:**
- Accept user input (search query + date)
- Orchestrate searches across multiple sources
- Parse and normalize data from different websites
- Aggregate and deduplicate results
- Return structured data to frontend

**Technology:**
- Python backend service
- Web scraping libraries (BeautifulSoup4, Scrapy, or Selenium)
- HTTP client (requests library)
- Data processing and filtering logic

**Search Sources:**
1. **Primary:** Toronto.com
2. **Additional Leisure Websites:**
   - BlogTO
   - Narcity Toronto
   - Tourism Toronto (SeeTorontoNow.com)
   - Eventbrite (Toronto events)
   - Now Toronto
   - Toronto Life
   - Toronto Star events section

### 3. Backend (Data Processing)
**Components:**
- **Search Engine:** Coordinates queries to multiple sources
- **Web Scraper:** Extracts activity information from target websites
- **Data Parser:** Normalizes data from different formats
- **Image Handler:** Retrieves and caches activity images
- **Cache Layer:** Stores recent search results (optional, using Redis or in-memory cache)

## Functional Requirements

### FR1: User Input
- Users can enter free-form text queries about activities
- Users can select a specific date or date range
- Support for common query types:
  - Activity categories (food, entertainment, sports, arts)
  - Keywords (free, outdoor, family-friendly, romantic)
  - Location refinements (downtown, North York, Scarborough)

### FR2: Search Functionality
- Search across multiple predefined websites
- Filter results by selected date
- Return relevant activities matching user query
- Handle various search result formats from different sources

### FR3: Results Display
- Display activity cards with:
  - **Title:** Name of the activity/event
  - **Description:** Brief overview (2-3 sentences)
  - **Date/Time:** When the activity occurs
  - **Images:** Representative photos (at least 1 per activity)
  - **Source Link:** URL to original listing
  - **Location:** Venue or area in GTA (if available)
- Paginated results (10-20 activities per page)
- Sort options (by date, relevance)

### FR4: Error Handling
- Graceful handling of website unavailability
- Display message when no results found
- Timeout handling for slow-responding websites
- User-friendly error messages

## Non-Functional Requirements

### NFR1: Performance
- Search results displayed within 5-10 seconds
- Concurrent requests to multiple websites
- Image loading optimization (lazy loading)
- Caching of common queries

### NFR2: Usability
- Clean, intuitive interface
- Mobile-responsive design
- Accessible color contrast and font sizes
- Clear visual hierarchy

### NFR3: Reliability
- Handle website structure changes gracefully
- Fallback to available sources if some fail
- Regular testing of web scrapers

### NFR4: Compliance
- Respect robots.txt files
- Implement rate limiting for web requests
- Include proper attribution to source websites
- Terms of service compliance for scraped websites

## Data Model

### Activity Object
```python
{
    "id": "unique_identifier",
    "title": "Activity Name",
    "description": "Detailed description of the activity",
    "date": "YYYY-MM-DD",
    "time": "HH:MM" (optional),
    "location": "Venue/Area",
    "images": ["url1", "url2", ...],
    "source_url": "https://original-listing-url",
    "source_site": "Toronto.com",
    "category": "Entertainment/Food/Sports/etc",
    "price": "Free/Paid/Price Range" (optional)
}
```

## User Stories

### US1: Basic Activity Search
**As a** user  
**I want to** search for activities in Toronto  
**So that** I can find something interesting to do

**Acceptance Criteria:**
- User enters a query like "museums"
- System displays relevant museum activities
- Each result shows description and link

### US2: Date-Specific Search
**As a** user  
**I want to** filter activities by date  
**So that** I can find activities available on a specific day

**Acceptance Criteria:**
- User selects a date from date picker
- System returns only activities available on that date
- Results clearly show date/time information

### US3: Browse Activity Details
**As a** user  
**I want to** view detailed information about an activity  
**So that** I can decide if I'm interested

**Acceptance Criteria:**
- Each activity card displays complete information
- Images are clearly visible
- Source URL is clickable and opens in new tab

## Technical Implementation

### Phase 1: MVP (Minimum Viable Product)
1. Basic Flask/Django web application
2. Simple search form (text + date)
3. Web scraper for Toronto.com
4. Basic results display
5. Static Toronto skyline background

### Phase 2: Enhancement
1. Add additional website sources
2. Implement caching layer
3. Improve UI/UX with CSS framework (Bootstrap/Tailwind)
4. Add image optimization
5. Implement error handling and logging

### Phase 3: Advanced Features
1. User preferences and saved searches
2. Email notifications for new activities
3. Interactive map integration
4. Social sharing features
5. Advanced filtering (price, category, distance)

## Technology Stack

**Frontend:**
- Flask or Django (Python web framework)
- Jinja2 templates
- Bootstrap 5 or Tailwind CSS
- JavaScript (vanilla or lightweight library)

**Backend:**
- Python 3.9+
- BeautifulSoup4 or Scrapy (web scraping)
- Requests library
- Optional: Selenium for JavaScript-heavy sites

**Data Storage:**
- Optional: SQLite or PostgreSQL for caching
- Optional: Redis for session storage

**Deployment:**
- Development: Local Flask development server
- Production: Gunicorn/uWSGI + Nginx
- Platform: Heroku, AWS, Azure, or DigitalOcean

## Security Considerations
- Input validation and sanitization
- Rate limiting to prevent abuse
- HTTPS for production deployment
- Secure handling of external URLs
- CORS configuration

## Testing Strategy
- Unit tests for scraping functions
- Integration tests for search workflow
- Manual testing of UI components
- Regular monitoring of source websites for structure changes

## Maintenance
- Monthly review of web scrapers
- Update selectors if website structures change
- Monitor error logs for issues
- Performance optimization based on usage patterns

## Success Metrics
- Search completion rate
- Average response time
- Number of successful results per query
- User engagement (click-through rate to source URLs)

## Future Enhancements
- Machine learning for better result ranking
- Natural language processing for query understanding
- User accounts and personalization
- Mobile app version
- Integration with ticketing platforms
- Real-time event availability checking
