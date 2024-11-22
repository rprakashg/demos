# configure_gh_actions_runner
This role can be used to configure a RHEL Image Builder host as a self hosted runner for GitHub Actions Workflow. Useful when building RHEL system images using GitOps methodology.

## Install this collection
Run command below to install latest version of this collection

```sh
ansible-galaxy collection install git+https://github.com/rprakashg/demos.git,main
```

## variables you can set 
Table below shows variables you can set when using this role 

| Name        | Default | Purpose | 
|------       | ------- | ------- | 
| runner_version | 2.320.0 | Version of the GitHub Actions runner to install |
| github_repo | | Specify Github repo to register the self hosted runner |
| github_org | | Specify Github Org repo is part of |

## Clone this repo
Clone this repo to your local by running command below and switch to demos directory.

```sh
git clone git@github.com:rprakashg/demos.git

cd demos
```

## Create Ansible vault
Role will download the registration token for the repo using a github personal access token. If you are not familar with Github PAT see this [article](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)

Create ansible vault by running command below

```sh
ansible-vault create playbooks/vars/secrets.yml
```

and include yaml snippet below with Github PAT token 

```yaml
github_token: <redacted>
```

Store vault secret in an environment variable

```sh
export VAULT_SECRET=<redacted>
```

## Create an inventory file
Create a ansible inventory file and store it under playbooks directory. Include content shown below to inventory file

```yaml
---
all:
  hosts:
    imagebuilder:
      ansible_host: <replace with imagebuilder host FQDN>
      ansible_port: 22
      ansible_user: admin
```

## Run playbook 
Run `configure_gh_actions_runner.yml` playbook to configure image builder host as a self hosted github actions runner. Replace value of vars to your specific values.

```sh
ansible-playbook -i inventory --vault-password-file <(echo "$VAULT_SECRET") configure_gh_actions_runner.yml
```

You can now login to github and navigate to repo->settings-actions-runners and you should see the image builder host registered as actions runner. 



