#!/usr/bin/env python

import redis
import simplejson

class BeetError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class GenericBeetObject(object):
    _metatype = 'stub'
    _attributes = ['identifier']
    _redis = redis.Redis()
    _cache = {}
    identifier = None

    @classmethod
    def _getinstance(cls, identifier):
        res = cls._redis.get('%s:%s' % (cls._metatype, identifier))
        if not res: return None
        pairs = simplejson.loads(res)
        pairs = dict((str(k), v) for k, v in pairs.iteritems())
        return cls(**pairs)

    @classmethod
    def all(cls):
        # TODO: make this return an iterator
        #return cls._redis.smembers('Objects:%s' % cls._metatype)
        return [cls._getinstance(i) for i in cls._redis.smembers('Objects:%s' % cls._metatype)]
#
# NOTE: code below could be slightly faster since it uses one mget command
# instead of many subsequent gets
#
#        raw_result = cls._redis.mget(*['%s:%s' % (cls._metatype, i) for i in
#                         cls._redis.smembers('Objects:%s' % cls._metatype)])
#        result = []
#        for item in raw_result:
#            pairs = simplejson.loads(item)
#            # convert unicode keys to strings
#            pairs = dict((str(k), v) for k, v in pairs.iteritems())
#            instance = cls(**pairs)
#            result.append(instance)
#        return result


    def save(self):
        if not self.identifier:
            raise BeetError('Incorrect identifier')
        self._redis.sadd('Objects:%s' % self._metatype, self.identifier)
        data = dict((key, self.__getattribute__(key)) for key in
                    self._attributes)
        data = simplejson.dumps(data)
        return self._redis.set('%s:%s' % (self._metatype, self.identifier), data)


    def __init__(self, **kwargs):
        self._cache = {}
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)


    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.identifier)


    def _get_related_one(self, metatype, use_cache=False, cache_id=None):
        if use_cache and cache_id:
            if cache_id in self._cache:
                return self._cache[cache_id]
        key = "%s:%s:>%s" % (self._metatype, self.identifier, metatype)
        value = self._redis.get(key)
        if use_cache and cache_id:
            self._cache[cache_id] = value
        return value

    def _set_related_one(self, metatype, value, use_cache=False, cache_id=None,
                        backref=False):
        key = "%s:%s:>%s" % (self._metatype, self.identifier, metatype)
        self._redis.sadd('Relations:%s:%s' % (self._metatype, self.identifier), key)
        self._redis.set(key, value)
        if backref:
            bkey = "%s:%s:>%s" % (metatype, value, self._metatype)
            self._redis.sadd('Relations:%s:%s' % (metatype, value), bkey)
            self._redis.set(bkey, self.identifier)
        if use_cache and cache_id:
            self._cache[cache_id] = value
        return value

    def _del_related_one(self, metatype, use_cache=False, cache_id=None):
        key = "%s:%s:>%s" % (self._metatype, self.identifier, metatype)
        self._redis.srem('Relations:%s:%s' % (self._metatype, self.identifier), key)
        if use_cache and cache_id:
            if cache_id in self._cache:
                del self._cache[cache_id]
        return self._redis.delete(key)


    def _get_related_set(self, metatype, use_cache=False, cache_id=None):
        if use_cache and cache_id:
            if cache_id in self._cache:
                return self._cache[cache_id]
        key = "%s:%s:}%s" % (self._metatype, self.identifier, metatype)
        values = self._redis.smembers(key)
        if use_cache and cache_id:
            self._cache[cache_id] = values
        return values

    def _set_related_set(self, metatype, value, use_cache=False, cache_id=None):
        # value should be iterable
        key = "%s:%s:}%s" % (self._metatype, self.identifier, metatype)
        self._redis.sadd('Relations:%s:%s' % (self._metatype, self.identifier), key)
        self._redis.delete(key)
        for i in value:
            self._redis.sadd(key, i)
        values = self._redis.smembers(key)
        if use_cache and cache_id:
            self._cache[cache_id] = values
        return values


    def _add_to_related_set(self, metatype, value, use_cache=False, cache_id=None):
        key = "%s:%s:}%s" % (self._metatype, self.identifier, metatype)
        self._redis.sadd('Relations:%s:%s' % (self._metatype, self.identifier), key)
        self._redis.sadd(key, value)
        if use_cache and cache_id:
            self._cache[cache_id] = self._redis.smembers(key)
        return value

    def _del_related_set(self, metatype, use_cache=False, cache_id=None):
        key = "%s:%s:}%s" % (self._metatype, self.identifier, metatype)
        self._redis.srem('Relations:%s:%s' % (self._metatype, self.identifier), key)
        if use_cache and cache_id:
            if cache_id in self._cache:
                del self._cache[cache_id]
        return self._redis.delete(key)
