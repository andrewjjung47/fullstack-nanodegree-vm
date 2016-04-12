from flask import Flask, render_template, request, redirect,jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from flask import session as login_session
import flask.ext.login as flask_login
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "showLogin"

CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# For Flask login
@login_manager.user_loader
def load_user(user_id):
    return getUserInfo(user_id)

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

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

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    
    user_id = getUserID(login_session['email'])
    if not user_id:
        createUser(login_session)

    # Login user with Flask login
    user = getUserInfo(user_id)
    flask_login.login_user(user)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    response = make_response(
                json.dumps(output), 200)
    print "Done!"
    response.headers['Content-Type'] = 'application/json'
    return response

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/logout')
def Logout():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
                json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    print login_session
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']

        flask_login.logout_user()

        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
                json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#JSON APIs to view Restaurant Information
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(Menu_Item = Menu_Item.serialize)

@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants= [r.serialize for r in restaurants])


#Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    public = False
    if 'username' not in login_session:
        public = True
    return render_template('categories.html', public = public, categories=categories)

# Create a new category
@app.route('/category/new/', methods=['GET','POST'])
@flask_login.login_required
def newCategory():
    # Only authenticated users can create a new category
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

# Edit category
@app.route('/category/<int:category_id>/edit/', methods=['GET','POST'])
@flask_login.login_required
def editCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
        session.add(category)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('editCategory.html', category_id=category_id, category=category)

# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET','POST'])
@flask_login.login_required
def deleteCategory(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(category)
        flash('%s Successfully Deleted' % category.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',category_id = category_id, category = category)

#Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant = editedRestaurant)


#Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
    else:
        return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)

# Show items in a category
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items')
def showItems(category_id):
    items = session.query(Item).filter_by(category_id = category_id).all()
    category = session.query(Category).filter_by(id = category_id).one()

    # Only authenticated user can add an item
    public = False
    if 'username' not in login_session:
        public = True
    return render_template('items.html', public=public, items=items, category_id=category_id, category=category)

# Show an item in a category
@app.route('/category/<int:category_id>/<int:item_id>')
def showOneItem(category_id, item_id):
    item = session.query(Item).filter_by(id = item_id).one()

    # Only authenticated user can add an item
    public = False
    if 'username' not in login_session:
        public = True
    return render_template('oneItem.html', public=public, item=item, category_id=category_id, item_id=item_id)



#Create a new item
@app.route('/category/<int:category_id>/item/new/',methods=['GET','POST'])
@flask_login.login_required
def newItem(category_id):
    if request.method == 'POST':
        newItem = Item(name = request.form['name'], description = request.form['description'], category_id = request.form['category_id'], user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showItem', item_id = newItem.id))
    else:
        categories = session.query(Category).all()
        return render_template('newItem.html', categories = categories, category_id=category_id)

#Edit a menu item
@app.route('/category/<int:category_id>/item/<int:item_id>/edit/', methods=['GET','POST'])
@flask_login.login_required
def editItem(category_id, item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    categories = session.query(Category).order_by(asc(Category.name))

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category_id']:
            item.category_id = request.form['category_id']
        session.add(item)
        session.commit() 
        flash('Item Successfully Edited')
        return redirect(url_for('showOneItem', category_id=category_id, item_id=item_id))
    else:
        return render_template('editItem.html', category_id=category_id, item_id=item_id, item=item, categories=categories)


#Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id = menu_id).one() 
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item = itemToDelete)




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 9000)
