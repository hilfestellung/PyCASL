# PyCASL is the pythonized version of http://casl.js.org

## Define abilities

Lets define ```Ability``` for a blog website where visitors:

* can read blog posts
* can manage (i.e. do anything) own post
* cannot delete a post if it was created more than a day ago

```python
from datetime import datetime
from casl import AbilityBuilder

def define_ability_for(user):
    ability_builder = AbilityBuilder()
    ability_builder.can('read', 'BlogPost')
    ability_builder.can('manage', 'BlogPost', fields={'author': user.id})
    ability_builder.cannot('delete', 'BlogPost', conditions=[
            lambda post: post.created_at < datetime.utcnow() - datetime.timedelta(days=1)
        ])
    return ability_builder.build()
```
Do you see how easily business requirements were translated into CASL's rules?

__Note__: you can use class instead of string as a subject type (e.g., ```can('read', BlogPost)```)

## Check abilities

```python
import datetime

class BlogPost(object):
    def __init__(self, title, author, created_at=None):
        self.title = title
        self.author = author
        self.created_at = created_at
        if created_at is None:
            self.created_at = datetime.utcnow()


user = get_loggedin_user()
ability = define_ability_for(user)

ability.can('read', 'BlogPost')  # True
ability.can('read', BlogPost)  # True

ability.can('manage', BlogPost('CASL', user.id))  # True

a_week_ago = datetime.utcnow() - datetime.timedelta(weeks=1)

ability.can('delete', BlogPost('CASL', user.id))  # True
ability.can('delete', BlogPost('CASL', user.id, a_week_ago))  # False
```

## Example with flask

```python
from casl import AbilityBuilder
from flask import _request_ctx_stack, g, request
from flask_restful import abort, fields, marshal

# Flask extension - https://flask.palletsprojects.com/en/1.1.x/extensiondev/
class FlaskAbility(object):
    def __init__(self):
        self.__define_abilities = None

    def init_app(self, app):
        app.before_request(self.init_abilities)

    def define_for(self, f):
        self.__define_abilities = f

    def init_abilities(self):
        request_context = _request_ctx_stack.top
        ability_builder = AbilityBuilder()
        if self.__define_abilities is not None:
            self.__define_abilities(ability_builder.can, ability_builder.cannot)
        casl_ability = ability_builder.build()
        setattr(request_context, 'casl_ability', casl_ability)
        g.ability = casl_ability

    def can(self, action, subject):
        def wrap(f):
            def decorated(*args, **kwargs):
                ctx = _request_ctx_stack.top
                ability = getattr(ctx, 'casl_ability')
                if not ability.can(action, subject):
                    abort(403, message='Access not allowed.')
                return f(*args, **kwargs)

            return decorated

        return wrap

app = create_app()

def define_abilities(can, cannot):
    user = request.user
    can('read', 'BlogPost')
    can('manage', 'BlogPost', fields={'author', user.id})

ability = FlaskAbility()
ability.init_app(app)
ability.define_for(define_abilities)

post_fields = {
    'title': fields.String,
    'author': fields.String,
    'createdAt': fields.DateTime(dt_format='rfc822')
}

@app.route('/post/<string:post_id>', methods=['GET'])
@ability.can('read', 'BlogPost')
def get_blogpost(post_id):
    blogpost = find_blogpost(post_id)
    return marshal(blogpost, fields=post_fields), 200


@app.route('/post/<string:post_id>', methods=['PUT'])
def put_blogpost(post_id):
    blogpost = find_blogpost(post_id)
    if g.ability.cannot('manage', blogpost):
        abort(403, message='Access not allowed')
    ...
    update_blogpost(post_id, blogpost)
    return marshal(blogpost, fields=post_fields), 200

```