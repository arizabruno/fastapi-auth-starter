
# FastAPI Auth Starter

## Requirements
- Python 3.10.6 or higher
- pip
- Docker
- Terraform
- AWS Account
- AWS CLI

## Setup Instructions

### 1. Install Dependencies

To install necessary Python packages, run:

```bash
make install
```

This command updates pip and installs dependencies listed in `requirements.txt`.

### 2. I AM Policies

Minimal I AM Policies:

```bash
AccessKeyCustom
AmazonEC2ContainerRegistryFullAccess
AmazonEC2FullAccess
AmazonRDSFullAccess
AmazonSESFullAccess
```

### 3. Database Setup

#### 1. Inititalizing Terraform

```bash
make init_db_infra
```

#### 2. Creating RDS instance

```bash
make apply_db_infra
```

#### 3. Destroying resources

```bash
make destroy_db_infra
```

#### 4. Database schema

```ddl

create table users
(
    user_id         serial,
    email           varchar(255) default 'guest@namex.com'::character varying,
    username        varchar(255) default 'guest'::character varying not null,
    hashed_password varchar(255),
    created_at      timestamp    default now(),
    roles           text         default 'user'::text
);

```

### 4. Running the API Locally

To start the API server on your local machine, run:

```bash
make run_api
```

This will launch the API at `http://0.0.0.0:8080`. The `--reload` flag enables hot reloading, allowing you to see changes in real-time without restarting the server.

### 5. Docker Setup

#### Building the Docker Image

To build a Docker image for the API, run:

```bash
make docker_build
```

#### Running the Docker Container

After building the image, start the container with:

```bash
make docker_run
```

This command runs the API inside a Docker container, mapping the container's port 8080 to port 8080 on your host.

### 6. Deploying to AWS

#### 1. Inititalizing Terraform

```bash
make init_cloud_infra
```

#### 2. Upload container to Registry

```bash
make upload_container_to_registry
```

#### 3. Deploying container

```bash
make apply_cloud_infra
```

#### 4. Destroying resources

```bash
make destroy_cloud_infra
```


### 7. Setup AWS SES

Do not forget to properly configure Amazon's Simple Email Service. This allows the API to send emails programatically, which is necessary for the password reset flow.
