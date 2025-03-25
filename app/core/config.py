class Settings:
    RABBITMQ_HOST = "rabbitmq"  # Должно совпадать с именем сервиса в docker-compose.yml
    RABBITMQ_PORT = 5672
    REDIS_HOST = "redis"
    REDIS_PORT = 6379
    DOWNLOAD_DIR = "/downloads"
    SUPPORTED_FORMATS = ["mp3", "mp4", "mkv"]
    MAX_PREFETCH_COUNT = 3  # Каждый worker обрабатывает до 3 задач одновременно
    CHECK_STATUS_PAUSE = 5000  # как часто опрашивать на статус задачи (в милисекундах)


settings = Settings()
