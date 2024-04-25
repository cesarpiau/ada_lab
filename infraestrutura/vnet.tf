resource "azurerm_resource_group" "rg" {
  name     = "rg-k8s"
  location = "eastus"
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-vm"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/24"]
}

resource "azurerm_subnet" "subnetpublic" {
  name                 = "sub-public"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.0.0/25"]
}

resource "azurerm_network_security_group" "nsgpublic" {
  name                = "nsg-public"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "allow_k8s_nodeport"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "30000-32767"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow_k8s_interno"
    priority                   = 101
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = azurerm_virtual_network.vnet.address_space[0]
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow_ssh"
    priority                   = 102
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow_kube_api"
    priority                   = 103
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "6443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

}

resource "azurerm_subnet_network_security_group_association" "subnetpublic" {
  subnet_id                 = azurerm_subnet.subnetpublic.id
  network_security_group_id = azurerm_network_security_group.nsgpublic.id
}

/*
resource "azurerm_network_security_group" "nsgprivate" {
  name                = "nsg-private"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "allow_http"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = azurerm_virtual_network.vnet.address_space[0]
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "deny_all"
    priority                   = 101
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "subnetprivate" {
  subnet_id                 = azurerm_subnet.subnetprivate.id
  network_security_group_id = azurerm_network_security_group.nsgprivate.id
}
*/

resource "azurerm_public_ip" "lbk8s" {
  name                = "pip-lbk8s"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = "adalab"
}

resource "azurerm_lb" "lbk8s" {
  name                = "lb-k8s"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"

  frontend_ip_configuration {
    name                 = "ip-config-public"
    public_ip_address_id = azurerm_public_ip.lbk8s.id
  }
}

resource "azurerm_lb_backend_address_pool" "lbk8s" {
  name            = "lbbeaddpoll-k8s-workers"
  loadbalancer_id = azurerm_lb.lbk8s.id
}

# resource "azurerm_lb_backend_address_pool_address" "lbk8s" {
#   count = var.vm-k8s
#   name                    = "lbbeaddpoll-k8s-workers-ips"
#   backend_address_pool_id             = azurerm_lb_backend_address_pool.lbk8s.id
#   virtual_network_id = azurerm_virtual_network.vnet.id
#   ip_address = element(azurerm_public_ip.vmk8s.*.ip_address, count.index)
# }

resource "azurerm_lb_backend_address_pool_address" "lbk8s2" {
  count = var.vm-k8s
  name                    = "lbbeaddpoll-k8s-workers-ips${count.index}"
  backend_address_pool_id             = azurerm_lb_backend_address_pool.lbk8s.id
  virtual_network_id = azurerm_virtual_network.vnet.id
  ip_address = element(azurerm_network_interface.vmk8s.*.private_ip_address, count.index)
}

resource "azurerm_lb_probe" "lbk8s" {
  loadbalancer_id     = azurerm_lb.lbk8s.id
  name                = "ssh-running-probe"
  port                = 22
  interval_in_seconds = 5
}

resource "azurerm_lb_rule" "rulelbhttp" {
  loadbalancer_id = azurerm_lb.lbk8s.id
  name            = "rule-http"
  protocol        = "Tcp"
  frontend_port   = 80
  backend_port    = 30000
  backend_address_pool_ids = [
    azurerm_lb_backend_address_pool.lbk8s.id
  ]
  frontend_ip_configuration_name = "ip-config-public"
  probe_id                       = azurerm_lb_probe.lbk8s.id
}

output "vmk8s_lb_ip" {
  value = azurerm_public_ip.lbk8s.ip_address
}