resource "azurerm_log_analytics_workspace" "ada-antifraude" {
  name                = "log-ada-antifraude"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "ada_antifraude" {
  name                       = "ada-antifraude"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.ada-antifraude.id
}

resource "azurerm_container_app" "minio" {
  name                         = "minio"
  container_app_environment_id = azurerm_container_app_environment.ada_antifraude.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "ada-antifraude-minio"
      image  = "quay.io/minio/minio"
      cpu    = 0.5
      memory = "1Gi"
      env {
        name  = "MINIO_ROOT_USER"
        value = "guest"
      }
      env {
        name  = "MINIO_ROOT_PASSWORD"
        value = "guestguest"
      }
      args = ["server", "/data", "--console-address", ":9001"]
      volume_mounts {
        name = "minio-data"
        path = "/data"
      }
    }
    volume {
      name         = "minio-data"
      storage_type = "EmptyDir"
    }
  }

  ingress {
    allow_insecure_connections = true
    external_enabled           = true
    target_port                = 9001
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

resource "azurerm_container_app" "rabbitmq" {
  name                         = "rabbitmq"
  container_app_environment_id = azurerm_container_app_environment.ada_antifraude.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "ada-antifraude-rabbitmq"
      image  = "rabbitmq:3-management"
      cpu    = 0.5
      memory = "1Gi"
    }
  }

  ingress {
    allow_insecure_connections = true
    external_enabled           = true
    target_port                = 15672
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

resource "azurerm_container_app" "redis" {
  name                         = "redis"
  container_app_environment_id = azurerm_container_app_environment.ada_antifraude.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "ada-antifraude-redis"
      image  = "redis/redis-stack:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }

  ingress {
    allow_insecure_connections = true
    external_enabled           = true
    target_port                = 8001
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

output "rabbitmq_url" {
  value = "https://${azurerm_container_app.rabbitmq.ingress[0].fqdn}"
}
output "redis_url" {
  value = "https://${azurerm_container_app.redis.ingress[0].fqdn}"
}
output "minio_url" {
  value = "https://${azurerm_container_app.minio.ingress[0].fqdn}"
}