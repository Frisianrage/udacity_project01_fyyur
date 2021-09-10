#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from types import CoroutineType
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from sqlalchemy import asc
from sqlalchemy.orm import backref
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
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
# Models.
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.with_entities(Venue, Venue.city, Venue.state).distinct(Venue.city)
  for venue in venues:
    venue_city = venue.city
    venue_state = venue.state
    entries = Venue.query.filter(Venue.city == venue.city).all()
    data.append({"city": venue_city, "state": venue_state, "venues": entries})
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  results = {
    "count":  0,
    "data": []
  }
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  
  for venue in venues:
    upcoming_shows = 0
    results['count'] += 1
    for show in venue.shows:
      if show.start_time.strftime('%Y-%m-%d %H:%M:%S') > now:
        upcoming_shows += 1

    results['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcoming_shows
    })
  
  return render_template('pages/search_venues.html', results=results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  past_shows = []
  upcoming_shows = []
  data = Venue.query.get(venue_id)

  for show in data.shows:
    if show.start_time.strftime('%Y-%m-%d %H:%M:%S') > now:
      upcoming_shows.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
    else:
      past_shows.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  data.upcoming_shows_count = len(upcoming_shows)
  data.past_shows_count = len(past_shows)
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
 
  venue_data = VenueForm(request.form)

  try:

    new_venue = Venue(
      name = venue_data.name.data,
      city = venue_data.city.data,
      state = venue_data.state.data,
      address = venue_data.address.data,
      phone = venue_data.phone.data,
      genres = venue_data.genres.data,
      image_link = venue_data.image_link.data,
      website_link = venue_data.website_link.data,
      facebook_link = venue_data.facebook_link.data,
      seeking_talent = venue_data.seeking_talent.data,
      seeking_description = venue_data.seeking_description.data
    )

    db.session.add(new_venue)
    db.session.commit()

    flash('Venue ' + venue_data.name.data + ' was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + venue_data.name.data + ' could not be listed.')
  # TODO: modify data to be the data object returned from db insertion

  finally:
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['POST', 'DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
 
  try:
        delete_venue = Venue.query.get(venue_id) 
        db.session.delete(delete_venue)
        db.session.commit()
        flash('Venue successfully deleted!')

  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Something went wrong! Venue is not deleted!')
  
  finally:
        db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  results = {
    "count":  0,
    "data": []
  }
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  
  for artist in artists:
    upcoming_shows = 0
    results['count'] += 1
    for show in artist.shows:
      if show.start_time.strftime('%Y-%m-%d %H:%M:%S') > now:
        upcoming_shows += 1

    results['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": upcoming_shows
    })

  return render_template('pages/search_artists.html', results=results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  past_shows = []
  upcoming_shows = []
  data = Artist.query.get(artist_id)

  for show in data.shows:
    if show.start_time.strftime('%Y-%m-%d %H:%M:%S') > now:
      upcoming_shows.append({
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
    else:
      past_shows.append({
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  data.upcoming_shows_count = len(upcoming_shows)
  data.past_shows_count = len(past_shows)
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  form_data = ArtistForm(request.form)
  
  artist = Artist.query.get(artist_id)

  try:
    artist.name = form_data.name.data
    artist.city = form_data.city.data
    artist.state = form_data.state.data
    artist.phone = form_data.phone.data
    artist.genres = form_data.genres.data
    artist.image_link = form_data.image_link.data
    artist.website_link = form_data.website_link.data
    artist.facebook_link = form_data.facebook_link.data
    artist.seeking_venue = form_data.seeking_venue.data
    artist.seeking_description = form_data.seeking_description.data

    db.session.commit()

  except:
    print(sys.exc_info()) 
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form_data = VenueForm(request.form)
  
  venue = Venue.query.get(venue_id)

  try:
    venue.name = form_data.name.data
    venue.city = form_data.city.data
    venue.state = form_data.state.data
    venue.address = form_data.address.data
    venue.phone = form_data.phone.data
    venue.genres = form_data.genres.data
    venue.image_link = form_data.image_link.data
    venue.website_link = form_data.website_link.data
    venue.facebook_link = form_data.facebook_link.data
    venue.seeking_talent = form_data.seeking_talent.data
    venue.seeking_description = form_data.seeking_description.data

    db.session.commit()

  except:
    print(sys.exc_info()) 
    db.session.rollback()

  finally:
    db.session.close()
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
  form_data = ArtistForm(request.form)

  try:

    new_artist = Artist(
      name = form_data.name.data,
      city = form_data.city.data,
      state = form_data.state.data,
      phone = form_data.phone.data,
      genres = form_data.genres.data,
      image_link = form_data.image_link.data,
      website_link = form_data.website_link.data,
      facebook_link = form_data.facebook_link.data,
      seeking_venue = form_data.seeking_venue.data,
      seeking_description = form_data.seeking_description.data
    )

    db.session.add(new_artist)
    db.session.commit()

  # on successful db insert, flash success
    flash('Artist ' + form_data.name.data + ' was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Artist ' + form_data.name.data + ' could not be listed.')
 
  finally:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form_data = ShowForm(request.form)
  try:

    new_show = Show(
      artist_id = form_data.artist_id.data,
      venue_id = form_data.venue_id.data,
      start_time = form_data.start_time.data
    )

    db.session.add(new_show)
    db.session.commit()
    
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')

  finally:
    return render_template('pages/home.html')

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
