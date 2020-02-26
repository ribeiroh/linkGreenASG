# linkGreenASG

CodeDeploy Blue/Green deployments can create an Auto Scaling Group on your behalf, but will not link them to your Target Group. This is a potential issue if you [rely on ELB Health Checks in your ASG](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-add-elb-healthcheck.html). This [SAM](https://aws.amazon.com/serverless/sam/) serverless function will automatically link your CodeDeploy Green Auto Scaling Groups to the Target Group defined in your Deployment Group.

Setup instructions:

1. Clone the repository

2. Package the SAM template and upload it to S3:  
   `$ aws cloudformation package --template-file template.yaml --s3-bucket <S3 Bucket> --output-template-file packaged.yaml`
   
   Note: replace `<S3 Bucket>` with a bucket in the same region of where the stack will be created.

4. Deploy the function with CloudFormation:  
   `$ aws cloudformation deploy --template-file packaged.yaml --stack-name linkGreenASG --capabilities CAPABILITY_IAM`

This function will attempt to link ASGs for all Blue/Green deployments happening on the account/region where the function is deployed, so not further configuration is needed.

> Note: this function will only link ASGs that have a Health Check Type set to `ELB`
