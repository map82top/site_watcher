import pykka
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from site_storage.sсhema import SiteConfig, RegularCheck
from site_storage.encoders import AlchemyEncoder
import json
import os

app = Flask(__name__,
            static_url_path='',
            static_folder='frontend/static')
socketio = SocketIO(app, async_mode='threading')

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/create_site')
def create_site():
    return app.send_static_file("index.html")


@socketio.on('save_site')
def save_site(data):
    print('Received message = ', data)
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()

    site = SiteConfig(
        name=data['name'],
        url=data['url'],
        regular_check=RegularCheck[data["regular_check"]],
        keys=str(data["keys"])
    )

    storage_proxy.create_site_record(site)


@socketio.on('get_sites')
def get_sites():
    print('Getting list of sites')
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()
    for site in storage_proxy.get_sites().get():
        emit('site', json.dumps(site, cls=AlchemyEncoder))

@socketio.on('delete_site')
def delete_site(site_data):
    print('Deleting site with id = ', site_data['id'])
    storage_urn = os.environ["SITE_STORAGE_URN"]
    storage_proxy = pykka.ActorRegistry.get_by_urn(storage_urn).proxy()
    storage_proxy.delete_site(site_data['id'])