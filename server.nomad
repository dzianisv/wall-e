job "walle" {
  group "group-1" {
    task "telegram-bot" {
      driver = "docker"

      # https://developer.hashicorp.com/nomad/docs/drivers/docker
      config {
        image      = "${IMAGE_TAG}"
        force_pull = true
        ports      = ["http"]
      }

      env {
        OPENAI_API_KEY = "${OPENAI_API_KEY}"
        TELEGRAM_BOT_TOKEN = "${TELEGRAM_BOT_TOKEN}"
        OPENWEATHERMAP_API_KEY = "${OPENWEATHERMAP_API_KEY}"
      }
    }
  }
}