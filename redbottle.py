import bottle
from redsession.plugin import RedSessionPlugin
from config import bottle_config, redis_config
from model.user import User, Post, NotFound

SESSION_LIFETIME = 7 * 24 * 3600

redbottle_app = bottle.Bottle()


def app_init():

    bottle.debug(True)
    red_session_plugin = RedSessionPlugin(cookie_lifetime=SESSION_LIFETIME, **redis_config)
    redbottle_app.install(red_session_plugin)

    bottle.run(redbottle_app, **bottle_config)


@redbottle_app.route('/')
def show_home(db, session):
    return bottle.template('home_template.tpl', {'session': session})


@redbottle_app.route('/sign_in')
def signin_form(db, session):
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
                message = 'Signing in as: %s' % user_dict['user_name']
                break
            else:
                message = 'Sign in failed: Wrong Password given.'
                break
    if 'user_id' not in session:
        message = 'Sign in failed: No such user.'
    return bottle.template('sign_in_result.tpl', {'message': message})


@redbottle_app.route('/sign_up', method='GET')
def signup_form(session):
    return bottle.template('register_user_template')


@redbottle_app.route('/add_user', method='POST')
def register_user(db, session):
    user_name = bottle.request.forms.get('user_name')
    real_name = bottle.request.forms.get('real_name')
    password = bottle.request.forms.get('password')
    new_user = User(db, data_dict=dict(user_name=user_name, real_name=real_name, password=password))
    uid = new_user.save()
    return bottle.template('user_success', {'uid': uid})


@redbottle_app.route('/post')
def show_post_form(session):
    return bottle.template('post_template')


@redbottle_app.route('/add_post')
def add_new_post(db, session):
    subject = bottle.request.query.subject
    post = bottle.request.query.post
    new_post = Post(db=db, data_dict=dict(subject=subject, body=post, user_name=session['user_name']))
    new_post.save()
    return bottle.template('post_success', subject=subject, post=post)


@redbottle_app.route('/get_all_posts')
def get_all_posts(db, session):
    post_ids = db.scan(0, match='post*')

    posts = []
    for post_id in post_ids[1]:
        posts.append(Post(db=db, doc_id=post_id).data)

    return bottle.template('read_template.tpl', posts=posts)


@redbottle_app.route('/clear_posts')
def clear_posts(db, session):
    post_ids = db.scan(0, match='post*')
    for post_id in post_ids:
        db.delete(post_id)
    return bottle.template('delete_template.tpl', length=len(post_ids[1]))


@redbottle_app.route('/get_user_data', method='GET')
def show_user_data_form(db, session):
    return bottle.template('user_data_request')


@redbottle_app.route('/user_data', method='POST')
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

@redbottle_app.route('/logout', method='GET')
def log_out(db, session):
    user_name = session['user_name']
    session.destroy()
    return bottle.template('logout_result', user_name=user_name)


if __name__ == '__main__':
    app_init()