import bottle
from bottle_session import SessionPlugin
from bottle_redis import RedisPlugin
from config import bottle_config, redis_config
from model.user import User, NotFound

SESSION_LIFETIME = 7 * 24 * 3600

post_list_key = 'post_list'
subject_list_key = 'subject_list'

bottledis_app = bottle.Bottle()


def app_init():

    bottle.debug(True)
    redis_plugin = RedisPlugin(**redis_config)
    bottledis_app.install(redis_plugin)

    session_plugin = SessionPlugin(cookie_lifetime=SESSION_LIFETIME,
                                   host=redis_config['host'],
                                   port=redis_config['port'],
                                   db=redis_config['database'])

    bottledis_app.install(session_plugin)

    bottle.run(bottledis_app, **bottle_config)


@bottledis_app.route('/')
def show_home(rdb, session):
    return bottle.template('home_template.tpl')


@bottledis_app.route('/post')
def show_post_form(session):
    return bottle.template('post_template')


@bottledis_app.route('/add_post')
def add_new_post(rdb, session):
    subject = bottle.request.query.subject
    post = bottle.request.query.post
    rdb.lpush(subject_list_key, subject)
    rdb.lpush(post_list_key, post)
    return bottle.template('post_success', subject=subject, post=post)


@bottledis_app.route('/get_new_posts')
def get_new_posts(rdb, session):
    start = bottle.request.query.get('start', 0)
    end = bottle.request.query.get('end', 9)

    subjects = rdb.lrange(subject_list_key, start=start, end=end)
    posts = rdb.lrange(post_list_key, start=start, end=end)

    return bottle.template('read_template.tpl', subject_list=subjects, post_list=posts)


@bottledis_app.route('/clear_posts')
def clear_posts(rdb, session):
    length = rdb.llen(post_list_key)
    rdb.delete(post_list_key)
    rdb.delete(subject_list_key)
    return bottle.template('delete_template.tpl', length=length)


@bottledis_app.route('/user', method='GET')
def show_user_registration_form(session):
    return bottle.template('register_user_template')


@bottledis_app.route('/add_user', method='POST')
def register_user(rdb, session):
    user_name = bottle.request.forms.get('user_name')
    real_name = bottle.request.forms.get('real_name')
    password = bottle.request.forms.get('password')
    new_user = User(rdb, data_dict=dict(user_name=user_name, real_name=real_name, password=password))
    uid = new_user.save()
    return bottle.template('user_success', {'uid': uid})

@bottledis_app.route('/get_user_data', method='GET')
def show_user_data_form(rdb, session):
    return bottle.template('user_data_request')


@bottledis_app.route('/user_data', method='POST')
def get_user_data(rdb, session):
    uid = bottle.request.forms.get('uid')
    try:
        user = User(rdb, uid=uid)
        return bottle.template('user_data', {'uid': uid,
                                      'user_name': user.data['user_name'],
                                      'real_name': user.data['real_name'],
                                      'password': user.data['password']
                                      })
    except NotFound:
        return bottle.template('user_not_found', {'uid': uid})


if __name__ == '__main__':
    app_init()