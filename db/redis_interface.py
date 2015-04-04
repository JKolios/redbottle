from redis import StrictRedis


class RedisInterface(object):
    _raw_handle = None
    
    @classmethod
    def init_handle(cls, config):
        cls._raw_handle = StrictRedis(**config)
    
    @classmethod
    def delete_key(cls, key):
        return cls._raw_handle.delete(key)
    
    @classmethod
    def key_type(cls, key):
        return cls._raw_handle.type(key)
            
    @classmethod
    def get_from_list(cls, key, start=0, end=-1):
        return cls._raw_handle.lrange(key, start, end)
    
    @classmethod
    def add_to_list(cls, key, element):
        return cls._raw_handle.lpush(key, element)
    
    @classmethod
    def list_length(cls, key):
        return cls._raw_handle.llen(key)
    
    @classmethod
    def set_dict(cls, key, dictionary):
        return cls._raw_handle.hmset(key, dictionary)
    
    @classmethod
    def get_dict(cls, key):
        return cls._raw_handle.hgetall(key)