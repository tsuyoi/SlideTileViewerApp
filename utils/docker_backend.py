import docker
from docker.errors import NotFound
from pytypes import typechecked
from typing import Dict

from utils import Config


class DockerBackendError(Exception):
    def __init__(self, message):
        self.message = message


class DockerBackend(object):
    def __init__(self):
        self.client = docker.from_env()
        self.backends = {}

    def __del__(self):
        self.client.close()

    def get_backend(self, _backend_name):
        if _backend_name in self.backends:
            return self.backends[_backend_name]
        return None

    def is_backend_running(self, _name):
        _backend = self.get_backend(_name)
        if _backend is not None:
            _backend.reload()
            self.backends[_name] = _backend
            return _backend.status == 'running'

    def start_backend(self, _name, _volumes=None):
        if _volumes is None:
            _volumes = {}
        if not Config.has_docker_backend(_name):
            raise DockerBackendError(f"Backend [{_name}] is not configured")
        if not self.is_backend_running(_name):
            _image = Config.get_docker_backend_property(_name, 'image')
            if _image is not None:
                _ports = Config.get_docker_backend_property(_name, 'ports')
                if _ports is None:
                    _ports = {}
                print(f"Starting {_name} backend with image: {_image}")
                self.backends[_name] = self.client.containers.run(
                    image=_image,
                    ports=_ports,
                    volumes=_volumes,
                    auto_remove=True,
                    detach=True
                )
            else:
                raise DockerBackendError(f"No default image configured for backend [{_name}]")
        else:
            raise DockerBackendError(f"Backend [{_name}] is already running")

    def stop_backend(self, _name):
        if self.is_backend_running(_name):
            print(f"Stopping backend [{_name}]")
            try:
                self.get_backend(_name).stop()
            except NotFound:
                print(f"Backend [{_name}] container was no longer running")
            self.backends.pop(_name)
        else:
            raise DockerBackendError(f"Backend [{_name}] is not running")

    def get_running_containers(self):
        _running = []
        for _container in self.client.containers.list():
            _running.append([
                _container.short_id,
                _container.attrs['Config']['Image']
            ])
        return _running

    @typechecked
    def get_images(self) -> Dict:
        _images = {}
        for _image in self.client.images.list():
            _images[_image.tags[0]] = _image.short_id[_image.short_id.index(':') + 1:]
        return _images
