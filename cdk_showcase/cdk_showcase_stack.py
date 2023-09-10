from aws_cdk import (
    Stack,
    App,
    Duration,
    aws_ec2 as ec2,
    aws_s3 as s3,
    Stack,
    aws_iam as iam,
    aws_s3_assets as s3_assets,
    aws_events as events,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_autoscaling_hooktargets as hooktargets,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    # aws_cloudwatch_widgets as cloudwatch_widgets

    # aws_sqs as sqs,
)

import boto3
from constructs import Construct
import aws_cdk as cdk
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationProtocol, HealthCheck

s3bucket_name = "my-bucket-shrirajchohan26"


class CdkShowcaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    # Create a new VPC
        vpc = ec2.Vpc(self, "MyVpc",
            subnet_configuration=[{
                'cidrMask': 24,
                'name': 'Public',
                'subnetType': ec2.SubnetType.PUBLIC
            }], max_azs=2, ip_addresses=ec2.IpAddresses.cidr("10.0.1.0/20"),
            enable_dns_support=True,
            enable_dns_hostnames=True,
                )  

        bucket_arns = [
            "arn:aws:s3:::your-bucket-name",
            "arn:aws:s3:::your-bucket-name/*"
        ]

    # Add an IAM policy to allow the EC2 instance to access the S3 bucket
        policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:*"],
            resources=bucket_arns
        )

    # Create an IAM role
        launch_template_role = iam.Role(self, "MyRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="My EC2 role",
        )

        launch_template_role.add_to_policy(policy) 

    # Create an S3 bucket for static web content
        bucket = s3.Bucket(self, "MyBucket",
            bucket_name=s3bucket_name, # my s3bucketname variable value is hidden for a security reason. 
            website_index_document="index.html",
            removal_policy=cdk.RemovalPolicy.DESTROY)  
        


        

        # Create a policy statement allowing all S3 actions
        # public_access_policy = iam.PolicyStatement(
        #     effect=iam.Effect.ALLOW,
        #     actions=["s3:*"],
        #     principals=[iam.AnyPrincipal()],
        #     resources=[bucket.bucket_arn + "/*"]
        # )

        # bucket_arns = [
        #     "arn:aws:s3:::my-bucket-shrirajchohan26",
        #     "arn:aws:s3:::my-bucket-shrirajchohan26/*"
        # ]
 




        # Attach the policy statement to the bucket's policy
        # bucket.add_to_resource_policy(public_access_policy) 

        original_user_data = ec2.UserData.for_linux()
        original_user_data.add_commands(
                "sudo su",
                "yum update -y",
                "yum install -y httpd",
                # "sudo su",
                "service httpd start",
                "sudo aws s3 sync s3://{0} /var/www/html/".format(bucket.bucket_name),
                "touch test.txt"
                )
        
    #Define Launch template.
        template = ec2.LaunchTemplate(self, "LaunchTemplate",
            instance_type=ec2.InstanceType("t2.micro"),     # Define Instance Size
            launch_template_name="CDK-Show-Case",       # Define Launch template name
            role=launch_template_role,      # Define role for Ec2 instance (Optional)
            key_name="shriraj",         # Key for Ec2 instances is optional too
            user_data=original_user_data,       # Define #user-data for Ec2 instances.
            machine_image=ec2.MachineImage.latest_amazon_linux(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,),      # Define AMI
            security_group=ec2.SecurityGroup(self, "LaunchTemplateSG",      # Define Security Groups for EC2
                vpc=vpc,        # Define VPC for Launch template and Ec2 instances to spin up in. 
                ),
            )

        # This block of SDK code updates the Launch template to the latest verison

        # # Create a Boto3 EC2 client 
        # ec2_client = boto3.client('ec2')

        # # Get the latest version number of the launch template
        # latest_version = ec2_client.describe_launch_template_versions(
        #     LaunchTemplateName='CDK-Show-Case',
        #     Versions=['$Latest']
        # )['LaunchTemplateVersions'][0]['VersionNumber']

        # print(latest_version)

        # # Update the default version of the launch template to the latest version
        # response = ec2_client.modify_launch_template(
        #     LaunchTemplateName='CDK-Show-Case',
        #     DefaultVersion=str(latest_version)
        # ) 
    
    # Create an ALB
        lb = elbv2.ApplicationLoadBalancer(self,"LB",
            vpc=vpc,
            internet_facing=True)


        # Create an ASG
        asg = autoscaling.AutoScalingGroup(
            self,
            "MyAsg",
            auto_scaling_group_name ="My-CDK-Asg",
            vpc=vpc, 
            min_capacity=1,     # Minimum number of instances that always should be on.
            max_capacity=5,     # Maximim number of instances that always should be on.
            desired_capacity=1,     # Desirable number of instances that always should be on.
            launch_template=template,       # Attatch Launch template to the ASG
            cooldown=cdk.Duration.minutes(2),       # Cooldown period for the ASG to Scale in and out
        )

        # ____________

    # # Create an EC2 Auto Scaling client
    #     autoscaling1 = boto3.client('autoscaling')
     

    # # Specify the name of the Auto Scaling group to update
    #     asg_name = 'My-CDK-Asg'

    #     asg_response = autoscaling1.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    #     if asg_response['AutoScalingGroups']:
    #         asg_launch_template_version = asg_response['AutoScalingGroups'][0]['LaunchTemplate']['Version']
    #         print(f"Launch template version: {asg_launch_template_version}")
    #     else:
    #         print(f"No Auto Scaling Group found with name: {asg_name}")

    #     response123 = autoscaling1.update_auto_scaling_group(
    #         AutoScalingGroupName=asg_name,
    #         LaunchTemplate={
    #             # 'LaunchTemplateId': '',
    #             'LaunchTemplateName': 'CDK-Show-Case',
    #             'Version': '$Latest'
    #             # 'Version': asg_launch_template_version
    #                 }
    #         )
    #     print(response123)

        # _____________

        #  # retrieve existing launch template
        # template_id = template.launch_template_id
                                            
                                            

        # # retrieve existing Auto Scaling Group
        # asg = autoscaling.AutoScalingGroup.from_auto_scaling_group_name(self, "ASG", "MyAsg")

        # # update ASG to use a new version of the Launch Template
        # asg.update(
        #     min_capacity=2,
        #     max_capacity=10,
        #     desired_capacity=2,
        #     launch_template=autoscaling.LaunchTemplateConfig(
        #         launch_template_id=template_id,
        #         version="$Latest"
        #     )
        # )


        # # Update ASG to use a new version of the Launch Template
        # asg.update(
        #     launch_template=autoscaling.LaunchTemplateSpecification(
        #         id=template.launch_template_id,
        #         version="$Latest"
        #     )
        # )

    # This policy tells the ASG to automatically scale the number of instances up or down based on the 
    # CPU utilization of the instances in the group. 
    # If the CPU utilization is consistently above 90%, the ASG will launch new instances. 
    # If the CPU utilization is consistently below 90%, the ASG will terminate instances.
        asg.scale_on_cpu_utilization("cpu-util-scaling", 
            target_utilization_percent= 90)
        
        cpu_utilization_metric = cloudwatch.Metric(
            namespace='AWS/EC2',
            metric_name='CPUUtilization',
            period=cdk.Duration.minutes(1),
            statistic='Average'
                )
        
        dashboard = cloudwatch.Dashboard(self, 'MyDashboard')

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
             title='CPU Utilization',
                left=[cpu_utilization_metric],
                width=12,
            )
        )

        asg.scale_on_schedule('ScheduleScalingPolicy',
             schedule=autoscaling.Schedule.cron(hour="8", minute="30"), #Scales up everyday at 08:30 UTC 
             min_capacity=1,
             max_capacity=5  # Maximum instances to allow
        )                  
        
    # Create Target Group
        target_group = elbv2.ApplicationTargetGroup(self, "MyTargetGroup",
            vpc=vpc,        # Define VPC
            port=80,        # Define port
            protocol=elbv2.ApplicationProtocol.HTTP,    # Define Protocol
            health_check=HealthCheck(
            path='/',       # Healthcheck path
            unhealthy_threshold_count=2,
            healthy_threshold_count=5,
            interval=cdk.Duration.seconds(30)
            )
        )

    # Attach the target group to the ASG.
        target_group.add_target(asg)    
        
    # Add a listener and open up the load balancer's security group to the world.
        listener = lb.add_listener("Listener",
            port=80,        # Listener port
            open=True,
            protocol=elbv2.ApplicationProtocol.HTTP,        # Listener protocol
            default_target_groups=[target_group],       # Listener target group
            )

    # #   Add the target groups to the ALB listener, 
    #     listener.add_target_groups("MyTargetGroupRule", target_groups=[target_group])

        asg.scale_on_request_count("requests-per-minute", target_requests_per_minute=100,
            cooldown=cdk.Duration.seconds(60)) 
        
        request_metric = cloudwatch.Metric(
            namespace='AWS/EC2',
            metric_name='Request Count Metric',
            dimensions_map={'AutoScalingGroupName': asg.auto_scaling_group_name},
            # dimensions_map=[{'AutoScalingGroupName': asg.auto_scaling_group_name}],
            period=cdk.Duration.seconds(10),
            statistic='Average'
                )
        

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
             title='Request metric',
                right=[request_metric],
                width=12,
            )
        )



        # sg= ec2.SecurityGroup(self,"MySg",
        #     vpc=vpc,
        #     description="Allow all traffic",
        #     allow_all_outbound=True)

        # # Add ingress rule to allow traffic from the security group
        # sg.add_ingress_rule(
        #     peer=ec2.Peer.ipv4("0.0.0.0/0"),
        #     connection=ec2.Port.tcp(80),
        # )

        # sg.add_ingress_rule(
        #     peer=ec2.Peer.ipv4("0.0.0.0/0"),
        #     connection=ec2.Port.tcp(443),
        # )

        # sg.add_ingress_rule(
        #     peer=ec2.Peer.ipv4("0.0.0.0/0"),
        #     connection=ec2.Port.tcp(22),
        # )



        
        # # Create an EC2 instance
        # instance = ec2.Instance(self, "MyInstance",
        #     instance_type=ec2.InstanceType("t2.micro"),
        #     machine_image=ec2.AmazonLinuxImage(),
        #     vpc=vpc,
        #     vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        #     key_name="shriraj",
        #     security_group=sg,
        #     user_data=original_user_data,
        # )


        

        asg.role.add_to_principal_policy(policy)

