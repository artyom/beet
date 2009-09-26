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
>>> u1.user = u2
>>> u1.user
<User:paul>
>>> u2.user
<User:john>
>>> Post.all()
[<Post:uh-oh>, <Post:hello>]
>>> u1.posts
set([])
>>> u1.posts = [p1.identifier, p2.identifier]
>>> u1.posts
set([u'uh-oh', u'hello'])
>>> [Post.get(p) for p in u2.user.posts]
[<Post:uh-oh>, <Post:hello>]
"""

import meta

class Post(meta.BaseModel):
    subject = meta.Field(u'Subject')

class User(meta.BaseModel):
    name = meta.Field(u'Name')
    user = meta.RelatedOneField('self', backref=True, title=u'Related user')
    posts = meta.RelatedSetField(Post, u'Related posts')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
