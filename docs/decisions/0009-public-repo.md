# 0009 The repo is public: no client material, no secrets, nothing personal

- **Date:** 13 Oct 2026 (repo created public), 15 Oct (client storage parked), 16 Oct (scan in the handover).
- **Context:** Public repos get free GitHub-hosted runners; everything committed and every release asset is public.
- **Decision:** Only studio code, invented sample businesses (marked Sample) and Sam's own cleared brands (Smart Mount,
  cleared 15 Oct) go here. No client briefs, photos, logos or finished client work; no API keys or tokens; no personal
  details about Sam or anyone (family, health, addresses, finances). Client material goes to a private home before the
  first client job (parked by Sam until there are paying clients).
- **Enforced in code:** `tools/verify.sh` gate `secrets`. Personal details and client material are not machine-checkable:
  every agent checks its own diff.
- **Status:** Active.
