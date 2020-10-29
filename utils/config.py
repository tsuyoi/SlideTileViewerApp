import errno
import os
import yaml

from appdirs import user_data_dir


class Config(object):
    appname = "UKHCTileViewer"
    appauthor = "UKHC"

    dir = user_data_dir(appname, appauthor)
    docker_backends = {}

    @classmethod
    def init(cls):
        try:
            os.makedirs(cls.dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
            pass
        cls.load()

    @classmethod
    def has_docker_backend(cls, _name):
        return _name in cls.docker_backends

    @classmethod
    def get_docker_backend(cls, _name):
        if _name in cls.docker_backends:
            return cls.docker_backends[_name]
        return None

    @classmethod
    def get_docker_backend_property(cls, _name, _property):
        _docker_backend = cls.get_docker_backend(_name)
        if _docker_backend is not None and _property in _docker_backend:
            return _docker_backend[_property]
        return None

    @classmethod
    def set_docker_backend_property(cls, _name, _property, _value, _save_config=True):
        _docker_backend = cls.get_docker_backend(_name)
        if _docker_backend is None:
            _docker_backend = {}
        _docker_backend[_property] = _value
        cls.docker_backends[_name] = _docker_backend
        if _save_config:
            cls.save()

    @classmethod
    def remove_docker_backend_property(cls, _name, _property):
        if _name in cls.docker_backends:
            cls.docker_backends[_name].pop(_property)
            cls.save()

    @classmethod
    def save(cls):
        _conf = {}
        if cls.docker_backends is not None:
            _conf['docker_backends'] = cls.docker_backends
        yaml.safe_dump(
            _conf,
            open(os.path.join(cls.dir, 'config.yml'), 'w'),
            sort_keys=False
        )

    @classmethod
    def load(cls) -> bool:
        try:
            _conf = yaml.safe_load(open(os.path.join(cls.dir, 'config.yml'), 'r'))
            if 'docker_backends' in _conf:
                cls.docker_backends = _conf['docker_backends']
            return True
        except FileNotFoundError:
            return False
