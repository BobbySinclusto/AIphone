# AIphone

This is a super janky game that's basically sort of like Gartic Phone but with AI generated images instead of drawing.

## Prerequisites
Before you can run AIphone using Docker, you'll have to get the NVIDIA Container Toolkit set up and working. Follow the instructions here: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

## Installation
1. Sign up for an account on huggingface and agree to the model terms here: https://huggingface.co/runwayml/stable-diffusion-v1-5
2. Clone this repo:
```
git clone https://github.com/BobbySinclusto/AIphone.git
```
3. Change directories into it: 
```
cd AIphone
```
4. Run 
```
python3 -m pip install -r requirements.txt
```
5. Install `git-lfs` if you don't already have it
6. Change directories into the image_generator directory:
```
cd image_generator
```
7. Clone the huggingface repo (while still inside the AIphone directory): 
```
git lfs install
git clone https://huggingface.co/runwayml/stable-diffusion-v1-5
```
8. Build the docker container:
```
UID=`id -u` GID=`id -g` docker compose build
```

### Running AIphone
After building (see installation section) spin up the docker container with
```
UID=`id -u` GID=`id -g` docker compose up
```

HAVE FUN!
