# linkGreenASG

This is a SAM serverless function to automatically link your CodeDeploy Green Auto Scaling Groups to the associated Target Group. Basic instructions:

`$ sam package --template-file template.yaml --s3-bucket <S3 Bucket> --output-template-file packaged.yaml`  
`$ sam deploy --template-file packaged.yaml --stack-name linkGreenASG --capabilities CAPABILITY_IAM`
