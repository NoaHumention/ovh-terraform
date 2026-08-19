# Learning Terraform on OVHcloud: From Terraform Basics to a Data Lake

## Introduction

This learning path is designed to take you from your current Terraform knowledge—being able to create one or multiple OVHcloud instances—to building a complete, reproducible **data lake infrastructure on OVHcloud using Terraform**.

The goal is not simply to learn Terraform syntax.

The goal is to understand how to use Terraform to design, provision, connect, secure, and eventually operate the infrastructure underneath a data platform.

The learning path therefore combines three areas:

1. **Terraform**
2. **OVHcloud infrastructure**
3. **Data lake architecture**

Each stage introduces a small number of new concepts and ends with a practical exercise.

---

# 1. What is Terraform?

Terraform is an **Infrastructure as Code (IaC)** tool.

Instead of manually creating infrastructure through a cloud provider's web interface, you describe the desired infrastructure in configuration files.

For example:

```hcl
resource "ovh_cloud_project_instance" "app_server" {
  service_name = var.service_name
  region       = var.region
  name         = "my-server"

  # ...
}
```

Terraform then communicates with the cloud provider's API and attempts to make the real infrastructure match the configuration.

Conceptually:

```text
Terraform configuration
        │
        ▼
Terraform
        │
        ▼
OVHcloud API
        │
        ▼
Actual infrastructure
```

## What Terraform does

Terraform is primarily responsible for **infrastructure provisioning and lifecycle management**.

It can, for example:

- create infrastructure
- modify infrastructure
- delete infrastructure
- connect resources together
- manage dependencies between resources
- keep track of infrastructure through Terraform state
- make infrastructure reproducible
- allow infrastructure to be reviewed before deployment
- allow infrastructure to be version-controlled with Git
- manage infrastructure across environments

For this learning project, Terraform will eventually manage things such as:

```text
OVHcloud
│
├── Networks
├── Subnets
├── Instances
├── Object Storage
├── IAM
├── Databases
├── Container registries
└── Other cloud resources
```

The OVHcloud Terraform provider is the interface between Terraform and OVHcloud. The current provider is available through the Terraform Registry.

**OVHcloud Terraform provider documentation:**

https://registry.terraform.io/providers/ovh/ovh/latest/docs

The provider documentation contains the available resources, data sources, arguments, attributes, and examples.

---

## What Terraform does NOT do

This distinction is extremely important for the data-lake project.

Terraform is **not** a general-purpose automation tool for everything that happens inside your infrastructure.

For example, Terraform should not normally be responsible for:

```text
Terraform
   │
   ├── Create VM                    ✓
   ├── Create network               ✓
   ├── Create object storage        ✓
   ├── Configure IAM                ✓
   │
   ├── Process 10 TB of data       ✗
   ├── Transform CSV into Parquet  ✗
   ├── Run daily ETL jobs          ✗
   ├── Analyze datasets            ✗
   └── Perform business analytics  ✗
```

Those responsibilities belong to other tools.

A useful mental model is:

```text
Terraform
    │
    ▼
Infrastructure
    │
    ├── Compute
    ├── Networking
    ├── Storage
    └── Security
            │
            ▼
       Data platform
            │
            ├── Ingestion
            ├── Processing
            ├── Transformation
            └── Analytics
```

Terraform creates the **environment in which the data platform runs**.

---

# 2. Why OVHcloud?

This learning path uses OVHcloud because it provides a broad cloud infrastructure portfolio while being a European cloud provider.

For European companies, one potentially important consideration is **data sovereignty and jurisdiction**.

OVHcloud states that customers can host personal data exclusively within the European Union and highlights measures around European data protection and sovereignty.

This can be particularly relevant for organizations dealing with:

- GDPR-regulated data
- customer information
- employee information
- healthcare-related data
- financial information
- government data
- other sensitive business information

However, an important distinction is:

