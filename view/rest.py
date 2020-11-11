import pykka
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from site_storage.sсhema import RegularCheck
from site_storage.messages import SiteResponse, SiteDeleteRequest, CreateSiteRequest, UpdateSiteRequest
from site_storage.encoders import AlchemyEncoder
import json
import os

app = Flask(__name__,
            static_url_path='',
            static_folder='frontend/static')
socketio = SocketIO(app, async_mode='gevent')

context = app.app_context()

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/create_site')
def create_site():
    return app.send_static_file("index.html")

@app.route('/update_site')
def update_site():
    return app.send_static_file("index.html")

@app.route('/versions_statistic')
def versions_statistic():
    return app.send_static_file("index.html")

@socketio.on('save_site')
def save_site(data):
    print('Received message = ', data)
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()

    create_site_request = CreateSiteRequest(
        name=data['name'],
        url=data['url'],
        regular_check=RegularCheck[data["regular_check"]],
        keys=str(data["keys"])
    )

    response = storage_proxy.create_site_record(create_site_request).get()
    socketio.emit('create_response', json.dumps(response, cls=AlchemyEncoder))


@socketio.on('update_site')
def update_site(data):
    print('Received message = ', data)
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()

    update_site_request = UpdateSiteRequest(
        id=data['id'],
        name=data['name'],
        url=data['url'],
        regular_check=RegularCheck[data["regular_check"]],
        keys=str(data["keys"])
    )

    response = storage_proxy.update_site(update_site_request).get()
    socketio.emit('update_response', json.dumps(response, cls=AlchemyEncoder))


@socketio.on('get_sites')
def get_sites():
    print('Getting list of sites')
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()

    for site in storage_proxy.get_sites().get():
        site = create_full_site_record(storage_proxy, site)
        json_site = json.dumps(site, cls=AlchemyEncoder)
        socketio.emit('site', json_site)


@socketio.on('get_versions')
def get_versions(data):
    print('Getting list of site_versions')
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()

    for version in storage_proxy.get_all_site_versions(site_id=data['site_id']).get():
        json_version = json.dumps(version, cls=AlchemyEncoder)
        socketio.emit('site_version', json_version)


def create_full_site_record(storage_proxy, site):
    all_site_versions = storage_proxy.get_all_site_versions(site.id).get()
    site_versions = []
    for site_version in all_site_versions:
        site_versions.append({"date": site_version.created_at,
                                           "count_changes": site_version.count_changes,
                                           "count_match_keys": site_version.count_match_keys
                                        })
    site.versions = json.dumps(site_versions, cls=AlchemyEncoder)
    return site

@socketio.on('delete_site')
def delete_site(site_data):
    print('Deleting site with id = ', site_data['id'])
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()
    storage_proxy.delete_site(SiteDeleteRequest(id=site_data['id']))