# 📚 Study Planner - Smart Curriculum System
#### Description:

A web-based study planner application that helps students organize and track their study schedule using a scientifically-proven Spaced Repetition System (SM-2 algorithm inspired by Anki). 

## ✨ Features

### 🎯 Smart Study Dashboard
- **Today's Review Plan**: Automatically displays topics due for review, sorted by priority
- **Study Consistency Heatmap**: Visual calendar tracking your study streaks over time
- **Live Clock**: Real-time display of current time
- **Smart Recommendations**: Uses SM-2 algorithm to optimize review intervals

### 📖 Topic Library
- **Browse All Topics**: View all available study topics organized by subject
- **Flexible Scheduling**: Add topics to your queue with specific due dates
- **Easy Addition**: One-click process to add new topics from the library

### 📅 Calendar Views
- **Monthly Overview**: See your entire month's study schedule at a glance
- **Daily Detail**: Click any day to see all planned reviews and past history
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 🔬 Spaced Repetition Algorithm (SM-2)
The app implements the Leitner System's SM-2 algorithm:
- **Grade "Again" (1)**: Reset review interval to 1 day
- **Grade "Good" (3)**: Standard progress with ease factor adjustment
- **Grade "Easy" (5)**: Maximum ease factor, longest intervals

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | Flask (Python) |
| Database ORM | Flask-SQLAlchemy |
| Database | SQLite |
| Frontend Templating | Jinja2 |
| Styling | CSS3 with Flexbox/Grid |
| Interactivity | JavaScript/jQuery |

## 📁 Project Structure

```
Study Planner/
├── app.py            # Main Flask application
├── seed.py                # Database seeding script
├── reset_database.py      # Clears Tables in Database
├── delete_database_row.py # Clears specific row in Database
├── topics.json            # Topic catalog configuration
├── requirements.txt       # Python dependencies
├── instance/              # SQLite database storage
├── static/                # Frontend assets
│   ├── style.css          # Stylesheet
│   └── script.js          # JavaScript functionality
├── templates/             # HTML templates
│   ├── layout.html        # Base template
│   ├── index.html         # Dashboard/Home view
│   ├── library.html       # Topic library view
│   ├── calendar.html      # Monthly calendar view
│   └── calendar_day.html  # Daily detail view
└── README.md            # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation for MacOS
For other OS, do search up relevant syntax of the commands below.

1. **Navigate to the project directory:**
   ```bash
   cd Study\ Planner/
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and visit:**
   ```
   http://localhost:5000
   ```

### Adding Topics

1. Navigate to the **Topic Library** page (`/library`)
2. Select a subject from the available categories
3. Choose a due date using the date picker
4. Click **"Add to Queue"** to add the topic to your study schedule

## 💾 Database

The application uses SQLite for data persistence:
- **Location**: `instance/study_app.db`
- **SQL Tables**:
  - `Topics`: Study units with subject, title, review interval, repetition count, ease factor, and due date
  - `Reviews`: Individual review sessions tracking grade and timestamp
- **Database Management**
  - `delete_database_row.py`: Edit the table id > `topic = db.session.get(Topic, 4)` where 4 is the id from the topics table
  - `reset_database.py`: Complete clears database without deleting table when run


## 🔧 Loading large data files (topics)

### topics.json
Edit this file to customize your study catalog. Each entry should have:
```json
{
  "subject": "Physics",
  "title": "Newtonian Mechanics"
}
```

To load custom topics into the database:
```bash
python seed.py
```

## 📊 Using the Spaced Repetition System

When reviewing a topic, you'll rate your performance:

| Grade | Meaning | Effect |
|-------|---------|--------|
| **1 - Again** | I struggled to recall this | Reset to day 1 |
| **3 - Good** | I recalled it with some effort | Standard interval progression |
| **5 - Easy** | I knew it immediately | Extended interval, increased ease factor |

The algorithm adapts based on your performance, creating an optimal review schedule.

## 🔍 Website Routes

| Route | Description |
|-------|-------------|
| `/` | Dashboard - Today's study plan |
| `/library` | Topic library - Browse all subjects |
| `/add-to-queue` | Add a topic to the review queue |
| `/calendar` | Monthly calendar view |
| `/calendar/day/<date>` | Daily detail view |

## 📝 Usage Tips

1. **Plan Ahead**: Review the Topic Library weekly to add upcoming study topics
2. **Consistency is Key**: The heatmap tracks your streaks - try to maintain them!
3. **Honest Grading**: Rate reviews honestly for optimal spacing recommendations
4. **Mobile Friendly**: Access your study plan from anywhere with a web browser

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No topics appear in dashboard | Add topics via the Library page |
| Database errors | Check `instance/` folder permissions |
| Topics don't load | Run `python seed.py` to populate from topics.json |
| Blank calendar | Ensure due dates are properly set in database |

## 📄 License

This project is made as part of my CS50 Final Project only.

---

Built with ❤️ using Flask and the SM-2 Spaced Repetition Algorithm.
