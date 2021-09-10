import os
import boto3

cloudfront_svc = boto3.client('cloudfront')


def generate_new_distribution_config(distribution_config: dict, lambda_updated_arn: dict) -> dict:
    try:
        print('Cloudfront Distribution : ')
        print(distribution_config)
        lambda_function_associations_list = distribution_config['DistributionConfig']['DefaultCacheBehavior']['LambdaFunctionAssociations']['Items']
        lambda_function_associations_list_updated = []
        for item in lambda_function_associations_list:
            event_type = item['EventType']
            if lambda_updated_arn[event_type] is not None:
                item['LambdaFunctionARN'] = lambda_updated_arn[event_type]
            lambda_function_associations_list_updated.append(item)
        distribution_config['DistributionConfig']['DefaultCacheBehavior']['LambdaFunctionAssociations'] = lambda_function_associations_list_updated
        return distribution_config
    except Exception as error:
        print("Error during update distribution config with new lambda ARN")
        print(error)
        exit(1)


def get_distribution_config(distribution_id: str) -> dict:
    try:
        cloudfront_svc.get_distribution_config(Id=distribution_id)
    except Exception as error:
        print("Error during get distribution config")
        print(error)
        exit(1)


def get_env_var(var_name, required):
    var_name = f"INPUT_{var_name}"
    if var_name in os.environ:
        return os.environ[var_name]
    else:
        if required is True:
            raise RuntimeError("Required parameter " + var_name + " missing.")
        return None


# Getting the input parameters
distribution_id = get_env_var('DISTRIBUTION_ID', True)

lambdas_arn = {
    "viewer-request": get_env_var('LAMBDA_VIEWER_REQUEST_VERSION_ARN', False),
    "origin-request": get_env_var('LAMBDA_ORIGIN_REQUEST_VERSION_ARN', False),
    "origin-response": get_env_var('LAMBDA_ORIGIN_RESPONSE_VERSION_ARN', False),
    "viewer-response": get_env_var('LAMBDA_VIEWER_RESPONSE_VERSION_ARN', False)
}


distribution_config = get_distribution_config(distribution_id)
distribution_config_updated = generate_new_distribution_config(distribution_config, lambdas_arn)

try:
    cloudfront_svc.update_distribution(
        DistributionConfig=distribution_config_updated,
        Id=distribution_id,
    )
except Exception as error_update:
    print('Error during cloudfront distribution update')
    print(error_update)
    exit(1)

cloudfront_waiter = cloudfront_svc.get_waiter('Distribution Deployed')
waiter.wait(Id=distribution_id)

try:
    response = client.create_invalidation(DistributionId=distribution_id)
except Exception as error_invalidate:
    print('Error during cache invalidation')
    print(error_invalidate)