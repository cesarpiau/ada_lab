variable "vm-k8s" {
  type    = number
  default = 3
}

resource "azurerm_public_ip" "vmk8s" {
  count               = var.vm-k8s
  name                = "pip-vml${count.index}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  allocation_method   = "Static"
  sku               = "Standard"
  # zones             = ["1"]
  domain_name_label = "adalab${count.index}"
}

output "vmk8s_public_ips" {
  value = azurerm_public_ip.vmk8s[*].domain_name_label
}

resource "azurerm_network_interface" "vmk8s" {
  count               = var.vm-k8s
  name                = "nic-vml${count.index}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnetpublic.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = element(azurerm_public_ip.vmk8s.*.id, count.index)
  }
}

resource "azurerm_linux_virtual_machine" "vmk8s" {
  count = var.vm-k8s
  name                = "k8s-${count.index}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  admin_username      = "adminuser"
  admin_password      = "Adalab$56789"
  size                = "Standard_D4as_v5"
  priority = "Spot"
  eviction_policy = "Deallocate"
  max_bid_price = "0.4000"

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("/id_rsa.pub")
  }

  network_interface_ids = [
    element(azurerm_network_interface.vmk8s.*.id, count.index),
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-minimal-jammy"
    sku       = "minimal-22_04-lts-gen2"
    version   = "latest"
  }

  provisioner "file" {
    connection {
      type = "ssh"
      user = "adminuser"
      host = element(azurerm_public_ip.vmk8s.*.ip_address, count.index)
      private_key = file("/id_rsa")
      agent    = false
      timeout  = "1m"
    }
    source = "./script-k8s-init.sh"
    destination = "/tmp/script-k8s-init.sh"
  }
}