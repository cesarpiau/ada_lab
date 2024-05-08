provider "aws" {
  region                      = "us-east-1"
  s3_force_path_style         = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    ec2            = "http://localhost:4597"
  }
}

resource "aws_instance" "vm-aula2" {
  ami           = "ami-0d57c0143330e1fa7"
  instance_type = "t2.micro"
}