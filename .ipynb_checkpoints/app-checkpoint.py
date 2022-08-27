#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    # I took this if else statement from the accepted answer of:
    #    https://stackoverflow.com/questions/63269150/typeerror-parser-must-be-a-string-or-character-stream-not-datetime
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    
    return render_template('pages/home.html', recent_venues=recent_venues, recent_artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    # populate all rows with distinct city and state combinations
    unique_areas = db.session.query(Venue).distinct(Venue.city, Venue.state).all()
    
    for unique_area in unique_areas:
        area = {}
        venues = Venue.query.filter_by(city=unique_area.city, state=unique_area.state).all()
        area['city'] = unique_area.city
        area['state'] = unique_area.state
        area['venues'] = []
        
        for venue in venues:
            venue_temp = {}
            venue_temp['id'] = venue.id
            venue_temp['name'] = venue.name
            venue_temp['num_upcoming_shows'] = len(Show.query.join(Venue).filter(Show.venue_id==Venue.id).filter(Show.start_time>datetime.now()).all())
            area['venues'].append(venue_temp)
            
        data.append(area)
        
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form['search_term']
    search_query = '%{0}%'.format(search_term)
    venues = Venue.query.filter(Venue.name.ilike(search_query)).all()

    response = {
        "count": len(venues),
        "data": venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    upcoming_shows_query = Show.query.join(Artist).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
    past_shows_query = Show.query.join(Artist).filter(Show.venue_id==venue.id).filter(Show.start_time<=datetime.now()).all()
    data={
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(past_shows_query),
    "upcoming_shows_count": len(upcoming_shows_query)
  }
    
    for past_shows in past_shows_query:
        past_shows_temp = {}
        past_shows_temp['artist_id'] = past_shows.artist_id
        past_shows_temp['artist_name'] = past_shows.artist.name
        past_shows_temp['start_time'] = past_shows.start_time
        past_shows_temp['artist_image_link'] = past_shows.artist.image_link

        data['past_shows'].append(past_shows_temp)

    for upcoming_shows in upcoming_shows_query:
        upcoming_shows_temp = {}
        upcoming_shows_temp['artist_id'] = upcoming_shows.artist_id
        upcoming_shows_temp['artist_name'] = upcoming_shows.artist.name
        upcoming_shows_temp['start_time'] = upcoming_shows.start_time
        upcoming_shows_temp['artist_image_link'] = upcoming_shows.artist.image_link
        upcoming_shows_temp['artist_name'] = upcoming_shows.artist.name
        
        data['upcoming_shows'].append(upcoming_shows_temp)
        
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()

    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm(request.form)
    if not form.validate():
        flash('Please make sure that Phone number format is xxx-xxx-xxxx and Links start with http://')
        return render_template('forms/new_venue.html', form=form)

    try:
        venue = Venue(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      address=form.address.data,
                      genres =form.genres.data,
                      phone=form.phone.data,
                      image_link=form.image_link.data,
                      facebook_link=form.facebook_link.data,
                      website=form.website_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data)
        
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        
        if error:
            flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
        else:
            flash('Venue ' + form.name.data + ' was successfully listed!')

    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record.
    error = False
    try:
        venue = db.session.query(Venue).get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
    else:
        flash('Venue was successfully deleted!')

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    
    return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form['search_term']
    search_query = '%{0}%'.format(search_term)
    artists = Artist.query.filter(Artist.name.ilike(search_query)).all()

    response = {
        "count": len(artists),
        "data": artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    upcoming_shows_query = Show.query.join(Venue).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all()
    past_shows_query = Show.query.join(Venue).filter(Show.artist_id==artist.id).filter(Show.start_time<=datetime.now()).all()
    data={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(past_shows_query),
    "upcoming_shows_count": len(upcoming_shows_query)
  }
    
    for past_shows in past_shows_query:
        past_shows_temp = {}
        past_shows_temp['venue_id'] = past_shows.venue_id
        past_shows_temp['venue_name'] = past_shows.venue.name
        past_shows_temp['start_time'] = past_shows.start_time
        past_shows_temp['venue_image_link'] = past_shows.venue.image_link

        data['past_shows'].append(past_shows_temp)

    for upcoming_shows in upcoming_shows_query:
        upcoming_shows_temp = {}
        upcoming_shows_temp['venue_id'] = upcoming_shows.venue_id
        upcoming_shows_temp['venue_name'] = upcoming_shows.venue.name
        upcoming_shows_temp['start_time'] = upcoming_shows.start_time
        upcoming_shows_temp['venue_image_link'] = upcoming_shows.venue.image_link
        upcoming_shows_temp['venue_name'] = upcoming_shows.venue.name
        
        data['upcoming_shows'].append(upcoming_shows_temp)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    # modified form since Artist table uses attribute 'website' instead of 'website_link'
    form.website_link.data = artist.website

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
    error = False
    form = ArtistForm(request.form)
    artist = db.session.query(Artist).get(artist_id)
    if not form.validate():
        flash('Please make sure that Phone number format is xxx-xxx-xxxx and Links start with http://')
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    try:
        artist.name=form.name.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.genres=form.genres.data
        artist.image_link=form.image_link.data
        artist.facebook_link=form.facebook_link.data
        artist.website=form.website_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
                        
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
    else:
        flash('Artist ' + form.name.data + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    # modified form since Venue table uses attribute 'website' instead of 'website_link'
    form.website_link.data = venue.website
    
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    error = False
    form = VenueForm(request.form)
    venue = db.session.query(Venue).get(venue_id)
    if not form.validate():
        flash('Please make sure that Phone number format is xxx-xxx-xxxx and Links start with http://')
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    try:
        venue.name=form.name.data
        venue.city=form.city.data
        venue.state=form.state.data
        venue.phone=form.phone.data
        venue.genres=form.genres.data
        venue.image_link=form.image_link.data
        venue.facebook_link=form.facebook_link.data
        venue.website=form.website_link.data
        venue.seeking_talent=form.seeking_talent.data
        venue.seeking_description=form.seeking_description.data
                        
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    else:
        flash('Venue ' + form.name.data + ' was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    form = ArtistForm(request.form)
    if not form.validate():
        flash('Please make sure that Phone number format is xxx-xxx-xxxx and Links start with http://')
        return render_template('forms/new_artist.html', form=form)
    
    try:
        artist = Artist(name=form.name.data,
                        city=form.city.data,
                        state=form.state.data,
                        phone=form.phone.data,
                        genres =form.genres.data,
                        image_link=form.image_link.data,
                        facebook_link=form.facebook_link.data,
                        website=form.website_link.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data)
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    else:
        flash('Artist ' + form.name.data + ' was successfully listed!')

    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = Show.query.join(Artist).join(Venue).all()

    data = []
    for show in shows:
        show_temp = {}
        show_temp["venue_id"] = show.venue_id
        show_temp["venue_name"] = show.venue.name
        show_temp["artist_id"] = show.artist_id
        show_temp["artist_name"] = show.artist.name
        show_temp["artist_image_link"] = show.artist.image_link
        show_temp["start_time"] = show.start_time
        
        data.append(show_temp)

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
    error = False
    form = ShowForm(request.form)
    
    try:
        venue = Venue.query.get(form.venue_id.data)
        artist = Artist.query.get(form.artist_id.data)
        show = Show(venue_id=form.venue_id.data,
                    artist_id=form.artist_id.data,
                    start_time=form.start_time.data)
        
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=3000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
'''
