job "wall-e" {
  group "group-1" {
    task "telegram-bot" {
      driver = "docker"

      # https://developer.hashicorp.com/nomad/docs/drivers/docker
      config {
        image      = "${IMAGE_TAG}"
        force_pull = true
        ports      = []
      }

      env {
        OPENAI_API_KEY = "${OPENAI_API_KEY}"
        TELEGRAM_BOT_TOKEN = "${TELEGRAM_BOT_TOKEN}"
        OPENWEATHERMAP_API_KEY = "${OPENWEATHERMAP_API_KEY}"
        GOOGLE_CLIENT_ID = "${GOOGLE_CLIENT_ID}"
        GOOGLE_CLIENT_SECRET = "${GOOGLE_CLIENT_SECRET}"
      }
    }
  }
}