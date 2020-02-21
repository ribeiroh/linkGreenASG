import boto3

cd_client = boto3.client('codedeploy')
asg_client = boto3.client('autoscaling')
elb_client = boto3.client('elbv2')

def fetchTargetGroupArn(targetGroup):
    try:
        response = elb_client.describe_target_groups(
            Names=[targetGroup]
        )     
        targetGroupArn = response["TargetGroups"][0]["TargetGroupArn"]
    except:
        raise
    
    return targetGroupArn

def linkGreenASG(targetASGs,targetGroupArn):
    for autoScalingGroup in targetASGs:
        try:
            print(f"Attempting to link Auto Scaling Group '{autoScalingGroup}' to target group \'{targetGroupArn.split(':')[-1].split('/')[1]}\'...")
            response = asg_client.attach_load_balancer_target_groups(
                AutoScalingGroupName=autoScalingGroup,
                TargetGroupARNs = [targetGroupArn]
            )
        except:
            raise
        else:          
            print("Auto Scaling Group successfully linked.")

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
        raise
    except:
        raise
    
    # Only EC2 Blue/Green deployments have 'targetInstances' defined
    if 'targetInstances' in deployment['deploymentInfo']:
        targetASGs = deployment['deploymentInfo']['targetInstances']['autoScalingGroups']
        targetGroup = deployment['deploymentInfo']['loadBalancerInfo']['targetGroupInfoList'][0]['name']
        linkGreenASG(targetASGs,fetchTargetGroupArn(targetGroup))
    else:
        print("This does not appear to be a valid EC2 Blue/Green deployment. Nothing to do...")