#!/usr/bin/env python
"""
>>> import redis
>>> r = redis.Redis()
>>> r.flush()
'OK'

>>> u1 = User(identifier='john', name='John')
>>> u2 = User(identifier='paul', name='Paul')
>>> u1.save()
'OK'
>>> u2.save()
'OK'
>>> p1 = Post(identifier='hello', subject='Hello, world!')
>>> p1.save()
'OK'
>>> p2 = Post(identifier='uh-oh', subject='Important announce')
>>> p2.save()
'OK'
>>> u1
<User:john>
>>> u2.user
>>> u1.user = u2.identifier
>>> u1.user
u'paul'
>>> u2.user
u'john'
>>> User._getinstance(u2.user)
<User:john>
>>> Post.all()
[<Post:uh-oh>, <Post:hello>]
>>> u1.posts
set([])
>>> u1.posts = [p1.identifier, p2.identifier]
>>> u1.posts
set([u'uh-oh', u'hello'])
>>> [Post._getinstance(p) for p in User._getinstance(u2.user).posts]
[<Post:uh-oh>, <Post:hello>]
"""

import beet

class User(beet.GenericBeetObject):
    _metatype = 'user'
    _attributes = ['identifier', 'name']

    def get_user(self): return self._get_related_one('user')
    def set_user(self, val): return self._set_related_one('user', val, backref=True)
    def del_user(self): return self._del_related_one('user')
    user = property(get_user, set_user, del_user, "Related user")

    def get_posts(self): return self._get_related_set('post', True, 'posts')
    def set_posts(self, posts): return self._set_related_set('post', posts, True, 'posts')
    def del_posts(self): return self._del_related_set('post', True, 'posts')
    posts = property(get_posts, set_posts, del_posts, "Related posts")


class Post(beet.GenericBeetObject):
    _metatype = 'post'
    _attributes = ['identifier', 'subject']

if __name__ == "__main__":
    import doctest
    doctest.testmod()
