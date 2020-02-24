import boto3

cd_client = boto3.client('codedeploy')
asg_client = boto3.client('autoscaling')
elb_client = boto3.client('elbv2')

def fetchTargetGroupArn(targetGroup):
    # we only have a target group name, but the linking requires full arn
    try:
        response = elb_client.describe_target_groups(
            Names=[targetGroup]
        )     
        targetGroupArn = response["TargetGroups"][0]["TargetGroupArn"]
    except:
        raise
    
    return targetGroupArn

def linkGreenASG(deploymentTargetASGs,targetGroupArn):
    try:
        targetASGs = asg_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=deploymentTargetASGs
        )
        if targetASGs["AutoScalingGroups"]:
            for autoScalingGroup in targetASGs["AutoScalingGroups"]:
                if autoScalingGroup["HealthCheckType"] == "ELB":
                        print(f"Attempting to link Auto Scaling Group \'{autoScalingGroup['AutoScalingGroupName']}\' to target group \'{targetGroupArn.split(':')[-1].split('/')[1]}\'...")
                        response = asg_client.attach_load_balancer_target_groups(
                            AutoScalingGroupName=autoScalingGroup["AutoScalingGroupName"],
                            TargetGroupARNs = [targetGroupArn]
                        )
                        if response["ResponseMetadata"]["HTTPStatusCode"] == 200: print("The Auto Scaling Group has been linked successfully.")
                else:
                    print(f"Auto Scaling Group \'{autoScalingGroup['AutoScalingGroupName']}\' does not use ELB Health Check Type. Skipping attempt to link to Target Group")
        else:
            print(f"The Auto Scaling Group(s) {', ' .join(deploymentTargetASGs)} no longer exist. Nothing to do.")
    except:
        raise

def lambda_handler(event, context):
    application =  event['detail']['application']
    deploymentGroup = event['detail']['deploymentGroup']
    deploymentId = event['detail']['deploymentId']
    
    print(f"Processing successful deployment {deploymentId} (Application = {application} | Deployment Group = {deploymentGroup})")
    
    # Load deployment object
    try:
        deployment = cd_client.get_deployment(deploymentId=deploymentId)
    except cd_client.exceptions.DeploymentDoesNotExistException as err:
        print(f"Deployment ID {deploymentId} does not exist. Exiting...")
        return None
    except:
        raise
    
    # Only EC2 Blue/Green deployments have 'targetInstances' defined
    if 'targetInstances' in deployment['deploymentInfo']:
        deploymentTargetASGs = deployment['deploymentInfo']['targetInstances']['autoScalingGroups']
        targetGroup = deployment['deploymentInfo']['loadBalancerInfo']['targetGroupInfoList'][0]['name']
        linkGreenASG(deploymentTargetASGs,fetchTargetGroupArn(targetGroup))
    else:
        print("This does not appear to be a valid EC2 Blue/Green deployment. Nothing to do...")