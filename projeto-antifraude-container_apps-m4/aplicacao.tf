resource "azurerm_container_app" "api_relatorios" {
  name                         = "api-relatorios"
  container_app_environment_id = azurerm_container_app_environment.ada_antifraude.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "ada-antifraude-api-relatorios"
      image  = "cesarpiau/lab-api-relatorios:latest"
      cpu    = 0.5
      memory = "1Gi"
      env {
        name  = "MINIO_ENDPOINT"
        value = "minio:9000"
      }
      env {
        name  = "MINIO_ROOT_USER"
        value = "guest"
      }
      env {
        name  = "MINIO_ROOT_PASSWORD"
        value = "guestguest"
      }
    }
  }

  ingress {
    allow_insecure_connections = true
    external_enabled           = true
    target_port                = 5000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

resource "azurerm_container_app" "consumer" {
  name                         = "consumer"
  container_app_environment_id = azurerm_container_app_environment.ada_antifraude.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "ada-antifraude-consumer"
      image  = "cesarpiau/lab-consumer:latest"
      cpu    = 0.5
      memory = "1Gi"
      env {
        name  = "RABBITMQ_HOST"
        value = "rabbitmq"
      }
      env {
        name  = "REDIS_HOST"
        value = "redis"
      }
      env {
        name  = "REDIS_PORT"
        value = "6379"
      }
      env {
        name  = "MINIO_ENDPOINT"
        value = "minio:9000"
      }
      env {
        name  = "MINIO_ROOT_USER"
        value = "guest"
      }
      env {
        name  = "MINIO_ROOT_PASSWORD"
        value = "guestguest"
      }
    }
  }
}

resource "azurerm_container_app_job" "producer" {
  name                         = "producer"
  container_app_environment_id = azurerm_container_app_environment.ada_antifraude.id
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location

  replica_timeout_in_seconds = 10
  replica_retry_limit        = 10

  manual_trigger_config {}

  template {
    container {
      name   = "ada-antifraude-producer"
      image  = "cesarpiau/lab-producer:latest"
      cpu    = 0.5
      memory = "1Gi"
      env {
        name  = "RABBITMQ_HOST"
        value = "rabbitmq"
      }
    }
  }
}

output "api_relatorios_url" {
  value = "https://${azurerm_container_app.api_relatorios.ingress[0].fqdn}/relatorios"
}