import calendar as calendar_module
from collections import defaultdict
from datetime import date, datetime, timedelta
from flask import Flask, abort, redirect, render_template, request, url_for
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
    reviews = db.relationship('Review', back_populates='topic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Topic {self.subject}: {self.title}>'

    def review(self, grade):
        """Apply an SM-2 review grade and schedule the next review."""
        if grade not in {1, 3, 5}:
            raise ValueError('grade must be 1, 3, or 5')

        quality_gap = 5 - grade
        self.ease_factor = max(
            1.3,
            self.ease_factor + 0.1 - quality_gap * (0.08 + quality_gap * 0.02),
        )

        if grade == 1:
            self.repetition = 0
            self.interval = 1
        elif self.repetition == 0:
            self.repetition = 1
            self.interval = 1
        elif self.repetition == 1:
            self.repetition = 2
            self.interval = 6
        else:
            self.interval = max(1, round(self.interval * self.ease_factor))

            self.repetition += 1
        self.due_date = datetime.utcnow() + timedelta(days=self.interval)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    topic = db.relationship('Topic', back_populates='reviews')

# Initialize tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Include overdue topics so missed reviews remain in the queue.
    today = datetime.utcnow()
    due_topics = Topic.query.filter(Topic.due_date <= today).order_by(
        Topic.due_date.asc()
    ).all()
    return render_template('index.html', due_topics=due_topics, today=today)


@app.route('/calendar')
def calendar_view():
    today = datetime.utcnow().date()
    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
        month_start = date(year, month, 1)
    except (TypeError, ValueError):
        abort(400, description='Invalid calendar month.')

    month_end = date(
        year, month, calendar_module.monthrange(year, month)[1]
    )
    range_start = datetime.combine(month_start, datetime.min.time())
    range_end = datetime.combine(month_end + timedelta(days=1), datetime.min.time())

    due_topics = Topic.query.filter(
        Topic.due_date >= range_start,
        Topic.due_date < range_end,
    ).order_by(Topic.due_date.asc()).all()
    reviews = Review.query.filter(
        Review.reviewed_at >= range_start,
        Review.reviewed_at < range_end,
    ).order_by(Review.reviewed_at.asc()).all()

    due_by_date = defaultdict(list)
    for topic in due_topics:
        due_by_date[topic.due_date.date()].append(topic)

    reviews_by_date = defaultdict(list)
    for review in reviews:
        reviews_by_date[review.reviewed_at.date()].append(review)

    weeks = []
    for week in calendar_module.monthcalendar(year, month):
        days = []
        for day_number in week:
            day = date(year, month, day_number) if day_number else None
            days.append(day)
        weeks.append(days)

    previous_month = month_start - timedelta(days=1)
    next_month = month_end + timedelta(days=1)
    return render_template(
        'calendar.html',
        month_name=month_start.strftime('%B %Y'),
        weeks=weeks,
        today=today,
        due_by_date=due_by_date,
        reviews_by_date=reviews_by_date,
        previous_month=previous_month,
        next_month=next_month,
    )


@app.post('/topics/<int:topic_id>/review')
def review_topic(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    try:
        grade = int(request.form.get('grade', ''))
    except ValueError:
        abort(400, description='A valid review grade is required.')

    if grade not in {1, 3, 5}:
        abort(400, description='Review grade must be 1, 3, or 5.')

    topic.review(grade)
    db.session.add(Review(topic=topic, grade=grade))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
