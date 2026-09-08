# Java/Spring Uplift Contract

The workflow must treat these as potentially protected contracts when the repository exposes them:

- public Java method signatures;
- public constructors;
- service interfaces;
- REST endpoint paths and HTTP methods;
- request/response DTO fields and serialization contracts;
- event/message names and payloads;
- externally consumed configuration properties;
- persistence-facing contracts explicitly declared by the plan;
- module/package boundaries explicitly declared by the plan.

A contract is not globally immutable. A planned migration may intentionally change a contract, but the accepted Plan must identify the change explicitly and the Verifier must verify the intended new contract.

For Spring migrations, pay special attention to:

- `javax.*` versus `jakarta.*` namespaces;
- Spring Security configuration APIs;
- Spring MVC/WebFlux APIs;
- Spring Data/JPA/Hibernate behavior;
- configuration property names;
- bean definitions and application startup;
- serialization and validation annotations;
- test/application context configuration.
