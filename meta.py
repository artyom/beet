#!/usr/bin/env python

import beet

class BaseField(object):
    def __init__(self, title=None):
        self.title = title


class Field(BaseField):
    pass


class BaseRelatedField(BaseField):
    def __init__(self, related, *args, **kwargs):
        self.related = related
        super(BaseRelatedField, self).__init__(*args, **kwargs)


    def resolve_related(field, func):
        def resolver(self, *args, **kwargs):
            if not field.related == 'self':
                kwargs['related_class'] = field.related
            else:
                kwargs['related_class'] = self.__class__
            kwargs['related_metatype'] = kwargs['related_class']._metatype
            return func(self, *args, **kwargs)
        return resolver


class RelatedOneField(BaseRelatedField):
    def __init__(self, related, backref=False, *args, **kwargs):
        self.backref = backref
        super(RelatedOneField, self).__init__(related, *args, **kwargs)

    def property(field):
        @field.resolve_related
        def fget(self, related_class, related_metatype):
            return related_class.get(self._get_related_one(related_metatype))
        @field.resolve_related
        def fset(self, val, related_class, related_metatype):
            if val.__class__ is not related_class:
                raise beet.BeetError
            return self._set_related_one(related_metatype, val.identifier, backref=field.backref)
        @field.resolve_related
        def fdel(self, related_class, related_metatype):
            return self._del_related_one(related_metatype)
        return property(fget, fset, fdel)


class RelatedSetField(BaseRelatedField):
    def property(field):
        @field.resolve_related
        def fget(self, related_class, related_metatype):
            return self._get_related_set(related_metatype, True, field.name)
        @field.resolve_related
        def fset(self, val, related_class, related_metatype):
            return self._set_related_set(related_metatype, val, True, field.name)
        @field.resolve_related
        def fdel(self, related_class, related_metatype):
            return self._del_related_set(related_metatype, True, field.name)
        return property(fget, fset, fdel)


class MetaModel(type):
    def __new__(cls, classname, bases, dict):
        metatype = classname.lower()
        attributes = ['identifier']
        class Meta:
            fields = []
        for name, field in dict.items():
            if issubclass(field.__class__, BaseField):
                field.name = name
                Meta.fields.append(field)
                del dict[name]
            if issubclass(field.__class__, Field):
                attributes.append(field.name)
            if issubclass(field.__class__, BaseRelatedField):
                dict[field.name] = field.property()
        dict['identifier'] = None
        dict['_metatype'] = metatype
        dict['_attributes'] = attributes
        dict['Meta'] = Meta
        return super(MetaModel, cls).__new__(cls, classname, bases, dict)


class BaseModel(beet.GenericBeetObject):
    __metaclass__ = MetaModel

