variable "location" {
  type = string
  default = "eastus"
}
variable "rg-name" {
  type    = string
  default = "rg-k8s"
}
variable "qtde-vms" {
  type    = number
  default = 1
}
variable "vm-size" {
  type = string
  default = "Standard_D4as_v5"
}
variable "vm-priority" {
  type = string
  default = "Regular"
}