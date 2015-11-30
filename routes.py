##############################################################################
                ##### CONTROLLER, ROUTES, VIEW  ####
##############################################################################
import os
from flask import Flask
from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_wtf import Form
from flask import jsonify
from datetime import datetime
from flask import send_from_directory
from werkzeug import secure_filename
from flask_debugtoolbar import DebugToolbarExtension
# IMPORTED MODEL TABLES TO ROUTES
from model import User, State, User_State, Postcard, AdventureList, Country, User_Country
from model import connect_to_db, db
##############################################################################

app = Flask(__name__)
UPLOAD_FOLDER = '/uploads'
app.secret_key = 'RED PANDA'
##############################################################################
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

##############################################################################

@app.route('/statemap')
def test():
    """ Index page where I test few functions
     and make sure routes are connected """

    print "SERVER IS RUNNING"


    return render_template("statemap.html")
    # return render_template("testworld.html")
##############################################################################
                        ## LOGIN ROUTE ##
##############################################################################

@app.route('/', methods=['GET'])
def wanderlust():
    """Show login form."""

    return render_template("wanderlust.html")


@app.route('/login-process', methods=['POST'])
def process_login():
    """Log user into site, find user in the DB and their
    their user id in the session then if they
     are logged in redirect them to map page"""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    # printing data from form to BASH
    print "form password"

    print password

    # check user exisit and then asign them variable user
    user = User.query.filter_by(email=email).first()

    print "\n \n \n ", user

    # Conditions
    if not user:

        flash("No such user")

        return redirect("/")

    elif user.password != password:

        flash("Incorrect password")

        return redirect("/")
    else:
        session["user_id"] = user.user_id

    flash("Logged in")

    return redirect('/passport')

##############################################################################
                        ## LOG OUT ROUTE ##
##############################################################################

@app.route("/logout")
def process_logout():
    """removing user_id from session to logout user"""

    print " LOGGED OUT USER "

    del session["user_id"]

    flash("You have Successfully Logged Out!")

    return redirect("/")

##############################################################################
                            # # REGISTER ROUTE # #
##############################################################################


@app.route('/register-process', methods=['POST'])
def register_processed():
    """New user signup form"""

    print "REGISTER ROUTE IS WORKING"

    # Get variables from HTML form
    email = request.form["email"]

    password = request.form["password"]

    # query the DB for user
    new_user = User(email=email, password=password)

    # check DB for user searching by email
    same_email_user = User.query.filter(User.email == email).first()

    # users who registered / login will be redircted --> passport/profile pg.
    if same_email_user:
        flash("Email is already registered. Please signin to your account")
        return redirect("/")

    # check user by username --> condition to authentiate user
    same_username = User.query.filter(User.email == email).first()
    if same_username:
        flash("please pick another username")
        return redirect("/")

        # add user to db if they are new
    db.session.add(new_user)
        # commit transaction
    db.session.commit()

    # query db user by email add them to current session and redirect
    # user to passport page

    user = User.query.filter_by(email=email).first()

    flash("User %s added.You have successfully created an account! Welcome to Wanderlust" % email)

    session["user_id"] = user.user_id

    return redirect("/passport")


##############################################################################
                        # #  PASSPORT / PROFILE PAGE # #
##############################################################################

@app.route('/passport')
def passport():
    """wanderlist list interative list where users can add new items to their
    travel bucket list"""

    user_id = session['user_id']

   # query users list items and load list items when user access passport page
    places = db.session.query(AdventureList.adventure_item).filter(AdventureList.user_id == user_id).all()

    # take users wanderlist and loads list items

    # create empty list bind list to variable name new_place_list
    new_place_list = []

    # iterate over items and append them to empty list starting from index[0]
    for item in places:
        new_place_list.append(item[0])

    print new_place_list

    return render_template('passport.html', places=new_place_list)

############################################################################
                            # # BUCKET LIST # #
##############################################################################

             # AJAX adventure list on passportpage

@app.route('/adventurelist', methods=['POST'])
def process_list():

    user_id = session["user_id"]
    new_item = request.form['place']
    print "adventurelist", new_item

    new_list_item = AdventureList(user_id=user_id, adventure_item=new_item)

    db.session.add(new_list_item)
    db.session.commit()
    return "New adventure has been stored in DB"


@app.route('/disply-user-adventure-list', methods=['POST'])


@app.route('/passport-dashboard')
def dashboard():

    address = request.form.get["Street address"]
    city = request.form.get["City"]
    state = request.form.get["State"]
    zipcode = request.form.get["zip code"]
    country = request.form.get["country"]
    des = request.form.get["description"]

    user_id = session["user_id"]


############################################################################

##############################################################################
                        # # STATE MAP AJAX CALL  # #
                    # AJAX CALL FOR USER STATE VISIT #
##############################################################################

