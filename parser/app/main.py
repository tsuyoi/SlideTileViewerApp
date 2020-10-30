from flask import Flask, jsonify
import numpy as np
import os
import sys
import traceback

app = Flask(__name__)
slide_file = os.listdir('/tmp/')[0]
slide_path = f"/tmp/{slide_file}"
slide_name, slide_ext = os.path.splitext(slide_path)
if slide_ext == ".isyntax":
    import pixelengine


    class Backend:
        """
        Class declaration for backends
        """

        def __init__(self, name, context, backend):
            """
            :param name: Name of Backend
            :param context: Context name for backend
            :param contextclass: Context class name for backend
            :param backend: Backend name
            :param backendclass: Backend class
            """
            self.name = name
            self.context = context[0]
            self.backend = backend[0]
            self.contextclass = context[1]
            self.backendclass = backend[1]

    # iterate over backend libraries that might or might not be available
    backends = [
        Backend('SOFTWARE', ['softwarerendercontext', 'SoftwareRenderContext'],
                ['softwarerenderbackend', 'SoftwareRenderBackend']),
        Backend('GLES2', ['eglrendercontext', 'EglRenderContext'],
                ['gles2renderbackend', 'Gles2RenderBackend']),
        Backend('GLES3', ['eglrendercontext', 'EglRenderContext'],
                ['gles3renderbackend', 'Gles3RenderBackend'])
    ]

    valid_backends = []
    for backend in backends:
        try:
            if backend.context not in sys.modules:
                contextlib = __import__(backend.context)
            if backend.backend not in sys.modules:
                backendlib = __import__(backend.backend)
        except RuntimeError:
            pass
        else:
            backend.context = getattr(contextlib, backend.contextclass)
            backend.backend = getattr(backendlib, backend.backendclass)
            valid_backends.append(backend)

    backends = valid_backends


    def get_backends(back_end):
        """
        Method to get backend render and context
        :param back_end: Input backend given by user
        :return: backend renderer and context
        """
        for b_end in backends:
            if b_end.name == back_end:
                return b_end.backend(), b_end.context()
        return None

    render_backend, render_context = get_backends("SOFTWARE")

    pe = pixelengine.PixelEngine(render_backend, render_context)
    pe_input = pe["in"]
    pe_input.open(slide_path)

    def image_properties():
        """
        Properties related to input file are used in this method
        :return: Output of file properties
        """
        num_images = pe_input.num_images
        output = ""
        output += "[common properties]" + "\n"
        output += "pixel engine version : " + pe.version + "\n"
        output += "barcode : " + str(pe_input.barcode) + "\n"
        output += "acquisition_datetime : " + str(pe_input.acquisition_datetime) + "\n"
        output += "date_of_last_calibration : " + str(pe_input.date_of_last_calibration) + "\n"
        output += "time_of_last_calibration : " + str(pe_input.time_of_last_calibration) + "\n"
        output += "manufacturer : " + str(pe_input.manufacturer) + "\n"
        output += "model_name : " + str(pe_input.model_name) + "\n"
        output += "device_serial_number : " + str(pe_input.device_serial_number) + "\n"
        if pe_input.derivation_description:
            output += "derivation_description : " + pe_input.derivation_description + "\n"
        if pe_input.software_versions:
            output += "software_versions : " + str(pe_input.software_versions) + "\n"
        output += "num_images : " + str(num_images) + "\n"
        return output

    def width_height_calculation(x_start, x_end, y_start, y_end, dim_ranges):
        """
        As the input Patch size is from User which is at Level 0 representation.
        Derive Patch Size for the given Level (it defines the output patch image size too)
        :param x_start: Starting X coordinate
        :param x_end: Ending X coordinate
        :param y_start: Starting Y coordinate
        :param y_end: Ending Y coordinate
        :param dim_ranges: Dimension ranges
        :return: patch_width,patch_height
        """
        try:
            # View Range is defined as a closed set i.e. the start and end index is inclusive
            # For example, for startIndex = 0 and endIndex = 511, the size is 512
            patch_width = int(1 + (x_end - x_start) / dim_ranges[0][1])
            patch_height = int(1 + (y_end - y_start) / dim_ranges[1][1])
            return patch_width, patch_height
        except RuntimeError:
            traceback.print_exc()

    def extract_patch(view, region):
        """
        Method to calculate pixel buffer size, patch width, patch height
        :param view: Source view object
        :param region: Region
        :param count: Patch Count
        :param isyntax_file_name: iSyntax Image Name
        :return: pixel_buffer_size, file_name, patch_width, patch_height
        """
        x_start, x_end, y_start, y_end, level = region.range
        dim_ranges = view.dimension_ranges(level)
        patch_width, patch_height = width_height_calculation(x_start, x_end, y_start, y_end,
                                                             dim_ranges)
        # Calculate patch image size for writting to disk
        # 3 is samples per pixels for RGB
        # 4 is samples per pixels for RGBA
        pixel_buffer_size = patch_width * patch_height * 3
        return pixel_buffer_size, patch_width, patch_height

    def grab_pixel_data(x_start, y_start, width, height, level=0):
        try:
            view = pe_input["WSI"].source_view
            truncationlevel = {0: [0, 0, 0]}
            view.truncation(False, False, truncationlevel)
            # Querying number of derived levels in an iSyntax file
            num_levels = view.num_derived_levels + 1
            x_end = x_start + width
            y_end = y_start + height
            view_ranges = []
            view_range = [x_start, (x_end - (2 ** level)), y_start, (y_end - (2 ** level)),
                          level]
            view_ranges.append(view_range)
            app.logger.error(f"{view_ranges}")
            data_envelopes = view.data_envelopes(level)
            app.logger.error(f"{data_envelopes}")
            regions = view.request_regions(view_ranges, data_envelopes, False, [254, 254, 254])
            app.logger.error(f"{regions}")
            region = regions[0]
            pixel_buffer_size, patch_width, patch_height = extract_patch(view, region)
            app.logger.error(f"{pixel_buffer_size} - {patch_width}x{patch_height}")
            pixels = np.empty(int(pixel_buffer_size), dtype=np.uint8)
            region.get(pixels)
            return jsonify(pixels.tolist())
        except:
            traceback.print_exc()
            return f"{traceback.format_exc()}"

else:
    import openslide

    def image_properties():
        return "Not iSyntax file"

    def grab_pixel_data(left, top, width, height):
        return f"Pixel data for {left}x{top}x{left+width}x{top+height}"


@app.route('/')
def index():
    return image_properties()


@app.route('/patch/<int:left>/<int:top>/<int:width>/<int:height>')
def get_patch(left, top, width, height):
    return grab_pixel_data(left, top, width, height)


@app.route('/hello')
def hello_world():
    return f"Hello, World!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
