# Slide Tile Viewer - Slide Parser Backend

This directory contains sources for the Docker backend which is used to retrieve data from various WSI slide formats, 
including the closed-source [Philips iSyntax](https://www.openpathology.philips.com/isyntax/) format.

### Building
__NOTE: To build this image, you will need to download the Ubuntu 18.04 Python 3.6 version of the Philips Pathology SDK from 
[Philips Open Pathology](https://www.openpathology.philips.com/). This may require signing up for a free account to 
download the required .zip file. Once downloaded, place the zip file in this directory before building your Docker 
image.__

Once you have the required SDK install files, build the image by running the following in this directory:
```
docker build -t <image_name>[:<image_version>] .
```

Docker will run the commands in the `Dockerfile` and report any errors it encounters.

### Running

Running this image requires two elements:
- A WSI slide file mounted to `/tmp/slide.<ext>`
- Expose a port to port `8000` in the container

As an example, to run a container exposing `images/wsi1.isyntax` on port `8080`, use the following:
```
docker run --rm -it -v ${PWD}/images/wsi1.isyntax:/tmp/slide.isyntax -p 8080:8000 <image_name>[:<image_version>]
```

### Backend API

The backend exposes the following API endpoints:
- `/`