@app.route('/state-map-ajax-add', methods=["POST"])
def state_map():
    """ user clicks on state, when color changes, state is stored as a visit.
    DB: STATE_ID: 1 STATE_ABBRREVATION: AL STATE_NAME: Alabama
    """

    # get current user from session
    user_id = session["user_id"]

    print user_id

    # inputs from state map in console.log [feature.id] = state_id feature = state
    state_id = request.form['feature_id']

    print state_id

    state = db.session.query(State).filter_by(state_id=state_id).one()

    user_state_obj = User_State(state_id=state_id, user_id=user_id, visited_at=datetime.now())

    db.session.add(user_state_obj)

    db.session.commit()

    user_state_json_data = {"state_id": state.state_id, "state_name": state.state_name, "visited_at": user_state_obj.visited_at}

    return jsonify(user_state_json_data)

            ################## REMOVING ##########################

@app.route('/state-map-ajax-remove', methods=['POST'])
def removeStateVisit():
    """delete function for removing state visit"""

    user_id = session["user_id"]
    print user_id

    state_id = request.form.get('feature_id')
    state = db.session.query(State).filter_by(state_id=state_id).one()

    user_state_obj = db.session.query(User_State).filter(User_State.user_id == user_id, User_State.state_id == state_id).first()
    print user_state_obj

    user_state_json_data = "error"

    if user_state_obj:

        db.session.delete(user_state_obj)
        db.session.commit()

        user_state_json_data = {"state_id": state_id, "state_name": state.state_name, "visited_at": user_state_obj.visited_at}


    return jsonify(user_state_json_data)


    ###################  LOAD USERS STATE VISITS  #######################

@app.route('/request-user-state-map-ajax-load', methods=['POST'])
def get_users_states():

    user_id = session['user_id']

    #query user in DB for this session
    user_states_visits = db.session.query(User_State).filter_by(user_id=user_id).all()

    # querying users states in User_States Table
    user_state_json_data = db.session.query(User_State).filter_by(state_id=state_id, state_name=state_name, user_id=user_id)

    #conditions
    if request.method == 'POST':
        user_states_data = json.loads(request.form.get('data'))

    # convert python object to json
    user_state_json_data = json.dumps(obj)

    print 'json: %s' % user_state_json_data

    # convert json to python object
    user_state_json_data = json.loads(user_state_json_data)

    return render_template('state_map.html', json=user_states_data )





##############################################################################
                            # # AJAX FOR USER PROFILE # #
##############################################################################

@app.route('/profile', methods=['POST'])
def profile():
    """ RETURN user profile information"""

    user_id = session["user_id"]
    # from HTML form getting inputs from ajax call
    first = request.form.get('first', None)
    last = request.form.get('last', None)
    username = request.form.get('username', None)
    city = request.form.get('city', None)
    state = request.form.get('state', None)
    quote = request.form.get('quote', None)
    about = request.form.get('about', None)


    print "profile", first, last, city, state, quote, about

    # query db for current user
    user = db.session.query(User).filter_by(user_id=user_id).one()

    # ajax request inputs
    user.first_name = first
    user.last_name = last
    user.username = username
    user.city = city
    user.state = state
    user.quote = quote
    user.about = about

    db.session.commit()

    # profile_info_data = {"key": value}
    profile_info_data = {"first": first, "last": last, "username": username,
     "city": city, "state": state, "quote": quote, "about": about}

    # query DB for this user if the unser is none
    print "Profile been has been stored in DB"

    return jsonify(profile_info_data)

    # @app.route('/disply-profile-info', methods=['POST'])

#
##############################################################################
                 # # GOOGLE FORM API PLACE ADDRESS FORM # #
##############################################################################

#AJAX google addresss from on passport page

@app.route('/google-postcard-ajax', methods=['POST'])
def google_postcard_form_ajax():
    """ google address form that prepopulates address"""

    user_id = session["user_id"]

    # input from ajax call from HTML form
    street_number = request.form.get('street_number')
    route_address = request.form.get('route')
    city = request.form.get('locality')
    postal_code = request.form.get('postal_code')
    state = request.form.get("state")
    country = request.form.get('country')
    message = request.form.get('message', None)

    print "google-postcard-ajax", street_number, route_address, city, postal_code, state, country, message

    # commit form information to Database
    db.session.commit()

    postcard_data = {"street_number": street_number, "route": route_address, "city": city, "state": state, "country": country, "message": message}

    return jsonify(postcard_data)

@app.route('/timeline', methods=['GET', 'POST'])
def time():
    return render_template("timeline.html")
#     user_id = session["user_id"]
#     new_item = request.form['postcard']
#     print "timeline", new_item

#     new_list_item = AdventureList(user_id=user_id, adventure_item=new_item)

#     db.session.add(new_list_item)
#     db.session.commit()
#     return "New adventure has been stored in DB"



