import calendar as calendar_module
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo


def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def local_now():
    return datetime.now(timezone.utc).astimezone(LOCAL_TIMEZONE)


def local_datetime_to_utc_naive(value):
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def utc_naive_to_local_date(value):
    return value.replace(tzinfo=timezone.utc).astimezone(LOCAL_TIMEZONE).date()

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Topic Model (Represents a distinct study unit/chapter) - creates one table: topic in the database
class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)       # e.g., "Physics"
    title = db.Column(db.String(150), nullable=False)         # e.g., "Newtonian Mechanics"
    interval = db.Column(db.Integer, default=0)               # Days until next review
    repetition = db.Column(db.Integer, default=0)             # Successful review streak
    ease_factor = db.Column(db.Float, default=2.5)            # Interval multiplier
    due_date = db.Column(db.DateTime, default=utc_now_naive) # When it should appear on the to-do list

    # Relationship to Review model: delete-orphan ensures that if a Topic is deleted, its associated Reviews are also deleted.
    reviews = db.relationship('Review', back_populates='topic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Topic {self.subject}: {self.title}>'

    def review(self, grade, reviewed_at=None):
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
        review_start = reviewed_at or utc_now_naive()
        self.due_date = review_start + timedelta(days=self.interval)

# Review Database  - creates one table: reviews in the database
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    reviewed_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)

    topic = db.relationship('Topic', back_populates='reviews')

# Initialize tables
with app.app_context():
    db.create_all()

# MAIN PAGE - Displays topics due for review today, sorted by due date
@app.route('/')
def index():
    # Include overdue topics so missed reviews remain in the queue.
    today = local_now()
    due_topics = Topic.query.filter(
        Topic.due_date <= utc_now_naive()
    ).order_by(
        Topic.due_date.asc()
    ).all()

    today_date = today.date()
    # 1. Expand the range to a full year (52 weeks = 364 days) like GitHub
    total_weeks = 52
    total_days = total_weeks * 7
    heatmap_start = today_date - timedelta(
        days=today_date.weekday() + ((total_weeks - 1) * 7)
    )
    
    heatmap_range_start = datetime.combine(
        heatmap_start, datetime.min.time(), tzinfo=LOCAL_TIMEZONE
    )
    heatmap_range_end = datetime.combine(
        today_date + timedelta(days=1), datetime.min.time(), tzinfo=LOCAL_TIMEZONE
    )
    
    heatmap_start_utc = local_datetime_to_utc_naive(heatmap_range_start)
    heatmap_end_utc = local_datetime_to_utc_naive(heatmap_range_end)

    planned_topics = Topic.query.filter(
        Topic.due_date >= heatmap_start_utc,
        Topic.due_date < heatmap_end_utc,
    ).all()
    completed_reviews = Review.query.filter(
        Review.reviewed_at >= heatmap_start_utc,
        Review.reviewed_at < heatmap_end_utc,
    ).all()

    planned_by_date = defaultdict(int)
    completed_by_date = defaultdict(int)
    for topic in planned_topics:
        planned_by_date[utc_naive_to_local_date(topic.due_date)] += 1
    for review in completed_reviews:
        completed_by_date[utc_naive_to_local_date(review.reviewed_at)] += 1

    heatmap_days = []
    for offset in range(total_days):
        current_date = heatmap_start + timedelta(days=offset)
        planned = planned_by_date[current_date]
        completed = completed_by_date[current_date]
        
        # 2. Maintain your exact task-completion status logic
        if planned and completed >= planned:
            level = 'complete'
        elif planned and completed:
            level = 'partial'
        elif planned:
            level = 'missed'
        elif completed:
            level = 'complete'
        else:
            level = 'empty'
            
        heatmap_days.append({
            'date': current_date,
            'planned': planned,
            'completed': completed,
            'level': level,
        })

    # 3. Chunk into 52 columns of 7 days each
    heatmap_weeks = [heatmap_days[index:index + 7] for index in range(0, total_days, 7)]
    
    return render_template(
        'index.html',
        due_topics=due_topics,
        today=today,
        heatmap_weeks=heatmap_weeks,
    )




