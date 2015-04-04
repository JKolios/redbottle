from bottle import Bottle, run, debug, request, template, ext
from bottle_session import SessionPlugin
from config import bottle_config, redis_config
from model.user import User, NotFound

SESSION_LIFETIME = 7 * 24 * 3600

post_list_key = 'post_list'
subject_list_key = 'subject_list'

bottledis_app = Bottle()


def app_init():

    debug(True)
    redis_plugin = ext.redis.RedisPlugin(**redis_config)
    bottledis_app.install(redis_plugin)

    session_plugin = SessionPlugin(cookie_lifetime=SESSION_LIFETIME, **redis_config)
    bottledis_app.install(session_plugin)

    run(bottledis_app, **bottle_config)


@bottledis_app.route('/')
def show_home(rdb, session):
    return template('home_template.tpl')


@bottledis_app.route('/post')
def show_post_form(session):
    return template('post_template')


@bottledis_app.route('/add_post')
def add_new_post(rdb, session):
    subject = request.query.subject
    post = request.query.post
    rdb.lpush(subject_list_key, subject)
    rdb.lpush(post_list_key, post)
    return template('post_success', subject=subject, post=post)


@bottledis_app.route('/get_new_posts')
def get_new_posts(rdb, session):
    start = request.query.get('start', 0)
    end = request.query.get('end', 9)

    subjects = rdb.lrange(subject_list_key, start=start, end=end)
    posts = rdb.lrange(post_list_key, start=start, end=end)

    return template('read_template.tpl', subject_list=subjects, post_list=posts)


@bottledis_app.route('/clear_posts')
def clear_posts(rdb, session):
    length = rdb.llen(post_list_key)
    rdb.delete(post_list_key)
    rdb.delete(subject_list_key)
    return template('delete_template.tpl', length=length)


@bottledis_app.route('/user', method='GET')
def show_user_registration_form(session):
    return template('register_user_template')


@bottledis_app.route('/add_user', method='POST')
def register_user(rdb, session):
    user_name = request.forms.get('user_name')
    real_name = request.forms.get('real_name')
    password = request.forms.get('password')
    new_user = User(data_dict=dict(user_name=user_name, real_name=real_name, password=password))
    uid = new_user.save()
    return template('user_success', {'uid': uid})

@bottledis_app.route('/get_user_data', method='GET')
def show_user_data_form(rdb, session):
    return template('user_data_request')


@bottledis_app.route('/user_data', method='POST')
def get_user_data(rdb, session):
    uid = request.forms.get('uid')
    try:
        user = User(uid=uid)
        return template('user_data', {'uid': uid,
                                      'user_name': user.data['user_name'],
                                      'real_name': user.data['real_name'],
                                      'password': user.data['password']
                                      })
    except NotFound:
        return template('user_not_found', {'uid': uid})


if __name__ == '__main__':
    app_init()