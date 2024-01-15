# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


# appsetup

page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
dbuser = config['DATABASE']['user']
portchoice = config['FLASK']['port']
if portchoice == '5xxx':
    print('ERROR: Please change config.ini as in the comments or Lab 08 instructions')
    exit(0)
session['isadmin'] = False

###########################################################################################
###########################################################################################
####                                 Database operative routes                         ####
###########################################################################################
###########################################################################################



#####################################################
##  INDEX
#####################################################

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['username'] = dbuser
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

#####################################################
# User Login related                        
#####################################################
# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'dbuser' : dbuser}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['userid'], request.form['password'])
        print(val)
        print(request.form)
        # If our database connection gave back an error
        if(val == None):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        print(val[0])
        session['name'] = val[0]['firstname']
        session['userid'] = request.form['userid']
        session['logged_in'] = True
        session['isadmin'] = val[0]['isadmin']
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)

# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



########################
#List All Items#
########################

@app.route('/users')
def list_users():
    '''
    List all rows in users by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_listdict = database.list_users()

    # Handle the null condition
    if (users_listdict is None):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users')
    page['title'] = 'List Contents of users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)
    

########################
#List Single Items#
########################


@app.route('/users/<userid>')
def list_single_users(userid):
    '''
    List all rows in users that match a particular id attribute userid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)
    page['title'] = 'List Single userid for users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)


########################
#List Search Items#
########################

