DELIMITER = ','
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
import os
import csv
import hashlib

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.utils import secure_filename
from flask import current_app as app
from . import database as db

session_vars= ('githash','adminkey','username','crank')
# check that admin key is correct, git commit is 7 digits and csv file is the right format
def validate(adminkey,githash,filename):
    if adminkey != app.config['ADMIN_KEY']:
        return "Wrong admin key"
    
    if len(githash) != 7:
        return "Git commit hash is not 7 characters (current length is %d)" % len(githash)

    header=""
    #make sure file is comma  delimited
    with open(filename, 'r') as fh:
        for header in fh:
            print(header)
            if header[0] != '#':
                break

    required_header="dataset,name,_rxn_M_inorganic,_rxn_M_organic"
    if header.strip() != required_header:
        return "csv file does not have required header '%s'" % required_header
    
    return None

bp = Blueprint('admin',__name__)
@bp.route('/admin', methods=('GET','POST'))
def admin():

    error = None
    
    if request.method == 'GET':
        #clear POST variables between sessions
        for key in session_vars:
            session.pop(key,None)
                
    if request.method == 'POST' and (request.headers.get('User-Agent') == 'escalation'):
        #save form values to pre-populate if there's an error so user saves time
        for key in session_vars:
            session[key] = request.form[key]

        stateset  = request.files['stateset']
        stateset_file  = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(stateset.filename))

        training = request.files['perovskitedata']
        training_file = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(training.filename))
                
        username = request.form['username']
        crank = request.form['crank']                
        githash  = request.form['githash']


        app.logger.info("Received request: {} {} {} {} {}".format(stateset_file,training_file,username,crank,githash))
        
        stateset.save(stateset_file)
        error = validate(request.form['adminkey'],githash,stateset_file)
        app.logger.info("Validated %s" % stateset.filename)

        training.save(training_file)
        stateset_id = None
        if error == None:
            #get statset from first element
            with open(stateset_file) as csv_file:
                csv_reader = csv.DictReader(filter(lambda row: row[0]!='#', csv_file))
                for row in csv_reader:
                    stateset_id = row['dataset']
                    break

            num_rows       = db.add_stateset(crank,stateset_id,stateset_file,githash,username)
            num_train_rows = db.add_training(crank,stateset_id,training_file,githash,username)            
            out="Successfully updated to crank %s and stateset %s with %d rows" % (crank, stateset_id,num_rows)
            app.logger.info(out)
            flash(out)
            for key in session_vars:
                session.pop(key,None)

        #custom check if POST from script instead of UI
        if request.headers.get('User-Agent') == 'escalation':
            if error:
                return jsonify({'error':error}), 400
            else:
                return jsonify({'success':'updated to crank %s and stateset hash %s with %d rows' % (crank,stateset_id,num_rows)}), 200

    if request.method == 'POST' and request.form['submit'] == "Roll back Stateset":
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            res = db.get_stateset(request.form['new_stateset'])
            if res is None:
                flash("Something went wrong getting stateset id",request.form['new_stateset'])
            else:
                flash("Updating stateset to crank %s and hash %s" % (res['crank'], res['stateset']))
                db.set_stateset(res['id'])
                app.logger.info("Updating stateset to crank %s and hash %s" % (res['crank'], res['stateset']))
                
    if request.method == 'POST' and  request.form['submit'] == 'Update Database' :
        for k in request.form:
            app.logger.info(k)
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            from . import insert_demo_data, delete_db
            if request.form['db'] == 'demo':
                insert_demo_data()
                app.logger.info("Reset database to demo data")
                flash("Reset statespace to demo data")
            elif request.form['db'] == 'reset':
                delete_db()
                app.logger.info("Deleted all data")
                flash("Deleted all data")
            else:
                flash("Unknown command, doing nothing")
            
            
    cranks = db.get_cranks()
    return render_template('admin.html',cranks=cranks,session=session)
