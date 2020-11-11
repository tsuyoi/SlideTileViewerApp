import io
import json
import numpy as np
import os
from PIL import Image
import PySimpleGUI as Sg
from pytypes import typechecked
import requests
import traceback

from gui import indicator_empty, indicator_off, indicator_on
from utils import Config, DockerBackend, DockerBackendError


def display_patch(_element, _size, _data):
    if _data is not None:
        _array = np.array(_data, dtype=np.uint8)
        im = Image.fromarray(_array, 'RGBA')
        bio = io.BytesIO()
        im.save(bio, format="PNG")
        del im
        _element.set_size((_size, _size))
        _element.change_coordinates(
            graph_bottom_left=(0, _size),
            graph_top_right=(_size, 0)
        )
        _element.draw_image(data=bio.getvalue(), location=(0, 0))

@typechecked
def gui_main() -> None:
    _docker_backend = DockerBackend()
    _table_data = _docker_backend.get_running_containers()
    Sg.ChangeLookAndFeel('Default 1')
    _menu = [
        [
            "&File",
            [
                "&Configuration",
                "---",
                "E&xit",
            ],
        ],
        [
            "&Help",
            [
                "&About",
            ],
        ],
    ]
    _headers = [
        "Name", "Image"
    ]
    """[
                Sg.Table(
                    values=_table_data,
                    headings=_headers,
                    auto_size_columns=False,
                    num_rows=2,
                    key='runningContainersTable',
                    justification='center',
                    col_widths=[24, 25],
                    bind_return_key=True,
                ),
            ],"""
    _layout = [
        [
            Sg.Menu(_menu),
        ],
        [
            Sg.Text('Slide File:'),
            Sg.Input(key="SLIDEFILEPATH", size=(25, 1)),
            Sg.FileBrowse(
                file_types=(
                    ("Aperio", "*.svs, *.tif"),
                    ("Hamamatsu", "*.vms, *.vmu, *.ndpi"),
                    ("Leica", "*.scn"),
                    ("MIRAX", "*.mrxs"),
                    ("Philips", "*.isyntax, *.tiff"),
                    ("Sakura", "*.svslide"),
                    ("Trestle", "*.tif"),
                    ("Ventana", "*.bif, *.tif"),
                    ("Generic tiled TIFF", "*.tif"),
                )
            ),
            Sg.Button('Start', key='-START-'),
            Sg.Button('Stop', key='-STOP-'),
            Sg.Image(data=indicator_off, key='-INDICATOR-', size=(18, 18))
        ],
        [
            Sg.Text('Left:'),
            Sg.Input(key="PATCHLEFT", default_text="14900", size=(6, 1)),
            Sg.Text('Top:'),
            Sg.Input(key="PATCHTOP", default_text="14900", size=(6, 1)),
            Sg.Text('Size:'),
            Sg.Input(key="PATCHSIZE", default_text="224", size=(6, 1)),
            Sg.Text('Level:'),
            Sg.Input(key="PATCHLEVEL", default_text="0", size=(6, 1)),
            Sg.Button('Query', key='-QUERY-'),
        ],
        [
            Sg.Graph(
                canvas_size=(224, 224),
                graph_bottom_left=(0, 224),
                graph_top_right=(224, 0),
                key="-PATCH-",
                enable_events=True,
                drag_submits=True
            ),
        ]
    ]
    _window = Sg.Window('Test Area', _layout)
    while True:
        _event, _values = _window.read(timeout=1000)
        if _event is None or _event == 'Exit':
            break

        # Events
        if _docker_backend.is_backend_running('slide'):
            _window.Element('-INDICATOR-').Update(data=indicator_on)
        else:
            _window.Element('-INDICATOR-').Update(data=indicator_off)
        if _event == 'Configuration':
            gui_main_configuration(_docker_backend)
        if _event == '-START-':
            _slide_file_path = _values['SLIDEFILEPATH']
            if _slide_file_path is not None and _slide_file_path != '' and os.path.exists(_slide_file_path):
                _slide_file_name, _slide_file_ext = os.path.splitext(_slide_file_path)
                try:
                    _volumes = {
                        _slide_file_path: {
                            'bind': f"/tmp/slide{_slide_file_ext}",
                            'mode': 'ro',
                        }
                    }
                    _docker_backend.start_backend('slide', _volumes)
                except DockerBackendError as e:
                    Sg.PopupError(e, title='Failed to start image backend')
            else:
                if _slide_file_path is None or _slide_file_path == '':
                    Sg.PopupError('Please select a slide file')
                elif not os.path.exists(_slide_file_path):
                    Sg.PopupError(f"Slide file [{_slide_file_path}] does not exist")
                else:
                    Sg.PopupError("Unknown error with _slide_file_path")
        if _event == '-STOP-':
            try:
                _docker_backend.stop_backend('slide')
            except DockerBackendError as e:
                Sg.PopupError(e, title='Failed to stop image backend')
        if _event == '-QUERY-':
            _patch_left = _values['PATCHLEFT']
            _patch_top = _values['PATCHTOP']
            _patch_size = _values['PATCHSIZE']
            _patch_level = _values['PATCHLEVEL']
            _patch_data = None
            _image_size = int(int(_patch_size) / max([1, int(_patch_level) * 2]))
            if _docker_backend.is_backend_running('slide'):
                _query_ports = Config.get_docker_backend_property('slide', 'ports')
                if _query_ports is not None and len(list(_query_ports.keys())) > 0:
                    _query_port = _query_ports[list(_query_ports.keys())[0]]
                    _query_url = f"http://localhost:{_query_port}/patch/{_patch_left}/{_patch_top}/" + \
                                 f"{_patch_size}/{_patch_size}/{_patch_level}"
                    try:
                        _req = requests.get(_query_url)
                        _resp = json.loads(_req.text)
                        if _resp['success']:
                            _patch_data = _resp['pixels']
                        else:
                            Sg.PopupError(_resp['error'], title="Patch Retrieval Error")
                    except Exception:
                        traceback.print_exc()
                        Sg.PopupError("Failed to query slide Docker backend", title="Patch Retrieval Error")
                else:
                    Sg.PopupError('Ports for query not properly configured in container')
            else:
                Sg.PopupError('Slide backend is not currently running')
            display_patch(_window.Element('-PATCH-'), _image_size, _patch_data)
    if _docker_backend.is_backend_running('slide'):
        _docker_backend.stop_backend('slide')
    _docker_backend = None
    _window.close()


