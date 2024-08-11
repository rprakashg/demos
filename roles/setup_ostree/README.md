# setup_ostree
Setup OSTree for building and updating OSTree based RHEL for edge images.

Before you can use this role install the collection as shown below

```sh
ansible-galaxy collection install git+https://github.com/rprakashg/demos.git,main
```

### Create an inventory file
Create an inventory file for ansible and include fully qualified DNS name for imagebuilder host. Example below since Imagebuilder host is provisioned on private subnet in VPC, internal DNS is being used.

```yaml
---
all:
  hosts:
    imagebuilder:
      ansible_host: ip-10-0-0-10.us-west-2.compute.internal
      ansible_port: 22
      ansible_user: ec2-user
```

### Create ansible vault
Create ansible vault secrets file by running command below

```sh
ansible-vault create vars/secrets.yml
```

and store red hat user name and password

```
rhuser: <fill>
rhpassword: <fill>
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
  tasks:
  - name: include ansible vault secrets with rhuser and rhpassword
    include_vars:
      file: "./vars/secrets.yml"
  - name: setup ostree
    ansible.builtin.include_role:
      name: rprakashg.demos.setup_ostree
```

Run the playbook

```sh
ansible-playbook -vvi inventory --vault-password-file <(echo "$VAULT_SECRET") setup.yml

```