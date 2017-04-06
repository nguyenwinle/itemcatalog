import jinja2

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, forSale, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Saleslist Application"

engine = create_engine('sqlite:///users.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# creates a page that renders user's information
@app.route('/user/<username>/<email>')
def showUser(username, email):
    user = session.query(User).filter_by(name=username, email=email).one()
    return render_template('showuser.html', user=user)

# login for google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# creates new user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# get's users id from when logging in
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# get's users email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# logout for google
@app.route('/gdisconnect/')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        return redirect('/login')
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    return redirect('/')

# login for facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

# logout got facebook
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return redirect('/')

@app.route('/disconnect')
def disconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        return redirect('/login')
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    return redirect('/')

    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home'))


# json request for all the cities
@app.route('/cities/JSON')
def cityJSON():
    cities = session.query(City).all()
    return jsonify(cities=[city.serialize for city in cities])

# json request for city's items
@app.route('/city/<int:city_id>/forsale/JSON')
def cityItemsSON(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    items = session.query(forSale).filter_by(city_id=city_id).all()
    return jsonify(forSale=[i.serialize for i in items])

# json request for just one item
@app.route('/city/<int:city_id>/forsale/<int:item_id>/JSON')
def cityItemJSON(city_id, item_id):
    sale = session.query(forSale).filter_by(id=item_id).one()
    return jsonify(forSale=sale.serialize)

# homepage
@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html')

# about page
@app.route('/about/')
def about():
    return render_template('about.html')

# contact page
@app.route('/contact/')
def contact():
    return render_template('contact.html')

# 1. page that displays all the cities
@app.route('/cities/')
def city():
    cities = session.query(City).order_by(City.name).all()
    if 'username' not in login_session:
        return render_template('publiccities.html', cities=cities)
    else:
        return render_template('city.html', cities=cities)

# 2. page to add new city
@app.route('/city/new', methods=['GET', 'POST'])
def newCity():
    if 'username' not in login_session:
        return redirect('/login')
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    if request.method == 'POST':
        newCity = City(name=request.form['name'],
                       user_id=login_session['user_id'])
        session.add(newCity)
        flash("New city created!")
        session.commit()
        return redirect(url_for('city', cities=cities))
    else:
        return render_template('newcity.html')

# 3. page to edit the city
@app.route('/city/<int:city_id>/edit', methods=['GET', 'POST'])
def editCity(city_id):
    editedCity = session.query(City).filter_by(id=city_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedCity.name = request.form['name']
        session.add(editedCity)
        session.commit()
        flash("City updated!")
        return redirect(url_for('city', city_id=city_id))
    else:
        return render_template('editcity.html', editedCity = editedCity, city_id=city_id)

# 4. page to delete the city
@app.route('/city/<int:city_id>/delete', methods=['GET', 'POST'])
def deleteCity(city_id):
    CityToDelete = session.query(City).filter_by(id=city_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if CityToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not allowed to delete this city.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(CityToDelete)
        session.commit()
        flash("City has been deleted!")
        return redirect(url_for('city', cities=cities))

    else:
        return render_template('deletecity.html', CityToDelete=CityToDelete, city_id=city_id)

# 5. page to the city's items that are being sold
@app.route('/city/<int:city_id>/forsale')
def showItems(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    creator = getUserInfo(city.user_id)
    items = session.query(forSale).filter_by(city_id=city_id).all()
    if 'username' not in login_session:
        return render_template('publicitems.html', items=items, city=city, creator=creator)
    else:
        return render_template(
            'item.html', city=city, items=items, city_id=city_id, creator=creator)

# 6. page to add items for sale
@app.route('/forsale/<int:city_id>/new', methods=['GET', 'POST'])
def newItem(city_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        itemSale = forSale(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], contact=request.form['contact'],
                           category=request.form['category'], city_id=city_id, user_id=login_session['user_id'])
        session.add(itemSale)
        session.commit()
        flash("New item created!")
        return redirect(url_for('showItems', city_id=city_id))
    else:
        return render_template('newitem.html', city_id=city_id)

# 7. page to edit the item that is listed
@app.route('/forsale/<int:city_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(city_id, item_id):
    editedItem = session.query(forSale).filter_by(id=item_id).one()
    city = session.query(City).filter_by(id=city_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['contact']:
            editedItem.contact = request.form['contact']
        if request.form['category']:
            editedItem.category = request.form['category']
        session.add(editedItem)
        session.commit()
        flash('Item Sucessfully Edited')
        return redirect(url_for('showItems', city_id=city_id))
    else:
        return render_template('edititem.html', city_id=city_id, item_id=item_id, item=editedItem)

# 8. page to delete the item
@app.route('/forsale/<int:city_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(city_id, item_id):
    itemDelete = session.query(forSale).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(itemDelete)
        session.commit()
        flash("Item deleted!")
        return redirect(url_for('showItems', city_id=city_id))
    else:
        return render_template('deleteitem.html', city_id=city_id, item_id=item_id, item=itemDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
