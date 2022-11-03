# AIphone

This is a super janky game that's basically sort of like Gartic Phone but with AI generated images instead of drawing.

## Installation
### Stable Diffusion Setup
1. Clone this other repo somewhere https://github.com/fboulnois/stable-diffusion-docker.git
2. Set up the huggingface API key by putting a `token.txt` file in the same directory where you cloned that repo. You can get the API key by signing up for an account on huggingface.
3. Also make sure you click the button on the stable diffusion repository on your huggingface account so that you can access the stable diffusion model.
4. Run `./build.sh build` in the stable-diffusion-docker repo to pull the docker containers
5. Oh yeah I forgot you also need to install docker first as well as the nvidia docker container thing, there are instructions iin the stable diffusion docker installation information somewhere.
### AIphone setup
1. Clone this repo and navigate to it
2. Edit the config.py to have the correct directory for your stable-diffusion-docker directory (the other repo you cloned)
3. Run `python3 -m pip install -r requirements.txt`
4. Spin up the server `gunicorn -w2 --bind 0.0.0.0:5000 wsgi:app`

HAVE FUN!
