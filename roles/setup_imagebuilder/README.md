# setup_imagebuilder
Setup imagebuilder  for building and updating RHEL system images
Before you can use this role install the collection as shown below

```sh
ansible-galaxy collection install git+https://github.com/rprakashg/demos.git,main
```

## variables you can set 
Table below shows variables you can set when using this role

| Name        | Default | Purpose | 
|------       | ------- | ------- | 
| create_infra | False | role will use terraform to provision infra in AWS |
| region | us-west-2 | Only used when provisioning infra with terraform |
| stack | imagebuilder-stack | Stack name |
| instance_name | imagebuilder | Name of EC2 instance |
| instance_type | m5.xlarge | EC2 instance type to use |
| ssh_key | ec2 | SSH key to use for EC2 |
| ami | ami-0f7197c592205b389 | AMI ID to use |
| my_ip | 136.27.40.26/32 | Your default IP to allow ssh traffic |
| iso_storage_bucket | rhde-isos | S3 Bucket for storing ISO installer images |
| ami_bucket_name | rhde-amis | S3 Bucket for storing Snapshot for AMIs |
| microshift | True | Enable Microshift required if building images with Microshift bits |
| microshift_release | 4.16 | Microsoft release |

## Create an inventory file
This step is required if you provisioned imagebuilder infrastructure ahead of time through some external process. Create an inventory file for ansible and include fully qualified DNS name for imagebuilder host. Example below since Imagebuilder host is provisioned on private subnet in VPC, internal DNS is being used.

```yaml
---
all:
  hosts:
    imagebuilder:
      ansible_host: ip-10-0-0-10.us-west-2.compute.internal
      ansible_port: 22
      ansible_user: admin
```

## Create ansible vault
Create ansible vault secrets file by running command below

```sh
ansible-vault create vars/secrets.yml
```

and store red hat user name and password

```
rhuser: <fill>
rhpassword: <fill>
admin_user: <fill>
admin_password: <fill>
offline_token: <fill>
admin_ssh_key: <fill>
```
Store vault password in an environment variable as shown below

```sh
export VAULT_SECRET="<redacted>"
```

Finally create an ansible playbook and name it setup.yml. See sample snippet below

```yml
---
- name: setup ostree playbook
  hosts:
    - imagebuilder
  become: true  
  tasks:
  - name: include ansible vault secrets with rhuser and rhpassword
    include_vars:
      file: "./vars/secrets.yml"
  - name: setup imagebuilder
    ansible.builtin.include_role:
      name: rprakashg.demos.setup_imagebuilder
```

Run the playbook

```sh
ansible-playbook -vvi inventory --vault-password-file <(echo "$VAULT_SECRET") setup.yml

```