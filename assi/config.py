from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = "mongodb+srv://matvei:antipova1977@cluster0.3t0ck.mongodb.net/"

settings = Settings()