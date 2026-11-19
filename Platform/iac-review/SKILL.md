---
name: iac-review
description: Review infrastructure as code against the plan, not the prose: what actually changes, what it costs, what it opens, and what cannot be undone. Use for /iac-review, "review this Terraform", "check this CloudFormation", "revisa esta infra", or before any apply.
---

# IaC review

**Review the plan, never the diff alone.** A three-line Terraform change can replace a database, and the diff does not say so. The plan does.

Get the plan output first, for the right workspace and the right state. A review without it is a review of someone's intention.

---

## 1. Read the plan for the four verbs

Count and classify every resource the plan touches:

- **create** — new surface, new cost, new permissions.
- **update in place** — usually safe, sometimes not.
- **replace (destroy then create)** — **the one that ruins afternoons.** Every replacement gets named explicitly in the review with what it is attached to. A replaced database, volume, or stateful resource is data loss unless something else protects it. A replaced load balancer or address is a DNS change people will feel.
- **destroy** — name each one and say what referenced it.

**Zero replacements and zero destroys is a sentence worth writing** when it is true. It is the single most reassuring line in an infrastructure review.

Then check the drift: does the state match reality, and is anything being "fixed" that a human changed by hand for a reason nobody wrote down (**why** answers that from the record).

## 2. Check what it opens

- **Network.** Any `0.0.0.0/0` ingress, a public subnet assignment, a security group referencing another by id versus by a wide CIDR, a database reachable from outside its tier.
- **Identity.** Wildcard actions, wildcard resources, a trust policy that trusts too broadly, a role a service did not need, a long-lived access key where a federated identity or an instance role would do.
- **Storage.** Public access blocks still on, encryption at rest with the key you meant, bucket policies, versioning and lifecycle where the data matters.
- **Secrets.** Nothing in a variable default, a committed tfvars, a user-data script, a container environment block in plain text, or the state file. **The state file holds everything the plan touched**, so it is encrypted, remote, versioned, locked, and access to it is access to the secrets.

## 3. Check what it costs

Every created resource is a recurring bill. Name the ones that cost whether or not anything uses them: an idle load balancer, a NAT gateway, provisioned IOPS, a reserved address, a cluster's control plane, a managed service's minimum, log retention measured in years, cross-AZ and egress traffic the topology forces.

Give the monthly delta with the assumption behind it (**cost-per-request** for the per-request share, **cloud-cost-forecast** for the bill-level view). A plan that adds $600 a month in NAT gateways for one cron job is a design finding, not a cost finding.

## 4. Check the operational basics

- **Tagged** so the bill can be allocated: owner, environment, product, cost center. Untagged resources are tomorrow's unallocated spend.
- **Observable** on arrival: metrics, logs with a retention you chose, an alarm on the thing that degrades (**observability-baseline**).
- **Backed up**, with the retention and the restore path stated for anything stateful. A snapshot nobody has restored from is not a backup.
- **Deletion protection** on the resources where a replacement would be unrecoverable.
- **Idempotent and declarative**, with no `local-exec` doing imperative work the provider should do (principle-make-operations-idempotent).
- **Modules pinned** to a version, not to a branch. A provider or module floating on `main` makes the plan non-reproducible.

## 5. Verdict

```
IAC REVIEW — <stack>, workspace <name>

Plan: 7 create, 3 update, 1 REPLACE, 0 destroy
  REPLACE: aws_db_instance.primary  (engine_version change forces replacement)

Opens:   nothing new publicly reachable
Costs:   +$180/month (NAT gateway $65, RDS class bump $115)
Ops:     tags ok, alarm missing on the new queue's age
Undo:    replacement is NOT reversible, no final snapshot configured

VERDICT: DO NOT APPLY — the primary database is being replaced
```

**Any replacement or destroy of a stateful resource means the apply waits for an explicit human decision**, with the data protection in place first. Never apply on the strength of your own review. For an irreversible change, state plainly that it cannot be undone and let the owner decide.