@typechecked
def gui_main_configuration(_docker_backend: DockerBackend) -> None:
    _combo_data = _docker_backend.get_images()
    _images = [""] + list(_combo_data.keys())
    _slide_image = Config.get_docker_backend_property('slide', 'image')
    _slide_ports = Config.get_docker_backend_property('slide', 'ports')
    _slide_ports_host = ""
    _slide_ports_container = ""
    if _slide_ports is not None:
        _slide_ports_container = list(_slide_ports.keys())[0]
        _slide_ports_host = _slide_ports[_slide_ports_container]
    _slide_backend_layout = [
        [
            Sg.Text('Docker Image:', size=(14, 1)),
            Sg.Combo(
                list(_images),
                key="SLIDEIMAGE",
                default_value=Config.get_docker_backend_property('slide', 'image'),
                size=(16, 1)
            ),
        ],
        [
            Sg.Text('Port Mapping:'),
        ],
        [
            Sg.Text('', size=(2, 1)),
            Sg.Text('Host'),
            Sg.Input(
                _slide_ports_host,
                key="SLIDEPORTHOST",
                size=(5, 1)
            ),
            Sg.Text('Container'),
            Sg.Input(
                _slide_ports_container,
                key="SLIDEPORTCONTAINER",
                size=(5, 1)
            ),
        ],
    ]
    _training_backend_layout = [
        [
            Sg.Text('Coming soon!')
        ]
    ]
    _tab_group_layout = [
        [
            Sg.Tab('Slide Parser', _slide_backend_layout),
            Sg.Tab('ML Trainer', _training_backend_layout),
        ]
    ]
    _layout = [
        [
            Sg.TabGroup(_tab_group_layout),
        ],
        [
            Sg.Button('Save Changes', key="-SAVE-")
        ]
    ]
    _window = Sg.Window('Configuration', _layout)
    while True:
        _event, _values = _window.read()
        if _event is None or _event == 'Exit':
            break

        # Values
        _slide_image = _values['SLIDEIMAGE']
        _slide_ports_host = _values['SLIDEPORTHOST']
        _slide_ports_container = _values['SLIDEPORTCONTAINER']

        # Events
        if _event == "-SAVE-":
            saved = True
            if _slide_image is not None and len(_slide_image) > 0:
                Config.set_docker_backend_property('slide', 'image', _slide_image)
            else:
                Config.remove_docker_backend_property('slide', 'image')
            try:
                if len(_slide_ports_host) > 0 and len(_slide_ports_container) > 0:
                    _slide_ports = {
                        int(_slide_ports_container): int(_slide_ports_host),
                    }
                    Config.set_docker_backend_property('slide', 'ports', _slide_ports)
                else:
                    Config.remove_docker_backend_property('slide', 'ports')
            except ValueError:
                Sg.PopupError('Please make sure your ports are valid', title='Ports Error')
                saved = False
            if saved:
                break
    _window.close()
