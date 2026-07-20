---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Cloud Security

## Purpose

This note standardizes references for the cloud-security branch.

Use it to:
- keep cloud notes tied to official provider and high-signal guidance
- avoid generic cloud-security checklists with weak sourcing
- separate cloud target-domain security from DevSecOps delivery workflow
- help future agents choose consistent references

## Source of truth rule

For cloud-security notes, this registry is the primary source of truth.

Use it together with:
- [[index|Cloud Security Index]]
- [[index|Networking Index]]
- [[index|DevSecOps Index]]
- [[index|Attack Surface Mapping Index]]

---

## Reference selection policy

### Source priority

1. official cloud-provider documentation
2. official provider security best practices
3. CIS benchmarks and foundation guidance
4. OWASP / NIST guidance where cloud overlaps app or engineering security
5. secondary sources only when they add clear operational value

### Per-note target

- minimum 2 references
- ideal 3 references
- avoid broad provider-link dumping

### Labeling

Use:
- **Foundational**
- **Official Docs**
- **Mitigation**
- **Testing / Lab**
- **Benchmark**

---

# Cloud topic map

## cloud-security-basics

Preferred references:
- **Foundational:** AWS Shared Responsibility Model — https://aws.amazon.com/compliance/shared-responsibility-model/
- **Foundational:** Google Cloud shared responsibility and shared fate — https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate
- **Foundational:** Microsoft Cloud Adoption Framework security — https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/

## cloud-lab-infrastructure

Preferred references:
- **Official Docs:** AWS Free Tier — https://aws.amazon.com/free/
- **Official Docs:** AWS Budgets — https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- **Official Docs:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

## ssh-access-to-cloud-hosts

Preferred references:
- **Official Docs:** AWS EC2 key pairs and Linux instances — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
- **Official Docs:** AWS EC2 security groups — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html
- **Mitigation:** Microsoft guidance for securing privileged access — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model

## cloud-dns-and-certbot

Preferred references:
- **Official Docs:** AWS Route 53 Developer Guide — https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- **Official Docs:** Certbot documentation — https://eff-certbot.readthedocs.io/en/stable/
- **Official Docs:** Let's Encrypt documentation — https://letsencrypt.org/docs/

## cloud-iam-boundaries

Preferred references:
- **Official Docs:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Official Docs:** Google Cloud IAM best practices — https://cloud.google.com/iam/docs/using-iam-securely
- **Official Docs:** Microsoft Entra security operations for privileged accounts — https://learn.microsoft.com/en-us/entra/architecture/security-operations-privileged-accounts

## cloud-metadata-security

Preferred references:
- **Official Docs:** AWS EC2 Instance Metadata Service — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Official Docs:** Google Cloud VM metadata — https://cloud.google.com/compute/docs/metadata/overview
- **Official Docs:** Azure Instance Metadata Service — https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service

## public-cloud-storage-exposure

Preferred references:
- **Official Docs:** Amazon S3 Block Public Access — https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html
- **Official Docs:** Google Cloud Storage access control — https://cloud.google.com/storage/docs/access-control
- **Official Docs:** Azure Storage security recommendations — https://learn.microsoft.com/en-us/azure/storage/blobs/security-recommendations

## cloud-network-boundaries

Preferred references:
- **Official Docs:** AWS VPC security groups — https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- **Official Docs:** Google Cloud VPC firewall rules — https://cloud.google.com/firewall/docs/firewalls
- **Official Docs:** Azure network security groups — https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview

## cloud-secrets-management

Preferred references:
- **Official Docs:** AWS Secrets Manager best practices — https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html
- **Official Docs:** Google Secret Manager best practices — https://cloud.google.com/secret-manager/docs/best-practices
- **Official Docs:** Azure Key Vault security features — https://learn.microsoft.com/en-us/azure/key-vault/general/security-features

## cloud-logging-and-detection

Preferred references:
- **Official Docs:** AWS CloudTrail security best practices — https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html
- **Official Docs:** Google Cloud Audit Logs — https://cloud.google.com/logging/docs/audit
- **Official Docs:** Microsoft Defender for Cloud — https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction

---

## Registry usage rules

- Prefer provider docs for exact service behavior.
- Cross-link to Networking when the note depends on routing, DNS, TLS, metadata, or boundaries.
- Cross-link to DevSecOps when the note depends on deployment workflow, IaC, CI/CD, or secret lifecycle.
- Treat live cloud labs as cost-bearing environments: include budget, least privilege, teardown, and read-only checks where possible.
