from bottle import Bottle, run, debug, request, template
from config import bottle_config, redis_config
from model.user import User, NotFound
from db.db_handle import DB


post_list_key = 'post_list'
subject_list_key = 'subject_list'

bottledis_app = Bottle()


def app_init():
    DB.setup('redis', redis_config)
    debug(True)

    run(bottledis_app, **bottle_config)


@bottledis_app.route('/')
def show_home():
    return template('home_template.tpl')


@bottledis_app.route('/post')
def show_post_form():
    return template('post_template')


@bottledis_app.route('/add_post')
def add_new_post():
    subject = request.query.subject
    post = request.query.post
    DB.add_to_list(subject_list_key, subject)
    DB.add_to_list(post_list_key, post)
    return template('post_success', subject=subject, post=post)


@bottledis_app.route('/get_new_posts')
def get_new_posts():
    start = request.query.get('start', 0)
    end = request.query.get('end', 9)

    subjects = DB.get_from_list(subject_list_key, start=start, end=end)
    posts = DB.get_from_list(post_list_key, start=start, end=end)

    return template('read_template.tpl', subject_list=subjects, post_list=posts)


@bottledis_app.route('/clear_posts')
def clear_posts():
    length = DB.list_length(post_list_key)
    DB.delete_key(post_list_key)
    DB.delete_key(subject_list_key)
    return template('delete_template.tpl', length=length)


@bottledis_app.route('/user', method='GET')
def show_user_registration_form():
    return template('register_user_template')


@bottledis_app.route('/add_user', method='POST')
def register_user():
    user_name = request.forms.get('user_name')
    real_name = request.forms.get('real_name')
    password = request.forms.get('password')
    new_user = User(data_dict=dict(user_name=user_name, real_name=real_name, password=password))
    uid = new_user.save()
    return template('user_success', {'uid': uid})

@bottledis_app.route('/get_user_data', method='GET')
def show_user_data_form():
    return template('user_data_request')


@bottledis_app.route('/user_data', method='POST')
def get_user_data():
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



# @bottledis_app.route('/get/<db_key>')
# def get_from_db(db_key):
# key_type = db_handle.type(db_key)
#     if key_type == 'string':
#         value = db_handle.get(db_key)
#     elif key_type == 'list':
#         value = db_handle.lrange(db_key, 0, -1)
#     elif key_type == 'hash':
#         value = db_handle.hgetall(db_key)
#     else:
#         value = 'Unsupported type.'
#     return value


# @bottledis_app.route('/set/<db_key>/<db_val>')
# def set_to_db(db_key, db_val):
#     db_handle.set(db_key, db_val)
#     return 'Key: %s set to value: %s' % (db_key, db_val)