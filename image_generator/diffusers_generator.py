from typing import Sequence
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
import redis
import json
import os

r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'))
pipe = StableDiffusionPipeline.from_pretrained("./stable-diffusion-v1-5", revision="fp16", torch_dtype=torch.float16, safety_checker=lambda images, *args, **kwargs: (images, False))
pipe.to("cuda")


def gen_images(prompt: Sequence[str], num_images: int, dir_path: Path):
    dir_path.mkdir(parents=True, exist_ok=True)
    i = 0
    for img in pipe([prompt], num_images_per_prompt=num_images).images:
        # This has to be something other than just image_number.png because I'm too lazy to fix the other code
        img_path = dir_path.joinpath(f"{prompt[:20]}_{i}.png")
        img.save(img_path) 
        i += 1


if __name__ == '__main__':
    while True:
        # Get image to generate
        _, data = r.blpop('image_to_generate')
        game_id, round_number, user_id, prompt, drawn_for, num_images = json.loads(data)
        # Generate image
        print(f"Generating images for:\nGame:\t{game_id}\nRound:\t{round_number}\nUser:\t{user_id}")
        dir_path = Path('data').joinpath(str(game_id)).joinpath(str(round_number)).joinpath(str(user_id))
        gen_images(prompt, num_images, dir_path)
        # Update flask with results
        r.lpush('flask_image_done', data)
        print('Sent update to redis')
        # TODO: Add to another react-specific list so that react can also update when images are done being generated
