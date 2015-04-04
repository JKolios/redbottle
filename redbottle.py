import bottle
from redsession.plugin import RedSessionPlugin
from config import bottle_config, redis_config
from model.user import User, Post, NotFound

SESSION_LIFETIME = 7 * 24 * 3600

bottledis_app = bottle.Bottle()


def app_init():

    bottle.debug(True)
    red_session_plugin = RedSessionPlugin(cookie_lifetime=SESSION_LIFETIME, **redis_config)
    bottledis_app.install(red_session_plugin)

    bottle.run(bottledis_app, **bottle_config)


@bottledis_app.route('/')
def show_home(db, session):
    return bottle.template('home_template.tpl')


@bottledis_app.route('/post')
def show_post_form(session):
    return bottle.template('post_template')


@bottledis_app.route('/add_post')
def add_new_post(db, session):
    subject = bottle.request.query.subject
    post = bottle.request.query.post
    return bottle.template('post_success', subject=subject, post=post)


@bottledis_app.route('/get_new_posts')
def get_new_posts(db, session):
    start = bottle.request.query.get('start', 0)
    end = bottle.request.query.get('end', 9)
    all_post_ids = db.scan(0, match='post*')

    subjects = db.lrange(subject_list_key, start=start, end=end)
    posts = db.lrange(post_list_key, start=start, end=end)

    return bottle.template('read_template.tpl', subject_list=subjects, post_list=posts)


@bottledis_app.route('/clear_posts')
def clear_posts(db, session):
    length = db.llen(post_list_key)
    db.delete(post_list_key)
    db.delete(subject_list_key)
    return bottle.template('delete_template.tpl', length=length)


@bottledis_app.route('/user', method='GET')
def show_user_registration_form(session):
    return bottle.template('register_user_template')


@bottledis_app.route('/add_user', method='POST')
def register_user(db, session):
    user_name = bottle.request.forms.get('user_name')
    real_name = bottle.request.forms.get('real_name')
    password = bottle.request.forms.get('password')
    new_user = User(db, data_dict=dict(user_name=user_name, real_name=real_name, password=password))
    uid = new_user.save()
    return bottle.template('user_success', {'uid': uid})

@bottledis_app.route('/get_user_data', method='GET')
def show_user_data_form(db, session):
    return bottle.template('user_data_request')


@bottledis_app.route('/user_data', method='POST')
def get_user_data(db, session):
    uid = bottle.request.forms.get('uid')
    try:
        user = User(db, doc_id=uid)
        return bottle.template('user_data', {'uid': uid,
                                      'user_name': user.data['user_name'],
                                      'real_name': user.data['real_name'],
                                      'password': user.data['password']
                                      })
    except NotFound:
        return bottle.template('user_not_found', {'uid': uid})


if __name__ == '__main__':
    app_init()