##############################################################################
                 # # IMAGE UPLAOD FORM ROUTE # #
##############################################################################


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/passport', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(filename)
            # return jsonify({"success":True})
            return redirect('/timeline')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


# @app.route('/timeline/<filename>' methods=["POST"])
# def timeline_image(user):
#     """uploaded postcards sent to timeline"""
#     # get info from postcard and save it to DB

#     user_id = session["user_id"]

#     street_number = request.form.get('street_number')
#     route_address = request.form.get('route')
#     city = request.form.get('locality')
#     postal_code = request.form.get('postal_code')
#     state = request.form.get("state")
#     country = request.form.get('country')
#     message = request.form.get('message', None)
#     image = request.form.get('image')

#     user = db.session.query(Postcard).filter_by(user_id)
#     new_user_postcards = db.session.query(User_Postcard).filter_by(user_id=user_id).all()

#     db.session.add(new_user_postcard)
#     db.session.commit()
#     return redirect("timeline.html", )


#     def timeline_load():
#         """query db for users postcard and loading all users timeline postcards to timeline"""


#     user_id = session['user_id']
#    # query to find users previous postcard items and loads when user logs into account page
#     postcards = db.session.query(PostcardList.postcard_item).filter(PostcardList.user_id == user_id).all()

#     # take users adventure list and loads their list when page loads
#     new_postcard_list = []
#     for item in places:
#         new_postcard_list.append(item[0])

#     print new_postcard_list

#     return render_template('timeline.html', postcards=new_place_item)

#     db.session.add(new_postcard_item)
#     db.session.commit()
#     return "New adventure has been stored in DB"




    #TODO:
    # query DB to post user_pictures on timeline when load
    # get image url id from html form
        # image_id = request.form.get("imge")
        # postcard = db.session.query(image_id.postcard).all())
            # get a list of all the postcards.all --> return list of tuples
        # styles = db.sessionselquery.(style1.styles) # two styles
    # random num = range(len(postcards)) [0, 1,2]
        # get url
        # for item in random_num
        # item = styles[randint(len(styes))]
        # styles[randint][style1, style1, style2, styl1, styl2,]



##############################################################################
                            # # WORLD MAP # #
##############################################################################
@app.route('/world')
def d3_world_map():
    """d3 state map where users can click on country and changes colors"""

    return render_template("world.html")




@app.route('/country-ajax-add', methods=["POST"])
def world_map():
    """ state map where users can click on state and changes colors
    """

    # AJAX CALL FOR USER STATE VISIT

    # get current user from session
    user_id = session["user_id"]
    print user_id

    # inputs from state map in console.log [feature.id] = state_id feature = state
    country_id = request.form['mapData.id']
    print country_id



    country = db.session.query(Country).filter_by(country_id=country_id).one()


    user_country_obj = User_Country(country_id=country_id, user_id=user_id, visited_at=datetime.now())


    # TODO: make the object be added
    db.session.add(user_country_obj)
    db.session.commit()


# #     # TODO: query datbase for the information to go into this json

    user_country_json_data = {"country_id": country.country_id, "country_name": country.country_name, "visited_at": user_country_obj.visited_at}


    return jsonify(user_country_json_data)


# @app.route('/country-ajax-remove', methods=['POST'])
# def removeCountryVisit():
#     """delete function for removing state visit"""

#     user_id = session["user_id"]
#     print user_id

#     country_id = request.form.get('mapData.id')
#     country = db.session.query(Country).filter_by(country_id=country_id).one()

#     user_country_obj = db.session.query(User_Country).filter(User_Country.user_id == user_id, User_Country.country_id == country_id).first()
#     print user_country_obj

#     user_country_json_data = "error"

#     if user_country_obj:

#         db.session.delete(user_country_obj)
#         db.session.commit()

#         user_country_json_data = {"country_id": country_id, "country_name": country.country_name, "visited_at": user_country_obj.visited_at}


#     return jsonify(user_country_json_data)


###############################################################################
# @app.route('/request-user-world-map-ajax-load', methods=['POST'])
# def get_users_states():

#     user_id = session['user_id']

#     #query user in DB for this session
#     user_states_visits = db.session.query(User_State).filter_by(user_id=user_id).all()
#     # querying users states in User_States Table
#     user_state_json_data = db.session.query(User_State).filter_by(state_id=state_id, state_name=state_name, user_id=user_id)
#     if request.method == 'POST':
#         user_states_data = json.loads(request.form.get('data'))

#     # convert python object to json
#     user_state_json_data = json.dumps(obj)
#     print 'json: %s' % user_state_json_data
#     # convert json to python object
#     user_state_json_data = json.loads(user_state_json_data)

#     return render_template('state_map.html', json=user_states_data )





##############################################################################
# HELPER FUNCTIONS
##############################################################################


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    app.debug = True
    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    app.run()