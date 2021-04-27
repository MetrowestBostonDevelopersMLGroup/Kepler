"""The Endpoints to manage the BOOK_REQUESTS"""
import uuid
from datetime import datetime, timedelta
from flask import jsonify, abort, request, Blueprint, current_app, flash, redirect
from appManagement import session as sess
import argparse
import os
from werkzeug.utils import secure_filename
from appManagement import configMgr as cmgr

from validate_email import validate_email

KEPLER_API = Blueprint('kepler_api', __name__)


def get_blueprint():
    """Return the blueprint for the main app module"""
    return KEPLER_API


BOOK_REQUESTS = {
    "8c36e86c-13b9-4102-a44f-646015dfd981": {
        'title': u'Good Book',
        'email': u'testuser1@test.com',
        'timestamp': (datetime.today() - timedelta(1)).timestamp()
    },
    "04cfc704-acb2-40af-a8d3-4611fab54ada": {
        'title': u'Bad Book',
        'email': u'testuser2@test.com',
        'timestamp': (datetime.today() - timedelta(2)).timestamp()
    }
}

@KEPLER_API.route('/v1/configuration', methods=['GET'])
def get_configurations():
    """Return all loaded configurations
    @return: 200: an array of all configurations as a \
    flask/response object with application/json mimetype.
    """
    return jsonify(current_app.appMethods.listUploadedConfigurations())

@KEPLER_API.route('/v1/session', methods=['POST'])
def get_session():
    """Creates and returns a unique session identifier
    @return: 200: a UUID identifying the session handle
    """    
    newConfigMgr = cmgr.ConfigMgr(os.getcwd()+current_app.config['UPLOAD_FOLDER'])
    sessionObj = sess.Session(newConfigMgr)
    sid = sessionObj.getNewSID()
    current_app.sessions[sid] = sessionObj
    return jsonify(sid)

@KEPLER_API.route('/v1/session', methods=['GET'])
def get_sessions():
    """Return all active sessions
    @return: 200: an array of all sessions as a \
    flask/response object with application/json mimetype.
    """
    return jsonify(current_app.sessions)

@KEPLER_API.route('/v1/request/<string:_id>', methods=['GET'])
def get_record_by_id(_id):
    """Get book request details by it's id
    @param _id: the id
    @return: 200: a BOOK_REQUESTS as a flask/response object \
    with application/json mimetype.
    @raise 404: if book request not found
    """
    if _id not in BOOK_REQUESTS:
        abort(404)
    return jsonify(BOOK_REQUESTS[_id])



@KEPLER_API.route('/v1/loadAndParseConfig', methods=['POST'])
def loadAndParseConfig():
    """Load and parse a recommender config
    @param sessionId: post : a valid session identifier
    @param configFilename: post : the name of the configuration file to load and parse
    @return: 201: the parse output as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood request
    """
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('filename'):
        abort(400)
    if not data.get('sessionId'):
        abort(400)

    response = current_app.appMethods.loadAndParseInSession(data['sessionId'], data['filename'])
    return response

@KEPLER_API.route('/v1/configRecommend', methods=['POST'])
def configRecommend():
    """Load and parse a recommender config
    @param sessionId: post : a valid session identifier
    @param prompt: post : the user specified text on which to base recommendations
    @return: 201: the parse output as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood request
    """
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('prompt'):
        abort(400)
    if not data.get('sessionId'):
        abort(400)

    response = current_app.appMethods.configRecommend(data['sessionId'], data['prompt'])
    return response

@KEPLER_API.route('/v1/request', methods=['POST'])
def create_record():
    """Create a book request record
    @param email: post : the requesters email address
    @param title: post : the title of the book requested
    @return: 201: a new_uuid as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood request
    """
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('email'):
        abort(400)
    if not validate_email(data['email']):
        abort(400)
    if not data.get('title'):
        abort(400)

    new_uuid = str(uuid.uuid4())
    book_request = {
        'title': data['title'],
        'email': data['email'],
        'timestamp': datetime.now().timestamp()
    }
    BOOK_REQUESTS[new_uuid] = book_request
    # HTTP 201 Created
    return jsonify({"id": new_uuid}), 201


@KEPLER_API.route('/v1/request/<string:_id>', methods=['PUT'])
def edit_record(_id):
    """Edit a book request record
    @param email: post : the requesters email address
    @param title: post : the title of the book requested
    @return: 200: a booke_request as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood request
    """
    if _id not in BOOK_REQUESTS:
        abort(404)

    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('email'):
        abort(400)
    if not validate_email(data['email']):
        abort(400)
    if not data.get('title'):
        abort(400)

    book_request = {
        'title': data['title'],
        'email': data['email'],
        'timestamp': datetime.now().timestamp()
    }

    BOOK_REQUESTS[_id] = book_request
    return jsonify(BOOK_REQUESTS[_id]), 200


@KEPLER_API.route('/v1/request/<string:_id>', methods=['DELETE'])
def delete_record(_id):
    """Delete a book request record
    @param id: the id
    @return: 204: an empty payload.
    @raise 404: if book request not found
    """
    if _id not in BOOK_REQUESTS:
        abort(404)

    del BOOK_REQUESTS[_id]

    return '', 204

