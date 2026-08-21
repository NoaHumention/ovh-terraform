# Terraform on OVH

This repository contains my experiments and learning project for using **Terraform to create and manage infrastructure on OVHcloud**.

The ultimate goal of this project is to learn how to build a **data lake on OVHcloud using Infrastructure as Code (IaC)**.

Instead of manually creating every resource in the OVHcloud Control Panel, Terraform allows the infrastructure to be described as code. Terraform can then create, update and remove the infrastructure based on that configuration.

## Documentation

The main documentation for the OVHcloud Terraform provider is available in the Terraform Registry:

[OVHcloud Terraform Provider documentation](https://registry.terraform.io/providers/ovh/ovh/latest/docs)

The provider is called:

```text
ovh/ovh
```

The OVHcloud Terraform provider is the interface between Terraform and the OVHcloud API. It provides Terraform resources and data sources for managing OVHcloud infrastructure. ([Terraform Registry][1])

OVHcloud also provides its own guide:

[Using Terraform with OVHcloud](https://docs.ovhcloud.com/en/guides/manage-and-operate/terraform/at-ovhcloud)

---

# Learning Terraform

I followed a document created with ChatGPT called:

```text
Learning Terraform on OVHcloud - From Terraform Basics to a Data Lake.md
```

This is a step-by-step learning guide that starts with the basics of Terraform and gradually builds towards creating a data lake on OVHcloud.

The intention is not simply to copy the Terraform code from the guide. Instead, each step introduces another Terraform or OVHcloud concept.

The learning path roughly looks like:

```text
Terraform basics
      ↓
OVHcloud provider
      ↓
Networking
      ↓
Compute / instances
      ↓
Storage
      ↓
IAM
      ↓
Terraform modules
      ↓
Data lake infrastructure
      ↓
Application deployment
```

This makes the repository both a working Terraform project and a learning exercise.

---

# Using ChatGPT as a Terraform tutor

A useful way to work through this project is to ask ChatGPT to **act as a tutor rather than a code generator**.

For example, instead of asking:

> "Give me the Terraform code to create an OVH network."

ask:

> "Act as a Terraform tutor. I want to create an OVH private network. Explain what I need to create and give me pseudocode, but don't give me the complete solution unless I ask for it."

This makes it easier to understand:

* What each Terraform resource does
* Why resources depend on each other
* How variables work
* How modules work
* How Terraform determines the order in which resources are created
* How OVHcloud concepts map to Terraform resources
* How to troubleshoot Terraform errors

If you get stuck, ask for progressively more help rather than immediately asking for the complete solution.

For example:

```text
1. Explain the concept
        ↓
2. Give me a hint
        ↓
3. Give me pseudocode
        ↓
4. Show me the relevant documentation
        ↓
5. Show me an example
        ↓
6. Give me the solution
```

This is especially useful when learning Terraform because the goal is to understand **Infrastructure as Code**, rather than simply producing a working `.tf` file.

---

# Project structure

The project is split into Terraform modules.

A simplified structure looks like:

```text
terraform/
├── main.tf
├── variables.tf
├── terraform.tf
├── standard_vars_auto.tfvars
│
├── modules/
│   ├── network/
│   ├── compute/
│   ├── storage/
│   └── IAM/
│
└── standard_vars_auto.tfvars.example
```

---

# Why use modules?

Terraform modules allow related resources to be grouped together.

For example:

```text
network module
    ├── private network
    └── subnet

compute module
    ├── instance 1
    ├── instance 2
    └── instance 3

storage module
    ├── bronze bucket
    ├── silver bucket
    └── gold bucket

IAM module
    ├── ingestion user
    ├── processing user
    └── analytics user
```

The root Terraform configuration can then connect these modules together.

For example:

```hcl
module "network" {
  source = "./modules/network"
}

module "compute" {
  source = "./modules/compute"

  network_id = module.network.network_id
}
```

This makes the configuration easier to maintain and allows a module to be reused.

Terraform's documentation provides more information about how modules work:

[Terraform modules](https://developer.hashicorp.com/terraform/language/modules)

You can also find existing modules in the Terraform Registry:

[Terraform Registry - Modules](https://registry.terraform.io/browse/modules)

Terraform supports both locally-created modules and modules published in the Terraform Registry. ([HashiCorp Developer][2])

---

# Variables and `.tfvars` files

Terraform variables allow values to be separated from the actual infrastructure definition.

For example:

```hcl
variable "region" {
  type    = string
  default = "GRA11"
}
```

The value can then be overridden using a `.tfvars` file:

```hcl
region = "GRA11"
```

This makes it possible to reuse the same Terraform configuration with different values.

For example:

```text
development
    region = GRA11

production
    region = SBG5
```

while keeping the actual infrastructure definition unchanged.

---

# `standard_vars_auto.tfvars`

This repository uses:

```text
standard_vars_auto.tfvars
```

for automatically loaded Terraform variable values.

Terraform automatically loads files ending in:

```text
.auto.tfvars
```

and:

```text
.auto.tfvars.json
```

when Terraform runs.

This means you do not have to specify the file manually with:

```bash
terraform apply -var-file="standard_vars_auto.tfvars"
```

Instead, Terraform automatically loads it.

For example:

```hcl
region = "GRA11"

instance_names = [
  "instance1",
  "instance2",
  "instance3"
]
```

## Example configuration

The repository also contains:

```text
standard_vars_auto.tfvars.example
```

This file demonstrates what your own `standard_vars_auto.tfvars` could look like.

The `.example` file is safe to commit to Git because it should contain example values rather than secrets.

A local configuration file containing sensitive values should **not** be committed to Git.

For example, if the real file contains a project ID or other sensitive configuration, add it to `.gitignore` where appropriate.

---

# OVHcloud authentication

Terraform needs to authenticate with OVHcloud before it can create resources.

The OVH provider supports several authentication methods. One option is to use an OVHcloud Application Key, Application Secret and Consumer Key. ([Terraform Registry][1])

The credentials can be supplied through environment variables rather than placing them directly in Terraform files.

For example:

```bash
export OVH_ENDPOINT="ovh-eu"
export OVH_APPLICATION_KEY="..."
export OVH_APPLICATION_SECRET="..."
export OVH_CONSUMER_KEY="..."
```

The OVH provider recognizes these environment variables automatically. ([Terraform Registry][1])

**Do not put these credentials directly into your Terraform files or commit them to GitHub.**

For more information:

[OVHcloud Terraform provider - Provider configuration](https://registry.terraform.io/providers/ovh/ovh/latest/docs)

[OVHcloud - How to use Terraform](https://docs.ovhcloud.com/en/guides/public-cloud/cross-functional/how-to-use-terraform)

---

# Basic Terraform workflow

Once authentication and the configuration are set up, the basic Terraform workflow is:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

## `terraform init`

Initializes the Terraform project and downloads the required providers.

```bash
terraform init
```

For this project, this downloads the OVHcloud Terraform provider.

---

## `terraform validate`

Checks whether the Terraform configuration is syntactically valid and internally consistent.

```bash
terraform validate
```

This is useful before creating any infrastructure.

---

## `terraform plan`

Shows what Terraform intends to change.

```bash
terraform plan
```

For example:

```text
Plan: 10 to add, 0 to change, 0 to destroy.
```

Always inspect the plan before applying it.

---

## `terraform apply`

Actually creates or modifies the infrastructure.

```bash
terraform apply
```

Terraform will normally ask you to confirm the changes.

The OVHcloud documentation also uses the standard `terraform init` and `terraform apply` workflow. ([OVHcloud Documentation][3])

---

# Understanding Terraform dependencies

One of the important things to understand in this project is that infrastructure has dependencies.

For example:

```text
Network
   ↓
Subnet
   ↓
Instance
```

An instance cannot use a subnet that does not exist yet.

Terraform can determine many of these dependencies automatically when one resource references another:

```hcl
subnet_id = module.network.subnet_id
```

Terraform understands that the network module needs to be created before the compute module can use its subnet.

This is one of the main advantages of describing infrastructure as code rather than manually creating resources in a specific order.

---

# Adapting the modules

The modules in this repository are examples and are not intended to be the only possible way to structure an OVHcloud environment.

Feel free to adapt them.

For example, you could change:

```text
3 instances
```

to:

```text
1 instance
```

or change:

```text
bronze
silver
gold
```

to a different storage structure.

You can also add new modules, such as:

```text
modules/
├── network/
├── compute/
├── storage/
├── IAM/
├── kubernetes/
└── monitoring/
```

The important part is to understand what each module is responsible for and how the modules communicate with each other through variables and outputs.

---

# Combining this project with the application repository

This Terraform repository can also be combined with my application repository:

[NoaHumention/wyr-app](https://github.com/NoaHumention/wyr-app)

The two repositories can have different responsibilities.

### Terraform repository

Responsible for creating the **infrastructure**:

```text
Terraform
   ↓
OVHcloud
   ├── Network
   ├── Compute
   ├── Storage
   ├── IAM
   └── Kubernetes
```

### Application repository

Responsible for the **application and deployment**:

```text
GitHub
   ↓
GitHub Actions
   ↓
Build application
   ↓
Deploy application
   ↓
OVHcloud infrastructure
```

This gives a useful separation between:

**Infrastructure as Code**

and

**Application CI/CD**

---

# Combining Terraform and GitHub Actions

Eventually, these two repositories can work together as part of a larger deployment architecture.

For example:

```text
                  GitHub
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
   Terraform repo        Application repo
          │                   │
          ▼                   ▼
   GitHub Actions        GitHub Actions
          │                   │
          ▼                   ▼
   Create/update         Build & deploy
   OVH infrastructure    application
          │                   │
          └─────────┬─────────┘
                    ▼
                 OVHcloud
```

Terraform can therefore create the environment in which the application runs, while the application repository can deploy new versions of the application into that environment.
---

# Learning goal

The final goal is to understand how to build a complete data platform on OVHcloud using Infrastructure as Code.

The project is therefore not only about getting Terraform to work.

It is about understanding the relationship between:

```text
Terraform
   ↓
Infrastructure
   ↓
OVHcloud
   ↓
Networking
   ↓
Compute
   ↓
Storage
   ↓
IAM
   ↓
Kubernetes
   ↓
Applications
   ↓
CI/CD
```

Once these concepts are understood individually, they can be combined into a larger, reproducible OVHcloud environment.

---

# Useful documentation

### OVHcloud

* [OVHcloud Terraform Provider](https://registry.terraform.io/providers/ovh/ovh/latest/docs)
* [OVHcloud Terraform Provider - Resources](https://registry.terraform.io/providers/ovh/ovh/latest/docs)
* [Using Terraform with OVHcloud](https://docs.ovhcloud.com/en/guides/manage-and-operate/terraform/at-ovhcloud)
* [How to use Terraform - OVHcloud Public Cloud](https://docs.ovhcloud.com/en/guides/public-cloud/cross-functional/how-to-use-terraform)

### Terraform

* [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
* [Terraform Modules](https://developer.hashicorp.com/terraform/language/modules)
* [Terraform Registry](https://registry.terraform.io/)

---

# Tips

* **Don't blindly copy-paste Terraform code.** Try to understand what each resource does.
* **Use ChatGPT as a tutor.** Ask for explanations and hints before asking for complete solutions.
* **Read the OVHcloud provider documentation.** The resource documentation often tells you exactly which arguments and attributes are available.
* **Use `terraform plan` frequently.** It is one of the best ways to understand what Terraform thinks your configuration means.
* **Start small.** Create one resource first, verify that it works, and then build on it.
* **Use modules once the configuration becomes more complex.** Don't introduce unnecessary abstraction too early.
* **Keep secrets out of Git.** Use environment variables, secret managers, or CI/CD secrets instead.
* **Adapt the examples.** The configuration in this repository is a learning environment, not a universal OVHcloud architecture.

[1]: https://registry.terraform.io/providers/ovh/ovh/latest/docs?utm_source=chatgpt.com "Docs overview | ovh/ovh | Terraform | Terraform Registry"
[2]: https://developer.hashicorp.com/terraform/registry/modules/use?utm_source=chatgpt.com "Find and use modules in the Terraform registry | Terraform | HashiCorp Developer"
[3]: https://docs.ovhcloud.com/en/guides/public-cloud/cross-functional/how-to-use-terraform?utm_source=chatgpt.com "How to use Terraform - OVHcloud Documentation"
