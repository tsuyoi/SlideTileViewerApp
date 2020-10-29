from flask import Flask
import os

app = Flask(__name__)
slide_file = os.listdir('/tmp/')[0]
slide_path = f"/tmp/{slide_file}"
slide_name, slide_ext = os.path.splitext(slide_path)
if slide_ext == ".isyntax":
    import pixelengine

    pe = pixelengine.PixelEngine()
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
else:
    import openslide

    def image_properties():
        return "Not iSyntax file"


@app.route('/')
def index():
    return image_properties()


@app.route('/hello')
def hello_world():
    return f"Hello, World!"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
