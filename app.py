from datetime import datetime, timedelta
from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Topic Model (Represents a distinct study unit/chapter)
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)       # e.g., "Physics"
    title = db.Column(db.String(150), nullable=False)         # e.g., "Newtonian Mechanics"
    
    # Spaced Repetition tracking fields for the topic
    interval = db.Column(db.Integer, default=0)               # Days until next review
    repetition = db.Column(db.Integer, default=0)             # Successful review streak
    ease_factor = db.Column(db.Float, default=2.5)            # Interval multiplier
    due_date = db.Column(db.DateTime, default=datetime.utcnow) # When it should appear on the to-do list

    def __repr__(self):
        return f'<Topic {self.subject}: {self.title}>'

    def review(self):
        """Schedule the next review using a small SM-2-style progression."""
        self.repetition += 1
        if self.repetition == 1:
            self.interval = 1
        elif self.repetition == 2:
            self.interval = 3
        else:
            self.interval = max(1, round(self.interval * self.ease_factor))
        self.due_date = datetime.utcnow() + timedelta(days=self.interval)

# Initialize tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Fetch all topics due today or overdue, grouped in database order.
    today = datetime.utcnow()
    due_topics = Topic.query.filter(Topic.due_date <= today).order_by(
        Topic.subject, Topic.title
    ).all()
    return render_template('index.html', due_topics=due_topics, today=today)


@app.post('/topics/<int:topic_id>/review')
def review_topic(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    topic.review()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
