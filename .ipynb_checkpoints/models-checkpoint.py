from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    past_shows_count = db.Column(db.Integer, nullable=False, default=0)
    upcoming_shows_count = db.Column(db.Integer, nullable=False, default=0)
    num_upcoming_shows = db.Column(db.Integer, nullable=False, default=0)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    upcoming_shows = db.relationship('Show', primaryjoin="and_(Venue.id==Show.venue_id, "
                                     "Show.start_time >= func.now())", cascade="all,delete", lazy=True)
    past_shows = db.relationship('Show', primaryjoin="and_(Venue.id==Show.venue_id, "
                                     "Show.start_time < func.now())", cascade="all,delete", lazy=True)
    
    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    past_shows_count = db.Column(db.Integer, nullable=False, default=0)
    upcoming_shows_count = db.Column(db.Integer, nullable=False, default=0)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    shows = db.relationship('Show', backref='artist', lazy=True)
    upcoming_shows = db.relationship('Show', primaryjoin="and_(Artist.id==Show.artist_id, "
                                     "Show.start_time >= func.now())", cascade="all,delete", lazy=True)
    past_shows = db.relationship('Show', primaryjoin="and_(Artist.id==Show.artist_id, "
                                     "Show.start_time < func.now())", cascade="all,delete", lazy=True)
    
    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_name = db.Column(db.String, nullable=False)
    artist_name = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_image_link = db.Column(db.String(500), nullable=False)
    artist_image_link = db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<id: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}>'