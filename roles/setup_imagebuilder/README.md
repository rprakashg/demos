# setup_imagebuilder
Setup imagebuilder  for building and updating RHEL system images
Before you can use this role install the collection as shown below

```sh
ansible-galaxy collection install git+https://github.com/rprakashg/demos.git,main
```

When this role is executed it runs the create_infra portion on your local host which basically runs terraform scripts to provision the require infra in AWS once the infra is provisioned all the image builder setup and configuration portion of the role runs on remote host running in AWS

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
| ostree_bucket_name | rhde-repos | S3 bucket for storing OSTree content |
| base_domain | sandbox2873.opentlc.com | Base domain |
| subdomain | ostree | subdomain for serving OSTree repos |
| microshift | True | Enable Microshift required if building images with Microshift bits |
| microshift_release | 4.16 | Microsoft release |

## Create an inventory file
This step is only required if you run this role with create_infra=false and provisioned the infra ahead of time.

```yaml
---
all:
  hosts:
    imagebuilder:
      ansible_host: <replace with imagebuilder host>
      ansible_port: 22
      ansible_user: admin
```

## Clone this repo
Clone this repo to your local machine and switch to `demos` directory as shown below

```sh
git clone git@github.com:rprakashg/demos.git

cd demos
```

## Create ansible vault
Create ansible vault secrets file by running command below

```sh
ansible-vault create playbooks/vars/secrets.yml
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


Run the playbook

```sh
ansible-playbook --vault-password-file <(echo "$VAULT_SECRET") playbooks/setup_imagebuilder.yml
```

In some cases you may need to retry running the playbook be sure to change the create_infra variable to false and also to specify inventory file when running ansible-playbook command above
