from redis_interface import RedisInterface


class DB(object):
    _db_class = None

    @classmethod
    def setup(cls, db_type, config):
        if db_type == 'redis':
            cls._db_class = RedisInterface
            cls._db_class.init_handle(config)
            print 'Redis initialized'
        else:
            print 'Unknown DB type'

    @classmethod
    def delete_key(cls, key):
        return cls._db_class.delete_key(key)

    @classmethod
    def key_type(cls, key):
        return cls._db_class.key_type(key)

    @classmethod
    def get_from_list(cls, key, start=0, end=-1):
        return cls._db_class.get_from_list(key, start, end)

    @classmethod
    def add_to_list(cls, key, element):
        return cls._db_class.add_to_list(key, element)

    @classmethod
    def list_length(cls, key):
        return cls._db_class.list_length(key)

    @classmethod
    def set_dict(cls, key, dictionary):
        return cls._db_class.set_dict(key, dictionary)

    @classmethod
    def get_dict(cls, key):
        return cls._db_class.get_dict(key)






