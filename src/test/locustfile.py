from locust import HttpUser, task, between
import boto3
import requests
import uuid

BUCKET_NAME = "123687089814-casamento-m-a-2026"

s3 = boto3.client("s3")

class UploadUser(HttpUser):

    wait_time = between(1, 2)

    @task
    def upload_imagem(self):

        nome_arquivo = f"teste_{uuid.uuid4()}.jpg"

        # 🔥 GERA PRESIGNED URL
        presigned_post = s3.generate_presigned_post(
            Bucket=BUCKET_NAME,
            Key=nome_arquivo,
            ExpiresIn=3600
        )

        # 🔥 ARQUIVO DE TESTE
        with open("foto.jpeg", "rb") as img:

            files = {
                "file": ("foto.jpg", img, "image/jpeg")
            }

            response = requests.post(
                presigned_post["url"],
                data=presigned_post["fields"],
                files=files
            )

            if response.status_code != 204:
                print("Erro upload:", response.text)