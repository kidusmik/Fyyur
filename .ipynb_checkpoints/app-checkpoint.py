#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
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

# TODO: connect to a local postgresql database

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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []

    # populate all rows with distinct city and state combinations
    unique_areas = db.session.query(Venue).distinct(Venue.city, Venue.state).all()
    for unique_area in unique_areas:
        area = {}
        area['city'] = unique_area.city
        area['state'] = unique_area.state
        area['venues'] = Venue.query.filter_by(city=unique_area.city, state=unique_area.state).all()
        data.append(area)
        
        for venue in area['venues']:
            venue.num_upcoming_shows = len(venue.upcoming_shows)
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
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
  # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    venue.past_shows_count = len(venue.past_shows)
    venue.upcoming_shows_count = len(venue.upcoming_shows)

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()

    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    error = False
    form = VenueForm(request.form)
    
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
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    #return render_template('pages/home.html')
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
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
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    
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
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    artist.past_shows_count = len(artist.past_shows)
    artist.upcoming_shows_count = len(artist.upcoming_shows)

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    # modified form since Artist table uses 'website' instead of 'website_link'
    form.website_link.data = artist.website

  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    
    error = False
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

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
    # modified form since Venue table uses 'website' instead of 'website_link'
    form.website_link.data = venue.website
    
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)

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
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    form = ArtistForm(request.form)

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
        # on successful db insert, flash success
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

    return render_template('pages/shows.html', shows=Show.query.all())

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    error = False
    form = ShowForm(request.form)
    
    try:
        venue = Venue.query.get(form.venue_id.data)
        artist = Artist.query.get(form.artist_id.data)
        show = Show(venue_id=form.venue_id.data,
                    artist_id=form.artist_id.data,
                    venue_name=venue.name,
                    artist_name=artist.name,
                    artist_image_link=artist.image_link,
                    venue_image_link=venue.image_link,
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
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
