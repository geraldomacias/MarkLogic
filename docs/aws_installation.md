To Set up your AWS Account

1. Create your AWS account. This needs to be a real AWS account and not a student version
2. Navigate to the Console and go to IAM
3. Create a role for EC2 and give it Full Access to EC2, IAM, and S3. Name it as you please
4. Navigate to the Console and go to EC2 so we can spin up an instance for your public facing classifier
5. Create a t2.micro instance with standard or custom settings and use the IAM Role you built as the IAM Role for the instance
6. Navigate to S3, create two buckets, one for classified and one for originals, name them as you please
7. Change the names on the docker compose file to reflect the names of your buckets
8. Naviate back over to IAM and create a role for your personal use on your machine. Make sure your permissions allow full access to S3. Keep track of your public and private keys for later

To Set up AWS Credentials for local development

1. On your LOCAL machine, create a hidden directory at HOME ~/ called ".aws"
2. Create a file named "credentails" and follow this format:

[default] aws_access_key_id = AKIA#################### aws_secret_access_key = #######################################

3. Create a file named "config" and follow this format based on the region you made your credentials in

[default] region=us-east-1

4. The rest should be taken care of and you can now use the backend on your localhost