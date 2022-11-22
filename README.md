# AIphone

This is a super janky game that's basically sort of like Gartic Phone but with AI generated images instead of drawing.

## Prerequisites
Before you can run AIphone using Docker, you'll have to get the NVIDIA Container Toolkit set up and working. Follow the instructions here: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

## Installation
1. Sign up for an account on huggingface and agree to the model terms here: https://huggingface.co/runwayml/stable-diffusion-v1-5
2. Install `git-lfs` if you don't already have it
3. Clone this repo:
```
git clone https://github.com/BobbySinclusto/AIphone.git
```
4. Change directories into `AIphone/image_generator`: 
```
cd AIphone/image_generator
```
5. Clone the huggingface repo (while still inside the AIphone directory): 
```
git lfs install
git clone https://huggingface.co/runwayml/stable-diffusion-v1-5
```
6. Build the docker container:
```
UID=`id -u` GID=`id -g` docker compose build
```

### Running AIphone
After building (see installation section) spin up the docker container with
```
UID=`id -u` GID=`id -g` docker compose up
```

HAVE FUN!
