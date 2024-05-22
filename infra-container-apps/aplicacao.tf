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
        name = "MINIO_ENDPOINT"
        value = "minio:9000"
      }
      env {
        name = "MINIO_ROOT_USER"
        value = "guest"
      }
      env {
        name = "MINIO_ROOT_PASSWORD"
        value = "guestguest"
      }
    }
  }

  ingress {
    allow_insecure_connections = true
    external_enabled = true
    target_port = 5000
    traffic_weight {
      percentage = 100
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
      image  = "quay.io/minio/minio"
      cpu    = 0.5
      memory = "1Gi"
      env {
        name = "MINIO_ROOT_USER"
        value = "guest"
      }
      env {
        name = "MINIO_ROOT_PASSWORD"
        value = "guestguest"
      }
      args = [ "server", "/data", "--console-address", ":9001" ]
      volume_mounts {
        name = "minio-data"
        path = "/data"
      }
    }
    volume {
      name = "minio-data"
      storage_type =  "EmptyDir"
    }
  }

  ingress {
    allow_insecure_connections = true
    external_enabled = true
    target_port = 9001
    traffic_weight {
      percentage = 100
      latest_revision = true
    }
  }
}

