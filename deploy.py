import os
import boto3

cloudfront_svc = boto3.client('cloudfront')

def generate_new_distribution_config(
    distribution_config: dict,
    path_pattern: str,
    lambda_association_event_type: str,
    lambda_association_version_arn: str,
) -> dict:
    try:
        print('\n-- Current Cloudfront Distribution : \n')
        print(distribution_config)
        # If Lambda already in CloudfrontDistribution
        # Filter by TargetOriginId on CacheBehaviors collection
        for cache_behavior in distribution_config['CacheBehaviors']['Items']:
            if path_pattern is not cache_behavior['PathPattern']:
                continue

            if 'Items' in cache_behavior['LambdaFunctionAssociations']:
                lambda_function_associations_list = cache_behavior['LambdaFunctionAssociations']['Items']
                for item in lambda_function_associations_list:
                    event_type = item['EventType']
                    if lambda_association_event_type is event_type:
                        item['LambdaFunctionARN'] = lambda_association_version_arn
            else:
                # When lambda are not associated to Cloudfront distribution, we add it
                cache_behavior['LambdaFunctionAssociations']['Items'] = [{
                    'LambdaFunctionARN': lambda_association_version_arn,
                    'EventType': lambda_association_event_type,
                    'IncludeBody': False
                }]
                if 'Quantity' in cache_behavior['LambdaFunctionAssociations']:
                    cache_behavior['LambdaFunctionAssociations']['Quantity'] += 1
                else:
                    cache_behavior['LambdaFunctionAssociations']['Quantity'] = 1

        return distribution_config
    except Exception as error:
        print("Error during update distribution config with new lambda ARN")
        print(error)
        exit(1)


def get_distribution_config(distribution_id: str) -> dict:
    try:
        return cloudfront_svc.get_distribution_config(Id=distribution_id)
    except Exception as error:
        print("Error during get distribution config")
        print(error)
        exit(1)


def get_input_var(var_name, required):
    var_name = f"INPUT_{var_name}"
    if var_name in os.environ:
        return os.environ[var_name]
    else:
        if required is True:
            raise RuntimeError("Required parameter " + var_name + " missing.")
        return None


# Getting the input parameters
distribution_id = get_input_var('DISTRIBUTION_ID', True)
path_pattern = get_input_var('PATH_PATTERN', True)
lambda_association_event_type = get_input_var('LAMBDA_ASSOCIATION_EVENT_TYPE', True)
lambda_association_version_arn = get_input_var('LAMBDA_ASSOCIATION_VERSION_ARN', True)
lambda_association_version_arn = get_input_var('CLOUDFRONT_INVALIDATION_REQUIRED', True)

distribution_config_response = get_distribution_config(distribution_id)
distribution_config = distribution_config_response['DistributionConfig']
distribution_etag = distribution_config_response['ETag']
distribution_config_updated = generate_new_distribution_config(
    distribution_config,
    path_pattern,
    lambda_association_event_type,
    lambda_association_version_arn
)

print('\n-- Cloudfront distribution to update : \n')
print(distribution_config_updated)

try:
    cloudfront_svc.update_distribution(
        DistributionConfig=distribution_config_updated,
        Id=distribution_id,
        IfMatch=distribution_etag
    )
except Exception as error_update:
    print('Error during cloudfront distribution update')
    print(error_update)
    exit(1)

cloudfront_waiter = cloudfront_svc.get_waiter('distribution_deployed')
cloudfront_waiter.wait(Id=distribution_id)

if cloudfront_invalidation_required:
    try:
        print('\n-- Start Cloudfront cache invalidation\n')
        response = client.create_invalidation(DistributionId=distribution_id)
    except Exception as error_invalidate:
        print('Error during cache invalidation')
        print(error_invalidate)