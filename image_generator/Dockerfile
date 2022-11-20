FROM pytorch/pytorch:latest

COPY requirements.txt /
RUN pip install -r /requirements.txt

# RUN apt-get -qq update && apt-get -qq --no-install-recommends install something

RUN mkdir /image_generator
WORKDIR /image_generator

COPY diffusers_generator.py .

ENV USE_TORCH=1
# dumb permissions issue idk
RUN mkdir -p /image_generator/.cache/huggingface/hub
RUN chmod 777 /image_generator/.cache/huggingface/hub
ENV TRANSFORMERS_CACHE=/image_generator/.cache/huggingface/hub

CMD [ "python3", "diffusers_generator.py" ]