> **Using a European cloud provider does not automatically make an application GDPR-compliant.**

Compliance depends on the entire architecture, configuration, processes, contracts, access controls, data flows, and legal requirements.

OVHcloud's European positioning can nevertheless be an important architectural consideration when choosing where data infrastructure should run.

For a data lake, this matters because the lake may eventually contain very large amounts of potentially sensitive information.

---

# 3. Terraform + OVHcloud

Terraform and OVHcloud fit together through the **OVHcloud Terraform provider**.

The provider translates Terraform resources into OVHcloud API operations.

For example:

```text
Terraform

resource "ovh_cloud_project_instance" ...

             │
             ▼

      OVHcloud provider

             │
             ▼

        OVHcloud API

             │
             ▼

      OVHcloud instance
```

Your current configuration already uses this relationship.

You have:

```hcl
resource "ovh_cloud_project_instance" "app_server" {
  # ...
}
```

Terraform interprets that resource using the OVHcloud provider.

The provider documentation should therefore become one of your primary reference sources while learning.

### Useful OVHcloud Terraform references

- **[OVHcloud Terraform provider documentation](https://registry.terraform.io/providers/ovh/ovh/latest/docs)**
- **[OVHcloud project data source](https://registry.terraform.io/providers/ovh/ovh/latest/docs/data-sources/cloud_project)**
- **[OVHcloud Object Storage-related documentation](https://registry.terraform.io/providers/ovh/ovh/latest/docs/data-sources/cloud_project_storages)**
- **[OVHcloud managed database resource](https://registry.terraform.io/providers/ovh/ovh/latest/docs/resources/cloud_project_database)**
- **[OVHcloud Container Registry resource](https://registry.terraform.io/providers/ovh/ovh/latest/docs/resources/cloud_project_containerregistry)**

The provider documentation is especially important because Terraform syntax alone does not tell you what OVHcloud-specific resources and attributes are available.

---

# 4. What is a Data Lake?

Before building one, it is important to understand what a data lake actually is.

A **data lake** is a data storage and processing architecture designed to store large amounts of data, often in its original/raw form, while allowing that data to be processed and transformed for different purposes.

A simple data lake might look like:

```text
                    Data Sources
                         │
                         ▼
                  ┌─────────────┐
                  │   Ingestion │
                  └──────┬──────┘
                         │
                         ▼
                ┌─────────────────┐
                │     BRONZE      │
                │                 │
                │    Raw data     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     SILVER      │
                │                 │
                │ Cleaned data    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │      GOLD       │
                │                 │
                │ Analytics data  │
                └────────┬────────┘
                         │
                         ▼
                    Analytics
```

The names **Bronze, Silver, and Gold** are a common way of describing progressively processed layers.

## Bronze

Bronze contains data close to its original form.

For example:

```text
bronze/
├── customers/
├── orders/
├── products/
└── events/
```

The goal is generally to preserve the original data.

---

## Silver

Silver contains cleaned, validated, normalized, or transformed data.

For example:

```text
silver/
├── customers/
├── orders/
└── products/
```

An ingestion system might take:

```text
raw CSV
```

and produce:

```text
cleaned Parquet
```

---

## Gold

Gold contains data prepared for specific analytical use cases.

For example:

```text
gold/
├── daily_revenue/
├── customer_metrics/
├── product_performance/
└── sales_dashboard/
```

The important concept is:

> **A data lake is not simply a large storage bucket.**

A useful data lake requires considerations around:

- storage
- data formats
- schemas
- ingestion
- processing
- security
- access control
- metadata
- data quality
- lifecycle
- networking
- monitoring
- analytics

Terraform will primarily help us build the **infrastructure layer** underneath these components.

---

# 5. The Final Goal

The final learning project will gradually evolve toward an architecture similar to:

```text
                         Data Sources
                              │
                              ▼
                       ┌──────────────┐
                       │  Ingestion   │
                       └──────┬───────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  OVH Object Storage│
                    │                    │
                    │       BRONZE       │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Processing Cluster │
                    │                    │
                    │ Spark / workers    │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  OVH Object Storage│
                    │                    │
                    │       SILVER       │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  OVH Object Storage│
                    │                    │
                    │        GOLD        │
                    └─────────┬──────────┘
                              │
                              ▼
                         Analytics
```

Terraform will eventually manage much of the infrastructure around this architecture.

---

# 6. Your Current Starting Point

You already know how to create multiple OVHcloud instances using Terraform.

Your current mental model is approximately:

```text
Terraform
    │
    ▼
OVHcloud
    │
    ├── Instance 1
    ├── Instance 2
    └── Instance 3
```

For example, you already understand concepts such as:

```hcl
for_each = toset(var.instance_names)
```

and data sources such as:

```hcl
data "ovh_cloud_project_flavors" "app" {
  # ...
}
```

and:

```hcl
data "ovh_cloud_project_images" "linux" {
  # ...
}
```

This is a good starting point.

The next step is to move from:

> **"I can create servers."**

to:

> **"I can describe an entire infrastructure system."**

---

# 7. Learning Path

## Stage 0 — Terraform Foundations

### Goal

Turn your current Terraform experiment into a clean Terraform project.

### Learn

- Terraform configuration structure
- providers
- resources
- data sources
- variables
- outputs
- state
- `.terraform.lock.hcl`
- `.gitignore`
- `terraform init`
- `terraform plan`
- `terraform apply`
- `terraform destroy`
- Terraform dependency graphs

### Target structure

Eventually:

```text
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── terraform.tfvars
└── .gitignore
```

### Exercise

Take your existing configuration and separate the different responsibilities into appropriate Terraform files.

Do not introduce modules yet.

### Milestone

You should be able to explain:

> What does Terraform know about my infrastructure, and where does Terraform store that information?

<details>
<summary>💡 Hint — I'm stuck on how to split my Terraform files</summary>

Terraform does not require everything to be in `main.tf`.

Ask yourself which parts describe:

- provider/Terraform configuration
- variables
- resources
- outputs

Terraform automatically loads `.tf` files in the same directory.

</details>

<details>
<summary>💡 Hint — I'm stuck on Terraform state</summary>

Look into the purpose of:

```text
terraform.tfstate
```

and the command:

```text
terraform show
```

The key concept is that Terraform needs to keep track of the relationship between your configuration and infrastructure.

</details>

---

# Stage 1 — Variables, Locals, Outputs and Expressions

### Goal

Make your infrastructure configurable rather than hard-coded.

Your current configuration contains hard-coded values such as:

```hcl
name_filter = "b3-8"
```

and:

```hcl
name = "testing_key"
```

These should gradually become configurable.

### Learn

- variables
- variable types
- validation
- locals
- outputs
- lists
- maps
- sets
- objects
- `for` expressions
- conditional expressions

### Exercise

Make the following configurable:

```text
environment
region
flavor
image
SSH key
instance names
```

### Milestone

You should be able to change the environment or configuration without rewriting the infrastructure logic.

<details>
<summary>💡 Hint — I'm stuck on making a value configurable</summary>

Ask:

> "Should this value be a variable?"

If the answer is yes, define:

```hcl
variable "..." {
  type = ...
}
```

Then reference it with:

```hcl
var....
```

</details>

<details>
<summary>💡 Hint — I'm stuck on transforming a list</summary>

Look at Terraform's:

```text
for expressions
```

For example, Terraform can transform collections using:

```hcl
[
  for item in collection :
  ...
]
```

</details>

<details>
<summary>💡 Hint — I'm stuck on choosing between list, set and map</summary>

Think about whether:

- order matters
- duplicates should be allowed
- values need keys

Then look at Terraform's collection types.

Your current use of:

```hcl
toset(var.instance_names)
```

is already an example of this concept.

</details>

---

# Stage 2 — Dependencies and Terraform's Resource Graph

### Goal

Understand how Terraform decides what needs to be created first.

A future data lake might have:

```text
Network
   │
   ├── Subnet
   │
   └── Compute
          │
          └── Processing cluster
```

and:

```text
Object Storage
      │
      └── Processing cluster accesses it
```

### Learn

- implicit dependencies
- explicit dependencies
- references
- `depends_on`
- resource IDs
- data sources
- `count`
- `for_each`

### Exercise

Create:

```text
1 private network
1 subnet
3 instances
```

and connect the instances to the private network.

### Milestone

You should be able to look at your Terraform configuration and predict which resources Terraform must create first.

<details>
<summary>💡 Hint — I'm stuck on creating a dependency</summary>

First ask whether Terraform can already infer the dependency from a reference such as:

```hcl
network_id = some_resource.example.id
```

Terraform normally builds the dependency automatically.

Only investigate:

```hcl
depends_on
```

when Terraform cannot infer the relationship from the configuration.

</details>

<details>
<summary>💡 Hint — I'm stuck on creating multiple resources</summary>

You already used:

```hcl
for_each
```

to create multiple instances.

Look at whether the collection you provide to `for_each` should be a:

```text
map
```

or:

```text
set
```

</details>

---

# Stage 3 — Terraform Modules

### Goal

Turn repeated infrastructure concepts into reusable modules.

Eventually:

```text
data-lake/
│
├── main.tf
├── variables.tf
├── outputs.tf
│
└── modules/
    ├── network/
    ├── storage/
    └── compute/
```

### Learn

- root modules
- child modules
- module inputs
- module outputs
- module composition
- module interfaces

### Exercise

Turn your existing instance configuration into a `compute` module.

Conceptually:

```hcl
module "compute" {
  source = "./modules/compute"

  # inputs
}
```

### Milestone

You should understand:

> A module is an interface around infrastructure, not merely a folder containing Terraform files.

<details>
<summary>💡 Hint — I'm stuck on what belongs inside a module</summary>

Start with a logical infrastructure component.

Ask:

> "Would I want to create this component more than once, or use it independently?"

Good candidates might eventually be:

```text
network
compute
storage
```

</details>

<details>
<summary>💡 Hint — I'm stuck on passing values into a module</summary>

Think in terms of:

```text
root module
    │
    │ input
    ▼
child module
    │
    │ output
    ▼
root module
```

Look at:

```hcl
variable "..."
```

inside the child module and:

```hcl
module.example.output_name
```

from the parent.

</details>

---

# Stage 4 — OVHcloud Networking

### Goal

Build the private network that will eventually host your data-processing infrastructure.

Your current instances use:

```hcl
network {
  public = true
}
```

For the data-lake architecture, we want to understand private networking and reduce unnecessary public exposure.

Conceptually:

```text
Internet
    │
    ▼
Access layer
    │
    ▼
┌─────────────────────────────┐
│       Private Network       │
│                             │
│  ┌───────┐ ┌───────┐       │
│  │Worker │ │Worker │ ...   │
│  └───────┘ └───────┘       │
│                             │
└─────────────────────────────┘
```

### Learn

- private networks
- subnets
- private IPs
- public IPs
- network interfaces
- security
- network segmentation

### Exercise

Create:

```text
private network
      │
      └── subnet
             │
             ├── instance 1
             ├── instance 2
             └── instance 3
```

### Milestone

You should be able to explain how the compute nodes communicate privately.

<details>
<summary>💡 Hint — I'm stuck on finding the correct OVH resource</summary>

Don't guess the resource name.

Search the OVHcloud Terraform provider documentation for:

```text
network
private network
subnet
```

Start from the provider documentation:

https://registry.terraform.io/providers/ovh/ovh/latest/docs

</details>

<details>
<summary>💡 Hint — I'm stuck on connecting the instance to the network</summary>

Look at the schema for:

```text
ovh_cloud_project_instance
```

Specifically investigate its:

```text
network
```

configuration.

The important question is:

> What attributes does this version of the OVH provider actually accept?

</details>

---

# Stage 5 — Object Storage

### Goal

Build the actual storage foundation of your data lake.

This is a major conceptual transition.

Instead of:

```text
Data
  ↓
VM disk
```

we move toward:

```text
Data
  ↓
Object Storage
```

A simplified layout might be:

```text
Object Storage
│
├── bronze/
│
├── silver/
│
└── gold/
```

### Learn

- object storage
- buckets/containers
- S3 concepts
- object keys
- prefixes
- storage lifecycle
- versioning
- durability
- access credentials

### Exercise

Provision the storage infrastructure required for your first data lake.

Then represent the conceptual layers:

```text
bronze
silver
gold
```

### Important concept

S3-compatible object storage does not necessarily work like a traditional filesystem.

For example:

```text
bronze/orders/2026/08/orders.parquet
```

is generally an **object key/prefix**, not necessarily a traditional directory.

### Milestone

You should be able to explain:

> Why is object storage a better foundation for a data lake than putting all the data on VM disks?

<details>
<summary>💡 Hint — I'm stuck on finding the OVH Object Storage Terraform resource</summary>

Search the OVH Terraform documentation for:

```text
storage
S3
container
object storage
```

You can also inspect the provider's storage-related data sources.

For example, the current provider documents S3-compatible storage containers.

</details>

<details>
<summary>💡 Hint — I'm stuck on understanding bronze/silver/gold</summary>

Think of the three layers as different **data states**, not necessarily three different physical storage systems.

Ask:

```text
What was the original data?
What processing happened to it?
What is the final analytical representation?
```

</details>

---

# Stage 6 — IAM and Security

### Goal

Control who and what can access your data lake.

Eventually you might have:

```text
                 Object Storage
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
   Ingestion        Spark        Analytics
       │              │              │
     WRITE        READ/WRITE       READ
     Bronze       Bronze/Silver    Gold
```

The goal is **least privilege**.

### Learn

- IAM
- access policies
- credentials
- service accounts
- API keys
- secrets
- sensitive Terraform variables
- credential rotation
- least privilege

### Exercise

Design access for:

```text
ingestion
processing
analytics
```

without giving every component unrestricted access.

### Milestone

You should be able to answer:

> If one processing server is compromised, what data can the attacker access?

<details>
<summary>💡 Hint — I'm stuck on discovering the available IAM resources</summary>

Use the OVH provider documentation and search for:

```text
IAM
policy
role
permission
identity
```

Don't assume that an AWS IAM resource has an identical OVHcloud equivalent.

</details>

<details>
<summary>💡 Hint — I'm stuck on handling credentials</summary>

First identify which values are secrets.

Then investigate:

```text
sensitive = true
```

and environment variables.

The OVH provider documentation also explains authentication mechanisms and recommends approaches that avoid putting secrets directly into source repositories.

</details>

---

# Stage 7 — Compute Cluster

### Goal

Turn your knowledge of multiple instances into a processing cluster.

Conceptually:

```text
             ┌──────────────┐
             │ Master/Head  │
             └──────┬───────┘
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Worker 1  Worker 2  Worker 3
```

This infrastructure could eventually host a processing framework such as Apache Spark.

### Learn

- cluster architecture
- master/worker concepts
- cloud-init
- bootstrap scripts
- service discovery
- configuration
- scaling
- node roles

### Exercise

Terraform should create:

```text
1 master
3 workers
```

and configure them sufficiently to form a processing cluster.

### Milestone

Destroy the cluster.

Then recreate it.

The infrastructure should be reproducible.

<details>
<summary>💡 Hint — I'm stuck on assigning different roles to instances</summary>

Consider whether every instance should have the same configuration.

A collection such as:

```text
master
worker
worker
worker
```

may be easier to model as structured data rather than simply a list of names.

Look at Terraform:

```text
maps
objects
for_each
```

</details>

<details>
<summary>💡 Hint — I'm stuck on configuring the server after Terraform creates it</summary>

Terraform creates the infrastructure, but something still needs to configure the operating system.

Investigate:

```text
cloud-init
user_data
bootstrap scripts
```

Then think about the boundary between:

```text
Terraform → infrastructure
configuration management → machine configuration
```

</details>

---

# Stage 8 — Build the Data Pipeline

### Goal

Create your first real data pipeline.

Start with something deliberately simple.

For example:

```text
customers.csv
orders.csv
products.csv
```

The pipeline becomes:

```text
CSV
 │
 ▼
Ingestion
 │
 ▼
BRONZE
 │
 ▼
Processing
 │
 ▼
SILVER
 │
 ▼
Aggregation
 │
 ▼
GOLD
```

### Learn

- ingestion
- ETL/ELT
- schemas
- data quality
- transformations
- Parquet
- partitioning
- batch processing
- idempotency

### Example

Raw data:

```text
orders.csv
```

Bronze:

```text
bronze/orders/
```

Silver:

```text
silver/orders/
```

Gold:

```text
gold/daily_revenue/
```

### Milestone

You should be able to take raw data and produce an analytics-ready dataset.

At this point, you have built a small but real data lake.

<details>
<summary>💡 Hint — I'm stuck on what should happen in Bronze</summary>

Bronze should generally preserve the raw/source representation.

Ask:

> "If my transformation code breaks tomorrow, can I reconstruct the processed data from Bronze?"

If the answer is no, reconsider what you're storing.

</details>

<details>
<summary>💡 Hint — I'm stuck on what format to use for Silver and Gold</summary>

Investigate:

```text
Parquet
```

and why columnar formats are useful for analytical workloads.

</details>

---

# Stage 9 — Production Terraform

### Goal

Make your infrastructure safe and maintainable.

Your workflow should eventually resemble:

```text
Git
 │
 ▼
Pull Request
 │
 ├── terraform fmt
 ├── terraform validate
 └── terraform plan
          │
          ▼
       Review
          │
          ▼
       Apply
```

### Learn

- remote state
- state locking
- environments
- development/staging/production
- CI/CD
- formatting
- validation
- linting
- security scanning
- infrastructure drift

### Example structure

```text
environments/
├── dev/
├── staging/
└── prod/

modules/
├── network/
├── storage/
└── compute/
```

### Milestone

Someone else should be able to clone your repository and understand:

> What infrastructure does this create, and how can I safely change it?

<details>
<summary>💡 Hint — I'm stuck on remote state</summary>

First understand why local state becomes problematic when multiple people or automation systems work with the same infrastructure.

Then investigate:

```text
Terraform backend
remote state
state locking
```

OVHcloud's Terraform provider documentation also contains information about using OVHcloud Object Storage for Terraform state.

</details>

<details>
<summary>💡 Hint — I'm stuck on validating my configuration</summary>

Start with the Terraform commands you already have available:

```text
terraform fmt
terraform validate
terraform plan
```

Understand what each command catches and what it does not catch.

</details>

---

# Stage 10 — Final Data Lake

## Capstone Project

Bring everything together.

Your final architecture should resemble:

```text
                         Internet
                            │
                            ▼
                    ┌───────────────┐
                    │ Data Ingestion│
                    └───────┬───────┘
                            │
                            ▼
                 ┌────────────────────┐
                 │   Object Storage   │
                 │                    │
                 │      BRONZE        │
                 └─────────┬──────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Processing      │
                  │ Cluster         │
                  │                 │
                  │ Master + Workers│
                  └────────┬────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │   Object Storage   │
                 │                    │
                 │      SILVER        │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │   Object Storage   │
                 │                    │
                 │       GOLD         │
                 └─────────┬──────────┘
                           │
                           ▼
                    Analytics / SQL
```

Terraform should manage the infrastructure surrounding this architecture:

```text
                         Terraform
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
       Network           Storage             Compute
          │                  │                  │
          │                  ├── Bronze         ├── Master
          │                  ├── Silver         └── Workers
          │                  └── Gold
          │
          └── Private networking

                             │
                             ▼
                           IAM
                             │
                             ▼
                         Security
```

---

# 8. Final Learning Map

The complete progression is:

```text
CURRENT KNOWLEDGE
      │
      ▼
┌──────────────────────────────┐
│ 1. Terraform foundations     │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 2. Variables & expressions   │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 3. Dependencies              │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 4. Modules                   │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 5. OVHcloud networking       │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 6. Object Storage            │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 7. IAM & security            │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 8. Compute cluster           │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 9. Data pipeline             │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 10. Production Terraform     │
└──────────────┬───────────────┘
               ▼
          DATA LAKE
```

---

# 9. How We Will Work Through This

The recommended approach is **interactive rather than solution-driven**.

For each stage:

```text
1. Learn the concept
       ↓
2. See a small example
       ↓
3. Complete an exercise
       ↓
4. Run terraform plan
       ↓
5. Inspect the result
       ↓
6. Fix problems
       ↓
7. Explain why it works
       ↓
8. Move to the next stage
```

You should attempt the exercises yourself.

When you get stuck, use the dropdown hints progressively.

The hints should follow this pattern:

```text
Level 1
"What concept should I investigate?"

        ↓

Level 2
"What Terraform feature/function is relevant?"

        ↓

Level 3
"What should I look for in the OVH provider documentation?"

        ↓

Level 4
"How should the pieces fit together?"
```

The objective is **not** to memorize Terraform syntax.

The objective is to develop the ability to look at an infrastructure problem and think:

> What resources do I need?

> What information does Terraform need?

> What depends on what?

> Which Terraform construct represents this?

> Which OVHcloud resource provides this capability?

> What should Terraform manage, and what should another tool manage?

That way, by the end of the project, you aren't just able to reproduce this particular data lake—you'll have learned how to design and provision other infrastructure systems with Terraform.

---

# 10. Primary Reference

Keep the following page bookmarked throughout the entire learning path:

**OVHcloud Terraform Provider — Documentation**

https://registry.terraform.io/providers/ovh/ovh/latest/docs

The current provider documentation lists the available OVHcloud Terraform resources and data sources and is the authoritative place to check the provider's current schema and supported functionality.

When an exercise says:

> "Find the appropriate OVHcloud resource"

the expected workflow is:

```text
Problem
   │
   ▼
Identify the infrastructure concept
   │
   ▼
Search OVH Terraform documentation
   │
   ▼
Find candidate resource/data source
   │
   ▼
Read its schema
   │
   ▼
Build Terraform configuration
   │
   ▼
terraform validate
   │
   ▼
terraform plan
```

This is a skill you should deliberately practice throughout the course.

---

# End Goal

At the beginning of this learning path, your Terraform mindset is:

```text
"I can create instances."
```

By the end, it should be:

```text
"I can design an infrastructure system,
represent it as Terraform,
provision it on OVHcloud,
secure it,
connect its components,
and reproduce it reliably."
```

And the final practical result will be:

```text
                 Terraform
                     │
                     ▼
              ┌─────────────┐
              │ OVHcloud    │
              │ Data Lake   │
              └──────┬──────┘
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
    Network       Storage        Compute
       │             │             │
       │        Bronze/Silver/     │
       │             Gold          │
       │                           │
       └─────────────┬─────────────┘
                     ▼
               Data Processing
                     │
                     ▼
                 Analytics
```

**The first practical step is Stage 0: refactor your current instance configuration into a clean Terraform project without changing what it actually deploys.**