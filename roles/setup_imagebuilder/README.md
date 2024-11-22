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
| my_ip | 136.27.40.26/32 | Your default IP to allow ssh traffic |
| iso_storage_bucket | rhde-isos | S3 Bucket for storing ISO installer images |
| ami_bucket_name | rhde-amis | S3 Bucket for storing Snapshot for AMIs |
| ostree_bucket_name | rhde-repos | S3 bucket for storing OSTree content |
| base_domain | sandbox2873.opentlc.com | Base domain |
| subdomain | ostree | subdomain for serving OSTree repos |
| microshift | True | Enable Microshift required if building images with Microshift bits |
| microshift_release | 4.16 | Microsoft release |

## Clone this repo
Clone this repo to your local machine and switch to `demos` directory as shown below

```sh
git clone git@github.com:rprakashg/demos.git

cd demos
```

## Store secrets in ansible vault
Role requires some secret values set. Table below describes what they are

| Name        | Purpose | 
|------       | ------- | 
| rhuser | Red Hat User Account |
| rhpassword | Red Hat User Account Password |
| admin_user | Admin user to create on device |
| admin_password | Admin user password on the device |
| offline_token | Red Hat Offline token, this is used to download redhat pullsecret |
| admin_ssh_key | SSH key for admin user on device |

Create ansible vault secrets file by running command below

```sh
ansible-vault create playbooks/vars/secrets.yml
```

and include snippet below

```
rhuser: <redacted>
rhpassword: <redacted>
admin_user: <redacted>
admin_password: <redacted>
offline_token: <redacted>
admin_ssh_key: <redacted>
```

Table below describes that the above secrets


Store vault password in an environment variable as shown below

```sh
export VAULT_SECRET="<redacted>"
```


Run the playbook

```sh
ansible-playbook --vault-password-file <(echo "$VAULT_SECRET") playbooks/setup_imagebuilder.yml
```

In some cases you may need to retry running the playbook be sure to change the create_infra variable to false and also to specify inventory file when running ansible-playbook command above
