resource "azurerm_storage_blob" "vmk8s" {
  name                   = "script-k8s-install-1.29.sh"
  storage_account_name   = azurerm_storage_account.stgaccountscript.name
  storage_container_name = azurerm_storage_container.stgcontainerscript.name
  type                   = "Block"
  source                 = "script-k8s-install-1.29.sh"
}

resource "azurerm_virtual_machine_extension" "vmk8s" {
  count = var.vm-k8s
  depends_on = [
    azurerm_storage_blob.vmk8s
  ]
  name                 = "vmk8s"
  virtual_machine_id   = element(azurerm_linux_virtual_machine.vmk8s.*.id, count.index)
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.0"

  protected_settings = <<PROTECTED_SETTINGS
    {
            "commandToExecute": "sh script-k8s-install-1.29.sh",
            "storageAccountName": "${azurerm_storage_account.stgaccountscript.name}",
            "storageAccountKey": "${azurerm_storage_account.stgaccountscript.primary_access_key}",
            "fileUris": [
                "${azurerm_storage_blob.vmk8s.url}"
            ]
    }
  PROTECTED_SETTINGS
}