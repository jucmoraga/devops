# =====================
# VARIABLES GENERALES
# =====================
AWS_REGION=us-east-1
ACCOUNT_ID=387050840675

# Credenciales fijas para la base de datos
DB_USER=proyectogrupo10
DB_PASSWORD=proyectogrupo10

# Microservicios
SERVICES=blacklist-app
FOLDERS=blacklist_app
IMAGE_TAG=latest

export AWS_REGION

# =====================
# STACKS INDIVIDUALES
# =====================
rds:
	cd terraform/stacks/rds && \
	terraform init -backend-config="../../environments/rds/backend.tfvars" && \
	terraform plan -var-file="../../environments/rds/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

ecr:
	cd terraform/stacks/ecr && \
	terraform init -backend-config="../../environments/ecr/backend.tfvars" && \
	terraform plan -var-file="../../environments/ecr/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

service:
	aws ecs create-service \
	--cluster athletic-penguin-uurvpz \
	--service-name servicio-bluegreen \
	--task-definition task-devops:17 \
	--desired-count 1 \
	--launch-type FARGATE \
	--deployment-controller type=CODE_DEPLOY \
	--load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:387050840675:targetgroup/target-group-1/b2e082f61677247e,containerName=blacklist,containerPort=5000" \
	--network-configuration "awsvpcConfiguration={subnets=[subnet-0491d15ed08b8838e,subnet-063ff44fd4989f3dd,subnet-09730e73a9d526aa0,subnet-04a9dff01e9f186f2,subnet-0df0997bf3161dbe0,subnet-0268dad6b6b38340d],securityGroups=[sg-081c581032f1b7b4a,sg-093cef7a5c0694b36],assignPublicIp=ENABLED}"

# =====================
# DESTROY
# =====================

destroy-rds:
	cd terraform/stacks/rds && \
	terraform destroy -var-file="../../environments/rds/terraform.tfvars"

destroy-ecr:
	cd terraform/stacks/ecr && \
	terraform destroy -var-file="../../environments/ecr/terraform.tfvars"

# =====================
# DOCKER + ECR
# =====================

ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

docker-push-all:
	@i=0; \
	for service in $(SERVICES); do \
		folder=$$(echo $(FOLDERS) | cut -d' ' -f$$((i+1))); \
		echo ">>> Construyendo y subiendo $$service desde $$folder"; \
		docker build --rm -t $$service:$(IMAGE_TAG) -f $$folder/Dockerfile $$folder/.; \
		docker tag $$service:$(IMAGE_TAG) $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG); \
		docker push $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG); \
		i=$$((i+1)); \
	done

# =====================
# WORKFLOWS COMPLETOS
# =====================

infra: rds ecr
images: ecr-login docker-push-all
deploy: infra images
destroy: destroy-rds destroy-ecr
