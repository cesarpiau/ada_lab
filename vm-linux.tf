variable "vmlinux-count" {
  type    = number
  default = 1
}

resource "azurerm_public_ip" "vmlinux" {
  count               = var.vmlinux-count
  name                = "pip-vml${count.index}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  allocation_method   = "Static"
  # Para definir zona em VM o IP precisa ser Standard
  # sku               = "Standard"
  # zones             = ["1"]
  # domain_name_label = "umbivis"
}

output "vmk8s_public_ips" {
  value = azurerm_public_ip.vmlinux[*].ip_address
}

resource "azurerm_network_interface" "vmlinux" {
  count               = var.vmlinux-count
  name                = "nic-vml${count.index}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnetpublic.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = element(azurerm_public_ip.vmlinux.*.id, count.index)
  }
}

resource "azurerm_linux_virtual_machine" "vmlinux" {
  count = var.vmlinux-count
  #  depends_on = [
  #    azurerm_availability_set.avsetlinux
  #  ]
  name                = "vm-linux-${count.index}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  admin_username      = "adminuser"
  admin_password      = "Parangarico-123"
  size                = "Standard_D4as_v5"
  priority = "Spot"
  eviction_policy = "Deallocate"
  max_bid_price = "0.0416"
  # zone = 1
  # availability_set_id = azurerm_availability_set.avsetlinux.id

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("/adalab_rsa.pub")
  }

  network_interface_ids = [
    element(azurerm_network_interface.vmlinux.*.id, count.index),
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-minimal-focal"
    sku       = "minimal-20_04-lts"
    version   = "latest"
  }
}

resource "azurerm_storage_blob" "vmlinux" {
  name                   = "script-linux-docker.sh"
  storage_account_name   = azurerm_storage_account.stgaccountscript.name
  storage_container_name = azurerm_storage_container.stgcontainerscript.name
  type                   = "Block"
  source                 = "script-linux-docker.sh"
}

resource "azurerm_virtual_machine_extension" "vmlinux" {
  count = var.vmlinux-count
  depends_on = [
    azurerm_storage_blob.vmlinux
  ]
  name                 = "vmlinuxdocker"
  virtual_machine_id   = element(azurerm_linux_virtual_machine.vmlinux.*.id, count.index)
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.0"

  protected_settings = <<PROTECTED_SETTINGS
    {
            "commandToExecute": "sh script-linux-docker.sh",
            "storageAccountName": "${azurerm_storage_account.stgaccountscript.name}",
            "storageAccountKey": "${azurerm_storage_account.stgaccountscript.primary_access_key}",
            "fileUris": [
                "${azurerm_storage_blob.vmlinux.url}"
            ]
    }
  PROTECTED_SETTINGS
}