# When user submits a review for a topic, this route processes the review and updates the topic's spaced repetition data accordingly.
@app.post('/topics/<int:topic_id>/review')
def review_topic(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    try:
        grade = int(request.form.get('grade', ''))
    except ValueError:
        abort(400, description='A valid review grade is required.')

    if grade not in {1, 3, 5}:
        abort(400, description='Review grade must be 1, 3, or 5.')

    review_date = request.form.get('review_date', '').strip()
    if review_date:
        try:
            selected_date = date.fromisoformat(review_date)
        except ValueError:
            abort(400, description='A valid review date is required.')
        selected_datetime = datetime.combine(
            selected_date, datetime.min.time(), tzinfo=LOCAL_TIMEZONE
        )
        reviewed_at = local_datetime_to_utc_naive(selected_datetime)
    else:
        reviewed_at = utc_now_naive()

    topic.review(grade, reviewed_at=reviewed_at)
    db.session.add(Review(topic=topic, grade=grade, reviewed_at=reviewed_at))
    db.session.commit()
    if request.form.get('return_to') == 'calendar':
        return redirect(url_for('calendar_view'))
    return redirect(url_for('index'))


@app.post('/topics/<int:topic_id>/reschedule')
def reschedule_topic(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    target_date = request.form.get('target_date', '').strip()
    try:
        selected_date = date.fromisoformat(target_date)
    except ValueError:
        abort(400, description='A valid target date is required.')

    selected_datetime = datetime.combine(
        selected_date, datetime.min.time(), tzinfo=LOCAL_TIMEZONE
    )
    topic.due_date = local_datetime_to_utc_naive(selected_datetime)
    db.session.commit()
    return jsonify(success=True, target_date=target_date)

# CALENDAR VIEW - Displays a monthly calendar with due topics and reviews
@app.route('/calendar')
def calendar_view():
    # Determine the month and year to display, defaulting to the current month if not specified in query parameters.
    today = local_now().date()
    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
        month_start = date(year, month, 1)
    except (TypeError, ValueError):
        abort(400, description='Invalid calendar month.')

    # Calculate the last day of the month and define the date range for querying due topics and reviews.
    month_end = date(
        year, month, calendar_module.monthrange(year, month)[1]
    )
    local_range_start = datetime.combine(
        month_start, datetime.min.time(), tzinfo=LOCAL_TIMEZONE
    )
    local_range_end = datetime.combine(
        month_end + timedelta(days=1), datetime.min.time(), tzinfo=LOCAL_TIMEZONE
    )
    range_start = local_datetime_to_utc_naive(local_range_start)
    range_end = local_datetime_to_utc_naive(local_range_end)

    # Query the database for topics due within the specified month and reviews conducted within the same range, ordering both by their respective dates.
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
        due_by_date[utc_naive_to_local_date(topic.due_date)].append(topic)

    reviews_by_date = defaultdict(list)
    for review in reviews:
        reviews_by_date[utc_naive_to_local_date(review.reviewed_at)].append(review)

    # Generate the calendar structure for the specified month, creating a list of weeks, each containing a list of days (with None for days outside the current month).
    weeks = []
    for week in calendar_module.monthcalendar(year, month):
        days = []
        for day_number in week:
            day = date(year, month, day_number) if day_number else None
            days.append(day)
        weeks.append(days)

    previous_month = month_start - timedelta(days=1)
    next_month = month_end + timedelta(days=1)
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    
    return render_template(
        'calendar.html',
        month_name=month_start.strftime('%B %Y'),
        weeks=weeks,
        today=today,
        due_by_date=due_by_date,
        reviews_by_date=reviews_by_date,
        current_week_start=current_week_start,
        current_week_end=current_week_end,
        previous_month=previous_month,
        next_month=next_month,
    )


@app.route('/calendar/day/<selected_date>')
def calendar_day_view(selected_date):
    try:
        selected_day = date.fromisoformat(selected_date)
    except ValueError:
        abort(400, description='Invalid calendar day.')

    local_range_start = datetime.combine(
        selected_day, datetime.min.time(), tzinfo=LOCAL_TIMEZONE
    )
    local_range_end = local_range_start + timedelta(days=1)
    range_start = local_datetime_to_utc_naive(local_range_start)
    range_end = local_datetime_to_utc_naive(local_range_end)

    due_topics = Topic.query.filter(
        Topic.due_date >= range_start,
        Topic.due_date < range_end,
    ).order_by(Topic.due_date.asc()).all()
    reviews = Review.query.filter(
        Review.reviewed_at >= range_start,
        Review.reviewed_at < range_end,
    ).order_by(Review.reviewed_at.asc()).all()

    return render_template(
        'calendar_day.html',
        selected_day=selected_day,
        due_topics=due_topics,
        reviews=reviews,
    )

if __name__ == '__main__':
    app.run(debug=True)