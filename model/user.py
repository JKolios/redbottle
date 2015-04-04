from uuid import uuid4


class NotFound(Exception):
    pass


class Document(object):
    document_prefix = 'doc'
    required_keys = []

    def __init__(self, db, data_dict=None, doc_id=None):
        self.db = db
        self.doc_id = None
        self.data_dict = None
        if doc_id:
            self.load(doc_id)
            self.doc_id = doc_id
        elif data_dict:
            if not self.validate(data_dict):
                return
            self.data_dict = data_dict
            print self.data_dict

    def validate(self, data):
        print data.keys()
        print self.required_keys
        for key in data.keys():
            if key not in self.required_keys:
                return False
        return True

    @property
    def data(self):
        return self.data_dict

    def load(self, doc_id):
        doc_id_to_load = self.document_prefix + '_' + doc_id
        if self.db.type(doc_id_to_load) == 'hash':
            self.data_dict = self.db.hgetall(doc_id_to_load)
            return doc_id_to_load
        else:
            raise NotFound

    def save(self):
        if not self.doc_id:
            self.doc_id = self.get_uid_for_type()
        print self.data_dict
        self.db.hmset(self.doc_id, self.data_dict)
        return self.doc_id

    @classmethod
    def get_uid_for_type(cls):
        return cls.document_prefix + '_' + str(uuid4())[:8]


class User(Document):
    document_prefix = 'user'
    required_keys = ['user_name', 'real_name', 'password']

    def __init__(self, db,  doc_id=None, data_dict=None):
        Document.__init__(self, db, doc_id=doc_id, data_dict=data_dict)


class Post(Document):
    document_prefix = 'post'
    required_keys = ['user_name', 'subject', 'body']

    def __init__(self, db,  doc_id=None, data_dict=None):
        Document.__init__(self, db, doc_id=doc_id, data_dict=data_dict)







