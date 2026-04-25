# Order Service

## About

A service for managing orders in a distributed system, 
leveraging a microservices architecture and patterns such 
as **Saga**, **Outbox**, **event sourcing**, **compensation transactions**, 
and both **optimistic** and **pessimistic locking**.

### Service Interaction Flow

Typical flow:

1. **Create order**
2. **Send command to Stocks Service** (reserve products)
3. **Send command to Payment Service** (charge payment)
  - **On success:** commit order
  - **On failure:** rollback (release resources)

### Key Features
* Event-driven architecture
* High fault tolerance
* Guaranteed message delivery
* Loose coupling between services
* Easy scalability

___
## Overview

Order Service is responsible for creating and managing abstract product orders.

This service does not operate in isolation — it is part of a larger ecosystem of microservices:

* https://github.com/NormanwOw/Microservice.Stocks
 — product inventory management
* https://github.com/NormanwOw/Microservice.Payment
 — payment processing
* https://github.com/NormanwOw/Microservice.Publisher
 — event publishing (outbox delivery)
___
## Architecture

The project is built using:

* **Clean Architecture**
* **Hexagonal Architecture** (Ports & Adapters)  

***Core principles:***
business logic is isolated from infrastructure
dependencies point inward
high testability and maintainability
___
## Patterns Used
### Saga (Orchestration)

The service implements an orchestration-based saga:

Order Service acts as the orchestrator
coordinates interactions between:
* Stocks Service
* Payment Service  

handles both success and rollback scenarios

### Outbox Pattern

***To ensure reliable event delivery:***

events are written to an outbox table
published asynchronously via a dedicated service (Publisher)

***Benefits:***

* no event loss
consistency between database and message broker
### Concurrency Control

***Two approaches are used:***

* Optimistic Locking
  - entity versioning (version)
  - checked during updates
* Pessimistic Locking
  - database-level locking, 
used in critical sections (e.g., reservation)
___
## Interaction Diagram — Success path

![Diagram](assets/Orchestrator-success.png)
___
## Tech Stack
- `Python 3.14`
- `FastAPI`
- `SQLAlchemy`
- `Pydantic`
- `Kafka`
- `PostgreSQL`
- `Docker`

Additional tools:

- `uv`
- `ruff`
- `mypy`

## Getting Started
``` shell
$ git clone https://github.com/NormanwOw/Microservice.Order &&
cd Microservice.Order/main-deploy &&
chmod +x install.sh &&
./install.sh
```