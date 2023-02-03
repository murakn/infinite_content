from datetime import datetime
import os
import time
import openai
import json
import urllib.request
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

from PIL import Image

openai.api_key = os.environ["OPEN_AI_KEY"]


class InfiniteContent:
    def __init__(self, seed) -> None:
        self.show = seed
        self.seed = f"write an episode of {seed} with dialogue"
        self.continuation = ""
        self.context = []

    def generate_image(self, text, model=None):
        if len(text) > 200:
            text = text[:200]
        response = openai.Image.create(
            prompt=f"scene from {self.show}: {text}",
            n=1,
            size="256x256",
        )
        filename = f"images/{datetime.timestamp(datetime.now())}.png"
        urllib.request.urlretrieve(response["data"][0]["url"], filename)
        img = Image.open(filename)

        return img

    def generate_gpt3_response(self, text, model=None):
        completions = openai.Completion.create(
            engine='text-davinci-003',
            temperature=0.7,
            prompt=text,
            max_tokens=1000,
            n=1,
            stop=None,
            model=model
        )

        return completions.choices[0].text

    def start_training(self, dataset):
        upload_response = openai.File.create(
            file="\n".join([json.dumps(datapoint)
                           for datapoint in dataset]).encode('utf-8'),
            purpose='fine-tune'
        )

        file_id = upload_response.id
        fine_tune_response = openai.FineTune.create(
            training_file=file_id, model=self.open_ai_model if self.open_ai_model else "davinci")

        return fine_tune_response.id

    def get_training_status(self, fine_tuning_id):
        response = openai.FineTune.retrieve(
            id=fine_tuning_id)

        if response.fine_tuned_model is not None:
            return response.fine_tuned_model, True

        response = openai.FineTune.list_events(
            id=fine_tuning_id)

        return response.data, False

    def get_voice(self, text, voice):
        try:
            voice_obj = gTTS(text=text, lang='en', slow=False)
        except AssertionError:
            return None

        mp3_fp = BytesIO()
        voice_obj.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        return mp3_fp

    def play(self, voice, image, text):
        print(f"\n\n{text}\n\n")
        image.show()
        if voice is not None:
            audio = AudioSegment.from_file(voice, format="mp3")
            play(audio)
        else:
            time.sleep(2)
        image.close()

    def main(self):
        while True:
            completion = self.generate_gpt3_response(
                self.continuation+self.seed)
            self.continuation = ""
            lines = completion.split("\n")
            for n, line in enumerate(lines):
                if line.replace(" ","") == "":
                    continue
                if len(line.split(":")) > 1:
                    voice = self.get_voice(
                        ":".join(line.split(":")[1:]), line.split(":")[0])
                else:
                    voice = self.get_voice(line, None)
                    if len(self.context) > 3:
                        self.context.pop(0)
                    self.context.append(line)
                context_text = '\n'.join(self.context)
                image = self.generate_image(
                    f"{self.seed}\n{context_text}\n{line}")
                self.play(
                    voice=voice,
                    image=image,
                    text=line
                )
                if n > (len(lines) - 4):
                    self.continuation += f"\n{line}"

            self.continuation += "\n\n continue"


if __name__ == "__main__":
    content = InfiniteContent(input("Seed: "))
    content.main()
