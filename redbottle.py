import bottle
from redsession.plugin import RedSessionPlugin
from config import bottle_config, redis_config, twitter_config
from model.user import User, Post, NotFound
import urlparse
import oauth2
from urllib import urlencode
import logging
from utils import get_uuid
from ujson import loads
from requests_oauthlib import OAuth1
from requests import get, post

SESSION_LIFETIME = 7 * 24 * 3600
LOG_FILENAME = 'redbottle.log'

redbottle_app = bottle.Bottle()
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


def app_init():
    bottle.debug(True)
    red_session_plugin = RedSessionPlugin(cookie_lifetime=SESSION_LIFETIME, **redis_config)
    redbottle_app.install(red_session_plugin)

    bottle.run(redbottle_app, **bottle_config)


@redbottle_app.route('/')
def show_home(session):
    return bottle.template('home_template.tpl', {'session': session})


@redbottle_app.route('/sign_in')
def signin_form():
    return bottle.template('sign_in_template.tpl')


@redbottle_app.route('/sign_in_result', method='POST')
def signin_result(db, session):
    user_name = bottle.request.forms.get('user_name')
    password = bottle.request.forms.get('password')

    user_record_ids = db.scan(0, match='user*')

    for user_record_id in user_record_ids[1]:
        user_dict = User(db=db, doc_id=user_record_id).data
        if user_name == user_dict['user_name']:
            if password == user_dict['password']:

                session['user_id'] = user_record_id
                session['user_name'] = user_dict['user_name']
                session['real_name'] = user_dict['real_name']
                if 'avatar_url' in user_dict:
                    session['avatar_url'] = user_dict['avatar_url']
                message = 'Signing in as: %s' % user_dict['user_name']
                break
            else:
                message = 'Sign in failed: Wrong Password given.'
                break
    if 'user_id' not in session:
        message = 'Sign in failed: No such user.'
    return bottle.template('sign_in_result.tpl', {'message': message})


@redbottle_app.route('/sign_up', method='GET')
def signup_form():
    return bottle.template('register_user_template')


@redbottle_app.route('/add_user', method='POST')
def register_user(db):
    user_name = bottle.request.forms.get('user_name')
    real_name = bottle.request.forms.get('real_name')
    password = bottle.request.forms.get('password')
    avatar_url = bottle.request.forms.get('avatar_url', None)

    user_dict = dict(user_name=user_name,
                     real_name=real_name,
                     password=password,
                     avatar_url=avatar_url)

    uid = create_user(db, user_dict)
    return bottle.template('user_success', {'uid': uid})


@redbottle_app.route('/sign_in_twitter', method='GET')
def twitter_request(session):
    consumer = oauth2.Consumer(twitter_config['consumer_key'], twitter_config['consumer_secret'])
    client = oauth2.Client(consumer)

    callback_url = '%s:%s%s' % (bottle_config['exernal_host'], bottle_config['port'], '/receive_twitter_tokens')
    resp, content = client.request(twitter_config['request_token_url'], "POST",
                                   body=urlencode({'oauth_callback': callback_url}))
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))
    session['oauth_token'] = request_token['oauth_token']
    session['oauth_token_secret'] = request_token['oauth_token_secret']

    final_auth_url = "%s?oauth_token=%s" % (twitter_config['authenticate_url'], request_token['oauth_token'])

    return bottle.redirect(final_auth_url)