@app.route('/consolidated/users')
def list_consolidated_users():
    '''
    List all rows in users join userroles 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_userroles_listdict = database.list_consolidated_users()

    # Handle the null condition
    if (users_userroles_listdict is None):
        # Create an empty list and show error message
        users_userroles_listdict = []
        flash('Error, there are no rows in users_userroles_listdict')
    page['title'] = 'List Contents of Users join Userroles'
    return render_template('list_consolidated_users.html', page=page, session=session, users=users_userroles_listdict)

@app.route('/user_stats')
def list_user_stats():
    '''
    List some user stats
    '''
    # connect to the database and call the relevant function
    user_stats = database.list_user_stats()

    # Handle the null condition
    if (user_stats is None):
        # Create an empty list and show error message
        user_stats = []
        flash('Error, there are no rows in user_stats')
    page['title'] = 'User Stats'
    return render_template('list_user_stats.html', page=page, session=session, users=user_stats)

@app.route('/users/search', methods=['POST', 'GET'])
def search_users_byname():
    '''
    List all rows in users that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        fnamesearch = database.search_users_customfilter("firstname","~",request.form['searchterm'])
        print(fnamesearch)
        lnamesearch = database.search_users_customfilter("lastname","~",request.form['searchterm'])
        print(lnamesearch)
        
        users_listdict = None

        if((fnamesearch == None) and (lnamesearch == None)):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if(((fnamesearch == None) and (lnamesearch == None)) or ((len(fnamesearch) < 1) and len(lnamesearch) < 1)):
            flash(f"No items found for searchterm: {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            
            users_listdict = fnamesearch
            users_listdict.extend(lnamesearch)
            # Handle the null condition'
            print(users_listdict)
            if (users_listdict is None or len(users_listdict) == 0):
                # Create an empty list and show error message
                users_listdict = []
                flash('Error, there are no rows in users that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Search for a User by name'
            return render_template('list_users.html', page=page, session=session, users=users_listdict)
            

    else:
        return redirect(url_for('/users'))
        
@app.route('/users/delete/<userid>')
def delete_user(userid):
    '''
    List all rows in stations join stationtypes 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_user(userid)
    
    # users_listdict = database.list_users()

    # # Handle the null condition
    # if (users_listdict is None):
    #     # Create an empty list and show error message
    #     users_listdict = []
    #     flash('Error, there are no rows in stations_stationtypes_listdict')
    page['title'] = f'List users after user {userid} has been deleted'
    return redirect(url_for('list_consolidated_users'))
    
@app.route('/users/update', methods=['POST','GET'])
def update_user():
    """
    Update details for a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        return redirect(url_for('list_consolidated_users'))

######
## add items
######

    
@app.route('/users/add', methods=['POST','GET'])
def add_user():
    """
    Add a new User
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        
        if ('firstname' not in request.form):
            newdict['firstname'] = 'Empty firstname'
        else:
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = 'Empty lastname'
        else:
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = 1 # default is traveler
        else:
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = 'blank'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Insert parametesrs are:')
        print(newdict)

        database.add_user_insert(newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_consolidated_users'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())
    
    
# Show all path segments
@app.route('/path_segments')
def path_segments():
    segments = database.list_all_path_segments()
    return render_template('path_segments.html',page=page, session=session, users=segments) 

# Show path segments based on stops traversed
@app.route('/path_segments/stops/<int:stops_count>')
def path_segments_by_stops(stops_count):
    segments = database.list_path_segments_by_stops(stops_count)
    return render_template('path_segments_stops.html',page=page,session=session,stops_count=stops_count,segments=segments)  
    
    
@app.route('/path_segments/add', methods=['GET', 'POST'])
def add_path_segment():
   
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))


    page['title'] = 'Add Path Segment'

   
    new_segment = {}

    if request.method == 'POST':
       
        new_segment['startstationid'] = request.form.get('startstationid', 'Empty')
        new_segment['endstationid'] = request.form.get('endstationid', 'Empty')
        new_segment['expectedtraveltimeSeconds'] = request.form.get('expectedtraveltimeSeconds', 'Empty')
        new_segment['stopsTraversed'] = request.form.get('stopsTraversed', 'Empty')
        new_segment['triplegs'] = request.form.get('triplegs', 'Empty')
        new_segment['coordinatemaplen'] = request.form.get('coordinatemaplen', 'Empty')

  
        database.add_path_segment(
            new_segment['startstationid'],
            new_segment['endstationid'],
            new_segment['expectedtraveltimeSeconds'],
            new_segment['stopsTraversed'],
            new_segment['triplegs'],
            new_segment['coordinatemaplen']
        )


        return redirect(url_for('path_segments'))
    else:
    
        return render_template('add_path_segment.html', page=page,session=session)
    

@app.route('/path_segments/update', methods=['POST', 'GET'])
def update_path_segment_route():
    """
    Update details for a path segment
    """
    # Check if the user is logged in, if not: back to login.
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update Path Segment'

    segment_update = None
    print("request form is:")
    update_dict = {}
    print(request.form)
    valid_update = False

    # Check your incoming parameters
    if request.method == 'POST':
        # verify that the values are available:
        mandatory_fields = ['startstationid', 'endstationid']
        for field in mandatory_fields:
            if field not in request.form:
                flash(f"Cannot update without a {field}")
                return redirect(url_for('path_segments'))
            else:
                update_dict[field] = request.form[field]
                print(f"We have a value for {field}: ", update_dict[field])

        optional_fields = ['expectedtraveltimeSeconds', 'stopsTraversed', 'triplegs', 'coordinatemaplen']
        for field in optional_fields:
            if field in request.form and request.form[field]:
                valid_update = True
                update_dict[field] = request.form[field]
                print(f"We have a value for {field}: ", update_dict[field])
            else:
                update_dict[field] = None

        print('Update dict is:')
        print(update_dict, valid_update)

        if valid_update:
            #forward to the database to manage update
            segment_update = database.update_path_segment(
                update_dict['startstationid'],
                update_dict['endstationid'],
                update_dict['expectedtraveltimeSeconds'],
                update_dict['stopsTraversed'],
                update_dict['triplegs'],
                update_dict['coordinatemaplen']
            )
        else:
            # no updates
            flash("No updated values for segment")
            return redirect(url_for('path_segments'))

        # Redirect to the updated segment or some other appropriate page
        return redirect(url_for('path_segments'))
    else:
        startstationid = request.args.get('startstationid', None)
        endstationid = request.args.get('endstationid', None)

        if not startstationid or not endstationid:
            return "Missing station IDs", 400

        # Fetch the current segment data based on IDs
        current_segment = database.get_path_segment_by_ids(startstationid, endstationid)
        
        # Render the update form with the current segment data
        return render_template('update_path_segment.html', page=page, segment=current_segment, session=session)


@app.route('/path/remove/<start_station>/<end_station>')
def remove_path_segment_route(start_station, end_station):
    '''
    Remove a travel path segment from the system by calling the relevant database calls and then redirecting to the appropriate listing.
    '''
    
    if 'logged_in' not in session or not session['logged_in']:
        flash("You need to be logged in to perform this action.", "error")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Only admins can remove path segments.", "error")
        return redirect(url_for('path_segments'))
    
    resultval = database.remove_path_segment(start_station, end_station)
    
    
    return redirect(url_for('path_segments'))

@app.route('/report/longest_travel_time')
def display_longest_travel_time():
    '''
    Display a report showing stations with the longest expected travel time
    by calling the relevant database function and pushing to the appropriate template
    '''
    # Connect to the database and call the relevant function
    travel_time_report = database.report_longest_travel_time()

    # Handle the null condition
    if (travel_time_report is None):
        # Create an empty list and show error message
        travel_time_report = []
        flash('Error, unable to fetch the travel time report.')

    page['title'] = 'Report on Longest Expected Travel Time by Start Station'
    return render_template('display_travel_time_report.html', page=page, session=session, report=travel_time_report)