from utils import get_uuid


class NotFound(Exception):
    pass


class ValidationError(Exception):
    pass


class Document(object):
    document_prefix = 'doc'
    required_keys = []
    redis_type = 'hash'

    def __init__(self, db,  *args, **kwargs):
        self.doc_id = None
        self.data = None

        if kwargs.get('doc_id') and kwargs.get('data') :
            self.update(db, doc_id=kwargs['doc_id'], new_data=kwargs['data'])
        elif kwargs.get('doc_id'):
            self.retrieve(db, kwargs['doc_id'])
        elif kwargs.get('data'):
            self.new(db, kwargs['data'])

    def update(self, db, doc_id=None, new_data=None):
        if not doc_id:
            doc_id = self.doc_id

        self.retrieve(db, doc_id)

        if not self._validate(new_data):
            raise ValidationError

        if isinstance(self.data, dict) and isinstance(new_data, dict):
            self.data.update(new_data)
        elif isinstance(self.data, list) and isinstance(new_data, list):
            self.data = new_data

    def retrieve(self, db, doc_id):

        if self.document_prefix not in doc_id:
            self.doc_id = self.document_prefix + '_' + doc_id
        else:
            self.doc_id = doc_id
        self._load(db)

    def new(self, db, new_data):
        if not self._validate(new_data):
            raise ValidationError
        self.data = new_data
        self._save(db)

    def _load(self, db):
        try:
            if self.redis_type == 'hash':
                self.data = db.hgetall(self.doc_id)
            elif self.redis_type == 'list':
                self.data = db.range(self.doc_id, 0, -1)
        except Exception as e:
            raise NotFound

    def _save(self, db):
        if not self.doc_id:
            self.doc_id = self.get_key_for_doc_type()
        if self.redis_type == 'hash':
            db.hmset(self.doc_id, self.data)
        elif self.redis_type == 'list':
            # TODO: Smarter list handling
            db.ltrim(self.doc_id, 0, 0)
            db.lpush(self.doc_id, self.data)
        return self.doc_id

    @classmethod
    def get_key_for_doc_type(cls):
        return cls.document_prefix + '_' + str(get_uuid())

    @classmethod
    def get_all_ids(cls, db):
        return db.scan_iter(match=cls.document_prefix + '_*')

    @classmethod
    def _validate(cls, new_data):
        if cls.redis_type == 'hash':
            if not isinstance(new_data, dict):
                return False
            for key in cls.required_keys:
                if key not in new_data.keys():
                    return False
        elif cls.redis_type == 'list':
            if not isinstance(new_data, list):
                return False
            return True
        return True


class User(Document):
    document_prefix = 'user'
    required_keys = ['user_name', 'real_name', 'password']


class Post(Document):
    document_prefix = 'post'
    required_keys = ['user_name', 'subject', 'body']