@redbottle_app.route('/receive_twitter_tokens', method='GET')
def twitter_response(db, session):

    oauth_token = bottle.request.query.oauth_token
    oauth_verifier = bottle.request.query.oauth_verifier

    if not oauth_token == session['oauth_token']:
        return bottle.redirect('/')

    token = oauth2.Token(oauth_token, session['oauth_token_secret'])
    token.set_verifier(oauth_verifier)

    consumer = oauth2.Consumer(twitter_config['consumer_key'], twitter_config['consumer_secret'])
    client = oauth2.Client(consumer, token)

    resp, content = client.request(twitter_config['access_token_url'], "POST")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])
    access_token = dict(urlparse.parse_qsl(content))
    user_access_token = access_token['oauth_token']
    user_access_secret = access_token['oauth_token_secret']

    auth = OAuth1(twitter_config['consumer_key'], twitter_config['consumer_secret'],
                  user_access_token, user_access_secret)

    twitter_user_data = get(twitter_config['verify_credentials_url'], auth=auth).json()

    new_user_dict = dict(user_name=twitter_user_data['screen_name'],
                         real_name=twitter_user_data['name'],
                         password=str(get_uuid()),
                         avatar_url=twitter_user_data['profile_image_url_https'],
                         twitter_access_token=user_access_token,
                         twitter_access_secret=user_access_secret)

    # determine if this is a sign-in or a new user
    user_record_ids = db.scan(0, match='user*')

    for user_record_id in user_record_ids[1]:
        user = User(db=db, doc_id=user_record_id)
        if twitter_user_data['screen_name'] == user.data['user_name']:
            # this is a sign-in
            user.data_dict = new_user_dict
            new_user_id = user.save()

            session['user_id'] = new_user_id
            session['user_name'] = twitter_user_data['screen_name']
            session['real_name'] = twitter_user_data['name']
            session['twitter_access_token'] = user_access_token
            session['twitter_access_secret'] = user_access_secret
            session['avatar_url'] = twitter_user_data['profile_image_url_https']
            return bottle.redirect('/')

    # this is a new user

    user_id = create_user(db, new_user_dict)

    session['user_id'] = user_id
    session['user_name'] = new_user_dict['user_name']
    session['real_name'] = new_user_dict['real_name']
    session['twitter_access_token'] = user_access_token
    session['twitter_access_secret'] = user_access_secret
    session['avatar_url'] = twitter_user_data['profile_image_url_https']
    return bottle.redirect('/')


def create_user(db, user_dict):
    new_user = User(db, data_dict=user_dict)
    return new_user.save()


@redbottle_app.route('/post')
def show_post_form():
    return bottle.template('post_template')


@redbottle_app.route('/add_post')
def add_new_post(db, session):
    subject = bottle.request.query.subject
    post = bottle.request.query.post
    new_post = Post(db=db, data_dict=dict(subject=subject, body=post, user_name=session['user_name']))
    new_post.save()
    return bottle.template('post_success', subject=subject, post=post)


@redbottle_app.route('/get_all_posts')
def get_all_posts(db):
    post_ids = db.scan(0, match='post*')

    posts = []
    for post_id in post_ids[1]:
        posts.append(Post(db=db, doc_id=post_id).data)

    return bottle.template('read_template.tpl', posts=posts)


@redbottle_app.route('/clear_posts')
def clear_posts(db):
    post_ids = db.scan(0, match='post*')
    for post_id in post_ids:
        db.delete(post_id)
    return bottle.template('delete_template.tpl', length=len(post_ids[1]))


@redbottle_app.route('/get_user_data', method='GET')
def show_user_data_form():
    return bottle.template('user_data_request')


@redbottle_app.route('/user_data', method='POST')
def get_user_data(db):
    uid = bottle.request.forms.get('uid')
    try:
        user = User(db, doc_id=uid)
        return bottle.template('user_data', {'uid': uid,
                                             'user_name': user.data['user_name'],
                                             'real_name': user.data['real_name'],
                                             'password': user.data['password'],
                                             'avatar_url': user.data['avatar_url']
                                             })
    except NotFound:
        return bottle.template('user_not_found', {'uid': uid})


@redbottle_app.route('/logout', method='GET')
def log_out(session):
    user_name = session['user_name']
    session.destroy()
    return bottle.template('logout_result', user_name=user_name)


if __name__ == '__main__':
    app_init()