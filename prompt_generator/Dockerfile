FROM huggingface/transformers-pytorch-gpu:latest

RUN mkdir /prompt_generator
WORKDIR /prompt_generator

COPY . .
RUN pip install -r requirements.txt

CMD [ "python3", "app.py" ]
