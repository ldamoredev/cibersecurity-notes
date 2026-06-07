# Reference Registry — Cloud Security

## Propósito

Esta nota estandariza las referencias para la rama cloud-security.

Usala para:
- mantener las notas cloud vinculadas a documentación oficial de providers y guía de alta señal
- evitar checklists genéricas de cloud-security con sourcing débil
- separar seguridad del target-domain cloud del workflow de delivery DevSecOps
- ayudar a agentes futuros a elegir referencias consistentes

## Regla de fuente de verdad

Para notas de cloud-security, este registry es la fuente de verdad primaria.

Usalo junto con:
- [[index|Cloud Security Index]]
- [[index|Networking Index]]
- [[index|DevSecOps Index]]
- [[index|Attack Surface Mapping Index]]

---

## Política de selección de referencias

### Prioridad de fuentes

1. documentación oficial de cloud providers
2. security best practices oficiales del provider
3. benchmarks CIS y guía fundacional
4. guía OWASP / NIST cuando cloud se superpone con app security o engineering security
5. fuentes secundarias solo cuando agregan valor operacional claro

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias
- evitar broad provider-link dumping

### Etiquetas

Usar:
- **Fundamental**
- **Docs oficiales**
- **Mitigación**
- **Testing / Lab**
- **Benchmark**

---

# Mapa de temas cloud

## cloud-security-basics

Referencias preferidas:
- **Fundamental:** AWS Shared Responsibility Model — https://aws.amazon.com/compliance/shared-responsibility-model/
- **Fundamental:** Google Cloud shared responsibility and shared fate — https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate
- **Fundamental:** Microsoft Cloud Adoption Framework security — https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/

## cloud-lab-infrastructure

Referencias preferidas:
- **Docs oficiales:** AWS Free Tier — https://aws.amazon.com/free/
- **Docs oficiales:** AWS Budgets — https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- **Docs oficiales:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

## ssh-access-to-cloud-hosts

Referencias preferidas:
- **Docs oficiales:** AWS EC2 key pairs and Linux instances — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
- **Docs oficiales:** AWS EC2 security groups — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html
- **Mitigación:** Microsoft guidance for securing privileged access — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model

## cloud-dns-and-certbot

Referencias preferidas:
- **Docs oficiales:** AWS Route 53 Developer Guide — https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- **Docs oficiales:** Certbot documentation — https://eff-certbot.readthedocs.io/en/stable/
- **Docs oficiales:** Let's Encrypt documentation — https://letsencrypt.org/docs/

## cloud-iam-boundaries

Referencias preferidas:
- **Docs oficiales:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Docs oficiales:** Google Cloud IAM best practices — https://cloud.google.com/iam/docs/using-iam-securely
- **Docs oficiales:** Microsoft Entra security operations for privileged accounts — https://learn.microsoft.com/en-us/entra/architecture/security-operations-privileged-accounts

## cloud-metadata-security

Referencias preferidas:
- **Docs oficiales:** AWS EC2 Instance Metadata Service — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Docs oficiales:** Google Cloud VM metadata — https://cloud.google.com/compute/docs/metadata/overview
- **Docs oficiales:** Azure Instance Metadata Service — https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service

## public-cloud-storage-exposure

Referencias preferidas:
- **Docs oficiales:** Amazon S3 Block Public Access — https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html
- **Docs oficiales:** Google Cloud Storage access control — https://cloud.google.com/storage/docs/access-control
- **Docs oficiales:** Azure Storage security recommendations — https://learn.microsoft.com/en-us/azure/storage/blobs/security-recommendations

## cloud-network-boundaries

Referencias preferidas:
- **Docs oficiales:** AWS VPC security groups — https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- **Docs oficiales:** Google Cloud VPC firewall rules — https://cloud.google.com/firewall/docs/firewalls
- **Docs oficiales:** Azure network security groups — https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview

## cloud-secrets-management

Referencias preferidas:
- **Docs oficiales:** AWS Secrets Manager best practices — https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html
- **Docs oficiales:** Google Secret Manager best practices — https://cloud.google.com/secret-manager/docs/best-practices
- **Docs oficiales:** Azure Key Vault security features — https://learn.microsoft.com/en-us/azure/key-vault/general/security-features

## cloud-logging-and-detection

Referencias preferidas:
- **Docs oficiales:** AWS CloudTrail security best practices — https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html
- **Docs oficiales:** Google Cloud Audit Logs — https://cloud.google.com/logging/docs/audit
- **Docs oficiales:** Microsoft Defender for Cloud — https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction

---

## Reglas de uso del registry

- Preferí docs del provider para comportamiento exacto del servicio.
- Cross-link a Networking cuando la nota depende de routing, DNS, TLS, metadata o límites.
- Cross-link a DevSecOps cuando la nota depende de workflow de deployment, IaC, CI/CD o lifecycle de secrets.
- Tratá labs cloud live como entornos con costo: incluí budget, least privilege, teardown y checks read-only cuando sea posible.
